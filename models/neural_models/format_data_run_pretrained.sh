#!/bin/bash

# A script to format data and run all DyGIE++ pre-trained models on a given dataset
# Run with the command:

# format_data_run_pretrained.sh <path to dataset> <path to top-level output directory> \
#       <output identifier> <models to run> <format data?>

# The path to dataset should be a path to a directory if format data is true,
# and a "" list of file paths if format data is false, to the pre-formatted
# datasets to be used with the models. Datasets should be listed in the same 
# order as the models are.

# The models to run argument should be a string with the names of the models 
# to run, separated by spaces; e.g. "genia genia-light"
# Options are:
# scierc scierc-light genia genia-light ace05 mechanic-granular mechanic-coarse

# Output identifier is a string that will be prepended to the name of the output 
# files, and should reflect what dataset the models are being run on 

# The format data argument is a string (true/false),  that tells the script 
# whether or not to format the data before running the models. If this is set 
# to false, the script will assume the properly formatted datafiles are in 
# the same location this script would have put them. The string must be lowercase.

# Assumes that all necessary output directories are where they should be and 
# have the following structure:

# dygiepp/
#    |
#    ├── prepped_data/
#    |
#    └── pretrained_output/
#               |
#               ├── lightweight/
#               |       |
#               |       ├── ace05/
#               |       |
#               |       ├── genia/
#               |       |
#               |       ├── scierc/
#               |       |
#               |`      ├── mechanic-fine/
#               |       |
#               |       └── mechanic-coarse/
#               |
#               └── withCoref/
#                       |
#                       ├── scierc/ 
#                       |
#                       └── genia/

# Where dygiepp/ is the top-level output directory.

# Also assumes that this is being run after switching to the 
# dygiepp/ repo top level, in my case, ~/Shiu_lab/dygiepp/

# Activate conda environment 
eval "$('/mnt/home/lotrecks/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
conda activate dygiepp

# Declare an array to match the models to their dataset names 
declare -A dataset_arr
dataset_arr[genia]=genia
dataset_arr[genia-light]=genia
dataset_arr[scierc]=scierc
dataset_arr[scierc-light]=scierc
dataset_arr[ace05]=ace05
dataset_arr[mechanic-coarse]=None
dataset_arr[mechanic-granular]=covid-event 

# Define variables for the command line args 
data_path=`realpath $1`
output_top_path=`realpath $2`
output_id=$3
models_to_run=$4
format_data=$5 

# Make the blank file for the dataset(s) and write into it
if [[ $format_data = true ]] 
then

    for model in $models_to_run; do
        
        echo "Formatting data for model $model"

        # Get dataset name
        dataset_name=${dataset_arr[${model}]}
        echo $data_path 
	# Make blank file to write the prepped data
        touch ${output_top_path}/prepped_data/${output_id}_dygiepp_formatted_data_${dataset_name}.jsonl;

        # Format the data
        echo "python scripts/new-dataset/format_new_dataset.py $data_path ${output_top_path}/prepped_data/${output_id}_dygiepp_formatted_data_${dataset_name}.jsonl $dataset_name --use-scispacy;"

    done

else
    datasets=($data_path)
    models_array=($models_to_run)\
    i=0
    declare -A formatted_data
    for dataset in $datasets; do 
        formatted_data[${models_array[i]}]=$dataset
        i=$((i+1))
    done
fi

# Run the model
for model in $models_to_run; do

    echo "Running model ${model}"

    # Get dataset name
    dataset_name=${dataset_arr[${model}]}

    # Get the output path for the results 
    case $model in

        scierc | genia)

            output_dir=${output_top_path}/pretrained_output/withCoref/$model
            model_file=${model}.tar.gz 
            ;;

        scierc-light | genia-light | ace05 | mechanic-granular | mechanic-coarse)

            output_dir=${output_top_path}/pretrained_output/lightweight/$model
            
            if [[ "$model" == *"light"* ]] 
            then
                model_file=${model}weight.tar.gz
            elif [[ "$model" == "ace05" ]]
            then 
                model_file=${model}-relation.tar.gz
            else 
                model_file=${model}.tar.gz
            fi
            ;;
    esac

    # Check if the output path exists; if not, create the directory 
    if ! [ -d $output_dir ]; then

        mkdir $output_dir;

    fi 

    # Get the formatted data path 
    if [[ $format_data = true ]] 
    then 
        jsonl=${output_top_path}/prepped_data/${output_id}_dygiepp_formatted_data_${dataset_name}.jsonl
    else 
        jsonl=${formatted_data[$model]}
        echo "jsonl file is"
        echo $jsonl
    fi
    
    # Run the model 
    allennlp predict \
        pretrained/$model_file $jsonl\
        --predictor dygie \
        --include-package dygie \
        --use-dataset-reader \
        --output-file ${output_dir}/${output_id}_${model}_predictions.jsonl \
        --cuda-device 0 \
        --overrides "{'dataset_reader' +: {'lazy': true}}" \
        --silent

done

