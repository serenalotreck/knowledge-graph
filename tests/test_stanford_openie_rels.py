"""
Spot checks for stanford_openie_rels.py.

Author: Serena G. Lotreck
"""
import unittest
import sys

sys.path.append('../models/benchmarks/stanford_openie_relations')

import stanford_openie_rels as sor
from stanza.server import CoreNLPClient


class TestDocSents(unittest.TestCase):
    def setUp(self):

        text1 = 'My name is Sparty. I like to wear green, and I am from Michigan.'
        text2 = ''
        text3 = 'My name is Sparty.'

        with CoreNLPClient(annotators=["openie"],
                           output_format="json") as client:
            self.ann1 = client.annotate(text1)
            self.ann2 = client.annotate(text2)
            self.ann3 = client.annotate(text3)

        self.right_answer_1 = [['My', 'name', 'is', 'Sparty', '.'],
                               [
                                   'I', 'like', 'to', 'wear', 'green', ',',
                                   'and', 'I', 'am', 'from', 'Michigan', '.'
                               ]]
        self.right_answer_2 = []
        self.right_answer_3 = [['My', 'name', 'is', 'Sparty', '.']]

    def test_doc_sents_mult_sents(self):

        sents = sor.get_doc_sents(self.ann1)

        self.assertEqual(sents, self.right_answer_1)

    def test_doc_sents_no_text(self):

        sents = sor.get_doc_sents(self.ann2)

        self.assertEqual(sents, self.right_answer_2)

    def test_doc_sents_one_sent(self):

        sents = sor.get_doc_sents(self.ann3)

        self.assertEqual(sents, self.right_answer_3)


class TestGetDocEnts(unittest.TestCase):
    def setUp(self):

        text1 = 'My name is Sparty. I like to wear green, and I am from Michigan.'
        text2 = ''
        text3 = 'My name is Sparty.'

        with CoreNLPClient(annotators=["openie"],
                           output_format="json") as client:
            self.ann1 = client.annotate(text1)
            self.ann2 = client.annotate(text2)
            self.ann3 = client.annotate(text3)

        self.right_answer_1 = [[[0, 1, "ENTITY"], [3, 3, "ENTITY"]],
                               [[5, 5, "ENTITY"], [8, 8, "ENTITY"],
                                [7, 8, "ENTITY"], [9, 9, "ENTITY"],
                                [12, 12, "ENTITY"], [15, 15, "ENTITY"]]]
        self.right_answer_2 = []
        self.right_answer_3 = [[[0, 1, "ENTITY"], [3, 3, "ENTITY"]]]

    def test_get_doc_ents_mult_sents(self):

        ents = sor.get_doc_ents(self.ann1)
        print(ents)
        print(self.right_answer_1)
        self.assertEqual(ents, self.right_answer_1)

    def test_get_doc_ents_no_text(self):

        ents = sor.get_doc_ents(self.ann2)

        self.assertEqual(ents, self.right_answer_2)

    def test_get_doc_ents_one_sent(self):

        ents = sor.get_doc_ents(self.ann3)

        self.assertEqual(ents, self.right_answer_3)


class TestGetDocRels(unittest.TestCase):
    def setUp(self):

        text1 = 'My name is Sparty. I like to wear green, and I am from Michigan.'
        text2 = ''
        text3 = 'My name is Sparty.'

        with CoreNLPClient(annotators=["openie"],
                           output_format="json") as client:
            self.ann1 = client.annotate(text1)
            self.ann2 = client.annotate(text2)
            self.ann3 = client.annotate(text3)

        self.right_answer_1 = [[[0, 1, 3, 3, 'is']],
                               [[5, 5, 8, 8, 'like'], [5, 5, 7, 8, 'like'],
                                [5, 5, 9, 9, 'wear'],
                                [12, 12, 15, 15, 'am from']]]
        self.right_answer_2 = []
        self.right_answer_3 = [[[0, 1, 3, 3, 'is']]]


    def test_get_doc_rels_mult_sent(self):

        rels = sor.get_doc_rels(self.ann1)

        self.assertEqual(rels, self.right_answer_1)


    def test_get_doc_rels_no_text(self):

        rels = sor.get_doc_rels(self.ann2)

        self.assertEqual(rels, self.right_answer_2)


    def test_get_doc_rels_one_sent(self):

        rels = sor.get_doc_rels(self.ann3)

        self.assertEqual(rels, self.right_answer_3)


class TestOpenieToDygiepp(unittest.TestCase):
    def setUp(self):

        text1 = 'My name is Sparty. I like to wear green, and I am from Michigan.'
        text2 = ''
        text3 = 'My name is Sparty.'

        self.doc_key = 'doc_1'

        with CoreNLPClient(annotators=["openie"],
                           output_format="json") as client:
            self.ann1 = client.annotate(text1)
            self.ann2 = client.annotate(text2)
            self.ann3 = client.annotate(text3)

        self.right_answer_1 = {
            "doc_key":
            self.doc_key,
            "dataset":
            'scierc',
            "sentences": [['My', 'name', 'is', 'Sparty', '.'],
                          [
                              'I', 'like', 'to', 'wear', 'green', ',', 'and',
                              'I', 'am', 'from', 'Michigan', '.'
                          ]],
            "predicted_ner": [[[0, 1, "ENTITY"], [3, 3, "ENTITY"]],
                              [[5, 5, "ENTITY"], [8, 8, "ENTITY"],
                               [7, 8, "ENTITY"], [9, 9, "ENTITY"],
                               [12, 12, "ENTITY"], [15, 15, "ENTITY"]]],
            "predicted_relations": [[[0, 1, 3, 3, 'is']],
                                    [[5, 5, 8, 8,
                                      'like'], [5, 5, 7, 8, 'like'],
                                     [5, 5, 9, 9, 'wear'],
                                     [12, 12, 15, 15, 'am from']]]
        }

        self.right_answer_2 = {
            "doc_key": self.doc_key,
            "dataset": 'scierc',
            "sentences": [],
            "predicted_ner": [],
            "predicted_relations": []
        }

        self.right_answer_3 = {
            "doc_key": self.doc_key,
            "dataset": 'scierc',
            "sentences": [['My', 'name', 'is', 'Sparty', '.']],
            "predicted_ner": [[[0, 1, "ENTITY"], [3, 3, "ENTITY"]]],
            "predicted_relations": [[[0, 1, 3, 3, 'is']]]
        }

    def test_openie_to_dygiepp_mult_sent(self):

        json = sor.openie_to_dygiepp(self.ann1, self.doc_key)

        self.assertEqual(json, self.right_answer_1)

    def test_openie_to_dygiepp_no_text(self):

        json = sor.openie_to_dygiepp(self.ann2, self.doc_key)

        self.assertEqual(json, self.right_answer_2)

    def test_openie_to_dygiepp_one_sent(self):

        json = sor.openie_to_dygiepp(self.ann3, self.doc_key)

        self.assertEqual(json, self.right_answer_3)


if __name__ == "__main__":
    unittest.main()
