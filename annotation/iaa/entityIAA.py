"""
Use the bratiaa package to get IAA for text-bound annotations.

bratiaa asumes the following directory structure:

    example-project/
    ├── annotation.conf
    ├── annotator-1
    │   ├── doc-1.ann
    │   ├── doc-1.txt
    │   ├── doc-3.ann
    │   ├── doc-3.txt
    │   └── second
    │       ├── doc-2.ann
    │       └── doc-2.txt
    └── annotator-2
        ├── doc-3.ann
        ├── doc-3.txt
        ├── doc-4.ann
        ├── doc-4.txt
        └── second
            ├── doc-2.ann
            └── doc-2.txt

In the specific structure that I have been using to coordinate annotators, the 
brat annotation.conf file must be moved to /mnt/research/ShiuLab/serena_kg/annotators_done/
in order for this script to work.

The bratiaa package doesn't provide a direct way to write the report to a file, 
so this script should be run on the command line as 

    python entityIAA.py <project_dir> > <my_file>

in order to save the results to a file instead of printing.


Author: Serena G. Lotreck
"""
import os 
import argparse

import bratiaa as biaa
import spacy 


def tokenizer(text):
    """
    Tokenizer funciton to use for token-level IAA.
    
    Yields a generator with the start and end character offsets for the 
    tokens in the doc.
    """
    nlp = spacy.load("en_core_sci_sm")
    doc = nlp(text)

    # Make each token into a Span object
    spans = []
    for i, token in enumerate(doc):
        spans.append(doc[i:i+1])

    doc.spans['token_spans'] = spans

    # Get character offsets from Span objects
    for span in doc.spans['token_spans']:
        yield span.start_char, span.end_char


def main(project_dir):

    # Instance-level agreement 
    instance_f1 = biaa.compute_f1_agreement(project_dir)
    biaa.iaa_report(instance_f1)

    # Token-level agreement 
    token_f1 = biaa.compute_f1_agreement(project_dir, token_func=tokenizer)
    biaa.iaa_report(token_f1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Calculate IAA')

    parser.add_argument('project_dir', type=str,
            help='Path to brat annotated files of multiple annotators, with '
                'the directory structure required by bratiaa')
    
    args = parser.parse_args()

    args.project_dir = os.path.abspath(args.project_dir)

    main(args.project_dir)
