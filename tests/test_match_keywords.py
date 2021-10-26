"""
Spot checks for match_keywords.py

Author: Serena G. Lotreck
"""
import unittest
import os
import shutil
import sys

sys.path.append('../benchmarks/ontology_keyword_matching')

import match_keywords as mk
import spacy
from spacy.matcher import Matcher


class TestMatchesToBrat(unittest.TestCase):

    def setUp(self):

        # Keywords
        nlp = spacy.load("en_core_web_sm")
        keywords = ['hello world', 'Sparty', 'A. thaliana', 'protein 5']
        self.keywords = [nlp(keyword) for keyword in keywords]
        # Text
        txt = ('Hello world, my name is Sparty. My research is about '
                'A. thaliana protein 5.')
        self.doc = nlp(txt)

        # Matcher
        matcher = Matcher(nlp.vocab)
        patterns = []
        for keyword in self.keywords:
            pattern = [{"LOWER": key_tok.text} for key_tok in keyword]
            patterns.append(pattern)
        matcher.add("Keywords", patterns)
        self.matches = matcher(self.doc)
        print(matcher.get("Keywords"))
        print(self.doc)
        print(self.matches)

    def test_matches_to_brat(self):

        brat_str = mk.matches_to_brat(self.matches, self.doc)

        right_answer = ("T1\tENTITY 0 11\tHello world\n"
                        "T2\tENTITY 24 30\tSparty\n"
                        "T3\tENTITY 53 64\tA. thaliana\n"
                        "T4\tENTITY 65 74\tprotein 5\n")

        print(brat_str)
        self.assertEqual(brat_str, right_answer)


class TestMain(unittest.TestCase):

    def setUp(self):

        # Set up tempdir
        self.tmpdir = "tmp"
        os.makedirs(self.tmpdir, exist_ok=True)
        os.makedirs(f'{self.tmpdir}/txt_dir', exist_ok=True)

        # Set up input files
        keywords = 'hello world\nSparty\nprotein 5\nA. thaliana'
        self.keywords_file = f'{self.tmpdir}/keywords.txt'
        with open(self.keywords_file, 'w') as f:
            f.write(keywords)

        txt = ('Hello world, my name is Sparty. My research is about '
                'A. thaliana protein 5.')
        self.txt_dir = f'{self.tmpdir}/txt_dir'
        self.txt_file = f'{self.txt_dir}/doc.txt'
        self.ann_file = f'{self.txt_dir}/doc.ann'
        with open(self.txt_file, 'w') as f:
            f.write(txt)

        self.right_answer = ("T1\tENTITY 0 11\tHello world\n"
                        "T2\tENTITY 24 30\tSparty\n"
                        "T3\tENTITY 53 64\tA. thaliana\n"
                        "T4\tENTITY 65 74\tprotein 5\n")


    def tearDown(self):

        shutil.rmtree(self.tmpdir)


    def test_main(self):

        mk.main(self.txt_dir, self.keywords_file, False)

        # Read back in answer 
        with open(self.ann_file) as f:
            text = f.read()

        self.assertEqual(text, self.right_answer)


if __name__ == "__main__":
    unittest.main()
