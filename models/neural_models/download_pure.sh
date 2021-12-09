#!/bin/bash

# Script to download the highest performing PURE models

# Run with the command:
# download_pure.sh <path to save the models>

# Models will be saved in the output directory with the following directory
# structure:

# <output dir>/
#    |
#    ├── ace05/
#    |
#    └── scierc/

# Activate conda environment
eval "$('/mnt/home/lotrecks/anaconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
conda activate pure

# Define variables for command line args
outpath=`realpath $1`

# Make new directories
cd $outpath
mkdir ace05
mkdir scierc

# Download files
# Certificate issue on HPCC - not a problem on local, --no-check-certificate added to download on HPCC
wget https://nlp.cs.princeton.edu/projects/pure/ace05_models/ent-alb-ctx100.zip -P ace05/ --no-check-certificate
wget https://nlp.cs.princeton.edu/projects/pure/ace05_models/rel-alb-ctx100.zip -P ace05/ --no-check-certificate
wget https://nlp.cs.princeton.edu/projects/pure/scierc_models/ent-scib-ctx300.zip -P scierc/ --no-check-certificate
wget https://nlp.cs.princeton.edu/projects/pure/scierc_models/rel-scib-ctx100.zip -P scierc/ --no-check-certificate
