"""
Script to run PURE models. PURE repository and corresponding
models must be downloaded with download_pure.sh before using.

Need to be in a computing environment with access to GPU in
order to run PURE models. NOTE TO SELF: Currently using a pure
environment + dygie developed + jsonlines + pandas to run this.

Takes DyGIE++ formatted data and removes the dataset field and
blanks out annotation fields or adds empty ones. Renames the
file to dev.json, which is required by PURE.

NOTE: PURE doesn't offer an option to direct where the output is
saved, and instead requires the model directory to be specified
as the output directory, and saves results there. Additionally,
there is no option to change the name of the output files, so the
outputs will be overwritten every time the model is run. For this
reason, PURE output files are copied with the out_prefix to the
out_loc directory with the number of the run, so that all results
are accessible, and the evaluation is performed from there.

Output directory structured as:

    out_loc
    |
    ├── formatted_data
    |
    ├── model_predictions
    |
    ├── stdout_stderr
    |
    └── performance

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath, exists, basename, splitext, split
from os import makedirs, walk, listdir
import subprocess
from collections import OrderedDict
from random import randint
from tqdm import trange
import jsonlines


class PrefixError(Exception):
    pass


class ModelNotFoundError(Exception):
    pass


def evaluate_models(top_dir, data_path, out_prefix):
    """
    Runs the model evaluation script on model output.

    parameters:
        top_dir, str: path to top level output dir
        data_path, str: path to data, must include gold standard
            annotations
        out_prefix, str: only evaluates files with this prefix

    returns: None
    """
    save_name = (f'{top_dir}/performance/{out_prefix}'
            '_model_performance.csv')
    evaluate = [
        "python",
        abspath("../evaluate_model_output.py"), data_path, save_name,
        f'{top_dir}/model_predictions/', '-use_prefix', out_prefix,
        '--bootstrap'
    ]
    subprocess.run(evaluate)


def run_models(model_paths, new_data_path, pure_path, top_dir,
                            out_prefix):
    """
    Runs models. Unzips model files and
    doesn't delete unzipped directories.

    parameters:
        model_paths, dict: keys are (model name, ent/rel), values are
            paths to zip files of models
        new_data_path, str: path to properly formatted dev.json
        pure_path, str: path to PURE directory
        top_dir, str: path to top directory for output file structure

    returns: None
    """
    prev_model_path = ''
    for model_name_tup, model_path in model_paths.items():

        verboseprint(f'On model {model_name_tup[0]} for {model_name_tup[1]}s.')

        # Unzip model
        unzip_path = split(model_path)[0]
        unzip = f'unzip {model_path} -d {unzip_path}'
        subprocess.run(unzip, shell=True)
        unzipped_model_path = model_path[:-4]


        # Get model task name
        if model_name_tup[0] == 'albert-xxlarge-v1':
            task = 'ace05'
        else: task = 'scierc'

        # Run model
        if model_name_tup[1] == 'ent':
            model_run = (f'python {pure_path}/run_entity.py --do_eval '
                        f'--context_window 0 --task {task} --data_dir '
                        f'{top_dir}/formatted_data --model {model_name_tup[0]} '
                        f'--output_dir {unzipped_model_path}')

        else:
            model_run = (f'python {pure_path}/run_relation.py --do_eval '
                        f'--context_window 0 --entity_output_dir '
                        f'{prev_model_path} --model {model_name_tup[0]} '
                        f'--output_dir {unzipped_model_path} --task {task}')

        out = subprocess.run(model_run, capture_output=True, shell=True)

        # Convert bytes to string so they can be written to a file
        stdout_s = out.stdout.decode("utf-8")
        stderr_s = out.stderr.decode("utf-8")

        # Save stdout
        stdout_loc = (f'{top_dir}/stdout_stderr/'
                      f'{out_prefix}_model_runs_stdout_stderr.txt')
        with open(stdout_loc, 'a') as myf:
            myf.write('====> STDOUT <====\n\n')
            myf.write(stdout_s)
            myf.write('\n\n====> STDERR <====\n\n')
            myf.write(stderr_s)

        # Copy model output with out_prefix to output directory
        if model_name_tup[1] == 'ent':
            old_name = f'{unzipped_model_path}/ent_pred_dev.json'
        else:
            old_name = f'{unzipped_model_path}/predictions.json'
        new_name = (f'{top_dir}/model_predictions'
                    f'/{out_prefix}_pure_{task}_{model_name_tup[1]}_output.jsonl')
        copy = f'cp {old_name} {new_name}'
        subprocess.run(copy, shell=True)

        prev_model_path = unzipped_model_path


def format_data(data_path, top_dir):
    """
    Make a new copy of the data on which to run the models, removing
    or adding an empty set of annotation fields, and removing the
    dataset name. Saves new copy as dev.json in top_dir.

    parameters:
        data_path, str: path to data file
        top_dir, str: path to top directory for output file structure

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

    new_data_path = f'{top_dir}/formatted_data/dev.json'
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
    model_paths_dict = OrderedDict()
    for model_dir in ['ace05', 'scierc']:
        if model_dir == 'ace05':
            model_paths = [f'{to_check}/{model_dir}/ent-alb-ctx100.zip',
                           f'{to_check}/{model_dir}/rel-alb-ctx100.zip']
            model_name_tups = [('albert-xxlarge-v1', 'ent'),
                               ('albert-xxlarge-v1', 'rel')]
        else:
            model_paths = [f'{to_check}/{model_dir}/ent-scib-ctx300.zip',
                           f'{to_check}/{model_dir}/rel-scib-ctx100.zip']
            model_name_tups = [('allenai/scibert_scivocab_uncased', 'ent'),
                               ('allenai/scibert_scivocab_uncased', 'rel')]

        for model_name_tup, model_path in zip(model_name_tups, model_paths):
            if basename(model_path) not in listdir(f'{to_check}/{model_dir}'):
                raise ModelNotFoundError(
                    'One or mode requested models has not '
                    'been downloaded. Please download '
                    'models and try again.')
            else:
                model_paths_dict[model_name_tup] = model_path

    return model_paths_dict


