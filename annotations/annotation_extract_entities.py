"""
Extracts entities surrounded by <entsl></entsl> type tags.

Tags must be of the form <X></X>.

Authors: Shinhan Shiu & Serena G. Lotreck
"""
import argparse
import os

import pandas as pd

def strip_outer(tagged_ents):
    """
    Helper for extract_entities.
    """
    astr4 = tagged_ents[tagged_ents.find(">")+1:tagged_ents.rfind("<")]

    return astr4


def strip_tags(tagged_ents, alist, lead_tag, end_tag):
    """
    Helper for extract_entities.

    Strips tags and returns list of entities without tags.
    """
    astr3 = []
    tagged_ents = tagged_ents.split(lead_tag)
    for i in tagged_ents:
        i = i.split(end_tag)
        astr3.extend(i)
    alist.append("".join(astr3))

    return alist


def find_entities(astr, end_tag):
    """
    Helper for extract_entities.

    Finds tagged entities and returns a list of tagged entities.
    """
    entL = [] # entity list
    cBgn = 0  # begin tag count
    iBgn = 0  # begin tag index
    cEnd = 0  # end tag count
    iEnd = 0  # end tag index
    for i in range(len(astr)):
        if astr[i] == "<":
            if astr[i+1] == "/":
                cEnd += 1
                if cEnd == cBgn:
                    iEnd = i + len(end_tag)
                    ent = astr[iBgn:iEnd]
                    entL.append(ent)
                    cBgn = cEnd = iBgn = iEnd = 0
            else:
                if cBgn == 0:
                    iBgn = i
                cBgn += 1
    return entL


def extract_entities(astr, alist, lead_tag, end_tag):
    """
    Recursive function that extracts entities and strips tags.

    parameters:
        astr, str: text string to extract
        alist, list: list to populate, empty on first iteration
        lead_tag, str: lead tag for entities
        end_tag, str: end tag for entities
    """
    tagged_ents = find_entities(astr, end_tag)
    if len(tagged_ents) == 1:
        alist = strip_tags(tagged_ents[0], alist, lead_tag, end_tag)
        astr_stripped_outer = strip_outer(tagged_ents[0])
        alist = extract_entities(astr_stripped_outer, alist, lead_tag, end_tag)
    else:
        for i in tagged_ents:
            alist = extract_entities(i, alist, lead_tag, end_tag)

    return alist


def cleanup(file):
    """
    Makes all words lowercase, strips empty lines and new line characters.

    parameters:
        file, str: file path to the file to clean

    returns: a string with lines joined with one space
    """
    cleaned = []
    filein  = open(file).readlines()
    for i in filein:
        i = i.lower().strip()
        if i != "":
            cleaned.append(i)

    return " ".join(cleaned)


def main(annotated_text, save_name, lead_tag, end_tag):
    """
    Extract entities and strips tags, and outputs a csv with a column of the
    extracted entities.

    parameters:
        annotated_text, str: path to the annotated text file
        save_name, str: name to save csv file
        lead_tag, str: lead tag for entities
        end_tag, str: end tag for entities
    """
    # Make file into one string
    txt_str = cleanup(annotated_text)
    print(f'Snapshot of the lowercase text to extract: \n\n{txt_str[:1000]}')

    # Get list of entities
    ent_list = []
    ent_list = extract_entities(txt_str, ent_list, lead_tag, end_tag)

    # Make dataframe and export csv
    ent_df = pd.DataFrame(ent_list, columns=['Entities'])
    print(f'\n\nSnapshot of the extracted entities:\n\n{ent_df.Entities.head()}')
    print('\n\nWriting to csv...')
    ent_df.to_csv(save_name, index=False)
    print('\n\nDone!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract hand-annotated entities')

    parser.add_argument('annotated_text', type=str, help='Path to .txt file with '
                        'annotated entities')
    parser.add_argument('save_name', type=str, help='Name to use when saving csv')
    parser.add_argument('lead_tag', type=str, help='Lead tag for entities. Must '
                        'escape <, >, and backslash')
    parser.add_argument('end_tag', type=str, help='End tag for entities. Must '
                        'escape <, >, and backslash')

    args = parser.parse_args()

    args.annotated_text = os.path.abspath(args.annotated_text)

    main(args.annotated_text, args.save_name, args.lead_tag, args.end_tag)
