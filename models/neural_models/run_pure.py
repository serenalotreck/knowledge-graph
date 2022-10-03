"""
Script to run PURE models. PURE repository and corresponding
models must be downloaded with download_pure.sh before using.

Takes DyGIE++ formatted data and removes the dataset field and
blanks out annotation fields or adds empty ones. Renames the
file to dev.json, which is required by PURE.
    
NOTE: PURE doesn't offer an option to direct where the output is
saved, and instead requires the model directory to be specified
as the output directory, and saves results there. Additionally,
there is no option to change the name of the output files, so the
outputs will be overwritten every time the model is run. For this
script, since the evaluation is external, the models can be run
multiple times without losing their evaluation scores, as these are
generated and saved separately in out_loc.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, exists, basename, splitext
from os import makedirs, walk, listdir
import subprocess
from random import randint
from tqdm import trange
import jsonlines


class PrefixError(Exception):
    pass


class ModelNotFoundError(Exception):
    pass


def run_and_evaluate_models(model_paths, new_data_path,
                            data_path, pure_path, out_loc,
                            out_prefix, num_runs):
    """
    Runs and evaluates models. Evaluates between each run in order to
    circumvent the outputs being overwritten. Unzips model files and
    doesn't delete unzipped directories.
    
    parameters:
        model_paths, dict: keys are (model name, ent/rel), values are
            paths to zip files of models
        new_data_path, str: path to properly formatted dev.json
        data_path, str: path to original dataset, for evaluation
        pure_path, str: path to PURE directory
        out_loc, str: path to save evaluation outputs
        num_runs, int: number of times to run the models
    
    returns: None
    """
    for model_name_tup, model_path in model_paths.items():

        verboseprint(f'On model {model_name_tup[0]} for {model_name_tup[1]}s.')
        
        # Unzip model
        print(model_path)
        unzip = f'unzip {model_path}'
        subprocess.run(unzip, shell=True)
        unzipped_model_path = model_path[:-4]
        
        # Run and evaluate sequentially
        for i in range(num_runs):
            
            # Get model task name
            if model_name_tup[0] == 'albert-xxlarge-v1':
                task = 'ace05'
            else: task = 'scierc'
                
            # Run model
            model_run = (f'python {pure_path}/run_entity.py --do_eval '
                        f'--context_window 0 --task {task} --data_dir '
                        f'{out_loc} --model {model_name_tup[0]} '
                        f'--output_dir {unzipped_model_path}')
            out = subprocess.run(model_run, capture_output=True, shell=True)

            # Convert bytes to string so they can be written to a file
            stdout_s = out.stdout.decode("utf-8")
            stderr_s = out.stderr.decode("utf-8")

            # Save stdout
            stdout_loc = f'{out_loc}/{out_prefix}_model_runs_stdout_stderr.txt'
            with open(stdout_loc, 'w') as myf:
                myf.write('====> STDOUT <====\n\n')
                myf.write(stdout_s)
                myf.write('\n\n====> STDERR <====\n\n')
                myf.write(stderr_s)

            # Evaluate
            save_name = f'{out_loc}/{out_prefix}_run_{i}_model_performance.csv'
            evaluate = [
                "python",
                abspath("../evaluate_model_output.py"), data_path, save_name,
                unzipped_model_path, '-use_prefix', out_prefix
            ]
            subprocess.run(evaluate)
            

def format_data(data_path, out_loc):
    """
    Make a new copy of the data on which to run the models, removing
    or adding an empty set of annotation fields, and removing the
    dataset name. Saves new copy as dev.json in out_loc.
    
    parameters:
        data_path, str: path to data file
        out_loc, str: place to save modified file copy
        
    returns:
        new_data_path, str: path to newly saved copy
    """
    mod_data = []
    with jsonlines.open(data_path) as reader:
        for obj in reader:
            # Drop dataset key
            del obj['dataset']
            # Replace ner and relation values with empty lists
            empty = [[] for i in range(len(obj['sentences']))]
            obj['ner'] = empty
            obj['relations'] = empty
            # Add to list for new doc
            mod_data.append(obj)
            
    new_data_path = f'{out_loc}/dev.json'
    with jsonlines.open(new_data_path, 'w') as writer:
        writer.write_all(mod_data)

    return new_data_path


def check_models(to_check):
    """
    Checks that all required models are downloaded. Raises an
    exception if one or more models are not found.

    parameters:
        to_check, str: path where models should be found

    returns:
        model_paths_dict, dict: keys are (model_name, rel/ent),
            values are paths to model zip files
    """
    model_paths_dict = {}
    for model_dir in ['ace05', 'scierc']:
        if model_dir == 'ace05':
            model_paths = [f'{to_check}/{model_dir}/ent-alb-ctx100.zip',
                           f'{to_check}/{model_dir}/rel-alb-ctx100.zip']
            model_name_tups = [('albert-xxlarge-v1', 'ent'), ('albert-xxlarge-v1', 'rel')]
        else:
            model_paths = [f'{to_check}/{model_dir}/ent-scib-ctx300.zip',
                           f'{to_check}/{model_dir}/rel-scib-ctx100.zip']
            model_name_tups = [('allenai/scibert_scivocab_uncased', 'ent'),
                               ('allenai/scibert_scivocab_uncased', 'rel')]
            
        for model_name_tup, model_path in zip(model_name_tups, model_paths):
            if basename(model_path) not in listdir(f'{to_check}/{model_dir}'):
                print(model_path)
                print(listdir(f'{to_check}/{model_dir}'))
                raise ModelNotFoundError(
                    'One or mode requested models has not '
                    'been downloaded. Please download '
                    'models and try again.')
            else:
                model_paths_dict[model_name_tup] = model_path
    
    return model_paths_dict
            
            
def check_prefix(out_loc, out_prefix):
    """
    Checks if any files in the tree exist with the same file prefix, in order
    to prevent files from being overwritten. Raises an exception if any files
    are found with that prefix.

    parameters:
        out_loc, str: path to save output files
        out_prefix, str: string to be prepended to all output files

    returns: None
    """
    for path, currentdir, files in walk(out_loc):
        for f in files:
            if f.startswith(out_prefix):
                raise PrefixError(
                    f'Files with prefix {out_prefix} already '
                    'exist in this file tree, please try again with a new prefix.'
                )

                
def main(data_path, pure_path, out_loc, out_prefix, model_path, num_runs):
    
    # Make sure no files with the same prefix exist
    verboseprint('\nMaking sure no files with the given prefix exist...')
    check_prefix(out_loc, out_prefix)
        
    # Check that the models exist, raise excpetion if not
    verboseprint('\nMaking sure all models are downloaded...')
    if model_path == '':
        to_check = f'{pure_path}/pretrained_models'
    else:
        to_check = model_path
    model_paths = check_models(to_check)
    
    # Format data
    verboseprint('\nFormatting data...')
    new_data_path = format_data(data_path, out_loc)
    
    # Run models
    verboseprint('\nRunning and evaluating models...')
    run_and_evaluate_models(model_paths, new_data_path,
                            data_path, pure_path, out_loc,
                            out_prefix, num_runs)
    
    verboseprint('\n\nDone!\n\n')

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run PURE models')
    
    parser.add_argument('data_path', type=str,
                        help='Path to dygiepp-formatted data on which '
                        'to run model. Must include annotations to get '
                       'model performance.')
    parser.add_argument('pure_path', type=str,
                        help='Path to the PURE repository.')
    parser.add_argument('out_loc', type=str,
                        help='Path to save output files.')
    parser.add_argument(
        'out_prefix',
        type=str,
        help='Prefix to prepend to all output files from this script. '
        'This differentiates files that might be placed into the same '
        'filetree on different runs of this script on different data.')
    parser.add_argument('-model_path', type=str,
                        help='Path to model directory if they are '
                        'located somewhere else besides the pretrained_models '
                        'subdirectory of the PURE repository.',
                       default='')
    parser.add_argument('-num_runs', type=int,
                        help='Number of times to run and evaluate models. '
                        'Default is 1.',
                        default=1)
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Whether or not to print updates as the script runs.')
    
    args = parser.parse_args()
    
    args.data_path = abspath(args.data_path)
    args.pure_path = abspath(args.pure_path)
    args.out_loc = abspath(args.out_loc)
    if args.model_path != '':
        args.model_path = abspath(args.model_path)
        
    verboseprint = print if args.verbose else lambda *a, **k: None
    
    main(args.data_path, args.pure_path, args.out_loc, args.out_prefix,
         args.model_path, args.num_runs)