def check_prefix(top_dir, out_prefix):
    """
    Checks if any files in the tree exist with the same file prefix, in order
    to prevent files from being overwritten. Raises an exception if any files
    are found with that prefix.

    parameters:
        top_dir, str: path to top directory for output file structure
        out_prefix, str: string to be prepended to all output files

    returns: None
    """
    for path, currentdir, files in walk(top_dir):
        for f in files:
            if f.startswith(out_prefix):
                raise PrefixError(
                    f'Files with prefix {out_prefix} already '
                    'exist in this file tree, please try again with a new prefix.'
                )


def check_make_filetree(top_dir):
    """
    Checks if the top_dir exists already, as well as the correct
    subdirectories. Creates any missing directories.

    parameters:
        top_dir, str: path to top directory for output file structure

    returns: True if top_dir exists, False otherwise
    """
    # Check if top_dir exists
    if exists(top_dir):

        # If it does, check for correct subdirectories
        formatted_data_path = f'{top_dir}/formatted_data'
        if not exists(formatted_data_path):
            makedirs(formatted_data_path)

        model_predictions_path = f'{top_dir}/model_predictions'
        if not exists(model_predictions_path):
            makedirs(model_predictions_path)

        allennlp_output_path = f'{top_dir}/stdout_stderr'
        if not exists(allennlp_output_path):
            makedirs(allennlp_output_path)

        performance_path = f'{top_dir}/performance'
        if not exists(performance_path):
            makedirs(performance_path)

        return True

    else:

        makedirs(top_dir)
        makedirs(f'{top_dir}/formatted_data')
        makedirs(f'{top_dir}/model_predictions')
        makedirs(f'{top_dir}/stdout_stderr')
        makedirs(f'{top_dir}/performance')

        return False


def main(data_path, pure_path, top_dir, out_prefix, model_path):

    # Check if the top_dir & other folders exist already
    verboseprint('\nChecking if file tree exists and creating it if not...')
    existed = check_make_filetree(top_dir)

    # Make sure no files with the same prefix exist
    verboseprint('\nMaking sure no files with the given prefix exist...')
    if existed:
        check_prefix(top_dir, out_prefix)

    # Check that the models exist, raise excpetion if not
    verboseprint('\nMaking sure all models are downloaded...')
    if model_path == '':
        to_check = f'{pure_path}/pretrained_models'
    else:
        to_check = model_path
    model_paths = check_models(to_check)

    # Format data
    verboseprint('\nFormatting data...')
    new_data_path = format_data(data_path, top_dir)

    # Run models
    verboseprint('\nRunning models...')
    run_models(model_paths, new_data_path, pure_path, top_dir,
                            out_prefix)

    # Evaluate models
    verboseprint('\nEvaluating models...')
    evaluate_models(top_dir, data_path, out_prefix)

    verboseprint('\n\nDone!\n\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run PURE models')

    parser.add_argument('data_path', type=str,
                        help='Path to dygiepp-formatted data on which '
                        'to run model. Must include annotations to get '
                       'model performance.')
    parser.add_argument('pure_path', type=str,
                        help='Path to the PURE repository.')
    parser.add_argument('top_dir', type=str,
                        help='Path to save the output of this script. A new filetree will '
        'be created here that includes sister dirs "formatted_data", '
        '"model_predictions", and "performance". The directory specified '
        'here can already exist, but will be created if it does not.')
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
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Whether or not to print updates as the script runs.')

    args = parser.parse_args()

    args.data_path = abspath(args.data_path)
    args.pure_path = abspath(args.pure_path)
    args.top_dir = abspath(args.top_dir)
    if args.model_path != '':
        args.model_path = abspath(args.model_path)

    verboseprint = print if args.verbose else lambda *a, **k: None

    main(args.data_path, args.pure_path, args.top_dir, args.out_prefix,
         args.model_path)
