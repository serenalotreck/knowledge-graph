"""
Script to generate gibberish text documents with certain statistical properties. 

Adapted from https://stackoverflow.com/a/22675818

Author: Serena G. Lotreck
"""
import os 
import argparse 

from itertools import islice
from random import choice, randint
import pandas as pd 

# Define universal frequencies 
## Letter frequency
LETTERS = (    # relative character frequencies
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabb"
        "bbbbbbbbbbcccccccccccccccccccccdddddddddddddddddddddddddddddddde"
        "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeefffffffffffffffffgggggggggggggggg"
        "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhiiiiiiiiiiiiiiiiii"
        "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiijjkkkkkklllllllllllllllllllll"
        "llllllllllmmmmmmmmmmmmmmmmmmmnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
        "nnnnnnnnnnnnnnnnoooooooooooooooooooooooooooooooooooooooooooooooo"
        "ooooooooopppppppppppppppqrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        "rrrrrrsssssssssssssssssssssssssssssssssssssssssssssssstttttttttt"
        "ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttuuuuuu"
        "uuuuuuuuuuuuuuuvvvvvvvvwwwwwwwwwwwwwwwwwwxxxyyyyyyyyyyyyyyyzz"
        )

CONSONANTS  = ''.join(ch for ch in LETTERS if ch not in "aeiouy")
VOWELS      = ''.join(ch for ch in LETTERS if ch     in "aeiouy")
PUNCTUATION = "....?"

is_cons     = set(CONSONANTS).__contains__    # is_cons(x) == x in set(CONSONANTS)

## Word length frequency
WORDLEN = [     # relative word-length frequencies
            2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,
            2,  2,  2,  2,  2,  3,  3,  3,  3,  3,  3,  3,
            3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,
            3,  3,  3,  3,  4,  4,  4,  4,  4,  4,  4,  4,
            4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,
            5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,
            5,  5,  6,  6,  6,  6,  6,  6,  6,  6,  6,  6,
            7,  7,  7,  7,  7,  7,  7,  7,  8,  8,  8,  8,
            8,  9,  9,  9, 10, 10, 10, 11, 11, 12
            ]

wordlen = lambda: choice(WORDLEN)


def gibberish():
    """
    Generate an infinite sequence of random letters,
    allowing no more than two consecutive consonants
    """
    a = choice(LETTERS); yield a
    b = choice(LETTERS); yield b
    while True:
        c = choice(VOWELS if is_cons(a) and is_cons(b) else LETTERS)
        yield c
        a, b = b, c


def take_n(chars, n):
    """
    Return an iterable with a slice of the character string of length n
    """
    return list(islice(chars, n))


def add_spaces(chars, wordlen):
    """
    Add spaces to gibberish sequence. 

    parameters:
        chars, iterable: output of take_n
        wordlen, lambda function: chooses word length 
    """
    chars = iter(chars)
    while True:
        for i in range(wordlen()):
            yield next(chars)
        yield ' '


def make_gibberish_sentence(len_chars):
    """
    Makes a gibberish sentence with the specified number of non-space
    characters.

    parameters:
        len_chars, int: number of non-space character to include

    returns:
        sentence, str: the gibberish sentence
    """
    chars = take_n(gibberish(), len_chars)              # Get chars
    chars = add_spaces(chars, wordlen)                  # Add spaces to make "words"
    sentence = ''.join(chars).rsplit(' ',1)[0]          # Crop at last space  
    return sentence.capitalize() + choice(PUNCTUATION)  # Capitalize first letter and add punct


def main(num_docs, chars_per_sent, sents_per_doc, out_loc):

    # Define frequencies that depend on corpus statistics
    print('\nDefining character and sentence frequencies...')
    ## Number of words per sentence
    chars_per_sent = pd.read_csv(chars_per_sent, header=None)[0].tolist()
    cps = lambda: choice(chars_per_sent)

    ## Number of sentences per document 
    sents_per_doc = pd.read_csv(sents_per_doc, header=None)[0].tolist()
    spd = lambda: choice(sents_per_doc)

    # Generate docs 
    print('\nGenerating gibberish docs...')

    for i in range(num_docs):

        print(f'Generating doc {i}')

        doc = ''

        # Choose a number of sentences for the doc
        for j in range(spd()):
            
            # Choose number of chars and make sentence
            sentence = make_gibberish_sentence(cps()) + ' '

            doc += sentence


        with open(f'{out_loc}/gib_doc_{i}.txt', 'w') as myfile:

            myfile.write(doc)

    print('\nDone!')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Generate gibberish abstracts')

    parser.add_argument('num_docs', type=int,
            help='Number of documents to generate')
    parser.add_argument('chars_per_sent', type=str,
            help='Path to file with chars per sent for corpus to emulate.')
    parser.add_argument('sents_per_doc', type=str,
            help='Path to file with sents per doc for corpus to emulate.')
    parser.add_argument('out_loc', type=str,
            help='Path to directory to save generated documents.')

    args = parser.parse_args()

    args.chars_per_sent = os.path.abspath(args.chars_per_sent)
    args.sents_per_doc = os.path.abspath(args.sents_per_doc)
    args.out_loc = os.path.abspath(args.out_loc)

    main(args.num_docs, args.chars_per_sent, args.sents_per_doc, args.out_loc)
