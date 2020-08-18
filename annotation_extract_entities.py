"""
Extracts entities surrounded by <entsl></entsl> type tags.

Authors: Shinhan Shiu & Serena G. Lotreck
"""
import argparse
import os

import pandas as pd

def strip_outer(astr2):
    """
    Helper for extract_entities.
    """
    astr4 = astr2[astr2.find(">")+1:astr2.rfind("<")]

    return astr4


def strip_tags(astr2, alist):
    """
    Helper for extract_entities.

    Strips tags and returns list of entities without tags.
    """
    astr3 = []
    astr2 = astr2.split("<ent>")
    for i in astr2:
        i = i.split("</ent>")
        astr3.extend(i)
    alist.append("".join(astr3))

    return alist


def find_entities(astr):
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
                    iEnd = i + len("</ent>")
                    ent = astr[iBgn:iEnd]
                    entL.append(ent)
                    cBgn = cEnd = iBgn = iEnd = 0
            else:
                if cBgn == 0:
                    iBgn = i
                cBgn += 1
    return entL


def extract_entities(astr, alist):
    """
    Extracts entities and strips tags.

    parameters:
        astr, str: text string to extract
        alist, list: empty list to populate
    """
    astr2 = find_entities(astr)
    if len(astr2) == 1:
        alist = strip_tags(astr2[0], alist)
        astr_stripped_outer = strip_outer(astr2[0])
        alist = extract_entities(astr_stripped_outer, alist)
    else:
        for i in astr2:
            alist = extract_entities(i, alist)

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


def main(annotated_text, save_name):
    """
    Extract entities and strips tags, and outputs a csv with a column of the
    extracted entities.

    parameters:
        annotated_text, str: path to the annotated text file
        save_name, str: name to save csv file
    """
    # Make file into one string
    txt_str = cleanup(annotated_text)

    # Get list of entities
    ent_list = []
    ent_list = extract_entities(txt_str, ent_list)

    # Make dataframe and export csv
    ent_df = pd.DataFrame(ent_list, columns='Entities')
    print(f'Snapshot of the extracted entities:\n\n{ent_df.head()}')
    print('\n\nWriting to csv...')
    ent_df.to_csv(save_name, index=False)
    print('\n\nDone!')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract hand-annotated entities')

    parser.add_argument('annotated_text', type=str, help='Path to .txt file with '
                        'annotated entities')
    parser.add_argument('save_name', type=str, help='Name to use when saving csv')

    args = parser.parse_args()

    args.annotated_text = os.path.abspath(args.annotated_text)

    main(args.annotated_text, args.save_name)
