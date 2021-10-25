"""
Unit tests for dygiepp_to_DOT.py

Author: Serena G. Lotreck
"""
import unittest
import shutil, tempfile
import os

import sys

sys.path.append('../graph_formatting')
import dygiepp_to_DOT as dd


class TestGetTokenizedDoc(unittest.TestCase):
    """
    Test various cases for the function get_tokenized_doc()
    """
    def setUp(self):
        """
        Make single doc dicts for testing
        """
        self.one_sentence_one_word = {
            "doc_key": "PMID1_abstract",
            "dataset": "scierc",
            "sentences": [['hello']]
        }

        self.one_sentence_one_word_answer = ["hello"]

        self.one_sentence_multi_word = {
            "doc_key": "PMID2_abstract",
            "dataset": "scierc",
            "sentences": [['hello', "world", "!"]]
        }

        self.one_sentence_multi_word_answer = ["hello", "world", "!"]

        self.multi_sentence_multi_word = {
            "doc_key":
            "PMID3_abstract",
            "dataset":
            "scierc",
            "sentences": [['hello', "world", "!"],
                          ["I", "like", "you", "world", "."]]
        }

        self.multi_sentence_multi_word_answer = [
            "hello", "world", "!", "I", "like", "you", "world", "."
        ]

    def test_get_tokenized_doc_one_sentence_one_word(self):
        """
        Tests function when there is one sentence containing one word
        """
        test_result = dd.get_tokenized_doc(self.one_sentence_one_word)

        self.assertEqual(test_result, self.one_sentence_one_word_answer)

    def test_get_tokenized_doc_one_sentence_multi_word(self):
        """
        Tests function when there is one sentence with multiple words 
        """
        test_result = dd.get_tokenized_doc(self.one_sentence_multi_word)

        self.assertEqual(test_result, self.one_sentence_multi_word_answer)

    def test_get_tokenized_doc_multi_sentence_multi_word(self):
        """
        Tests function when there are multiple sentences with multiple words
        """
        test_result = dd.get_tokenized_doc(self.multi_sentence_multi_word)

        self.assertEqual(test_result, self.multi_sentence_multi_word_answer)


class TestGetTriples(unittest.TestCase):
    """
    Test various cases for the function get_triples()
    """
    def setUp(self):
        """
        Make DyGIE++-formatted dicts for testing
        """
        # Make dicts
        self.one_doc_no_triples = {
            "doc_key": "PMID1",
            "dataset": "scierc",
            "sentences": [["hello", "world", "!"]],
            "predicted_relations": [[]]
        }

        self.one_doc_one_triple = {
            "doc_key": "PMID2",
            "dataset": "scierc",
            "sentences": [["hello", "world", "!"]],
            "predicted_relations": [[[0, 0, 1, 1, "TO_THE", 0.89, 1.45]]]
        }

        self.one_doc_multiple_triples = {
            "doc_key":
            "PMID3_abstract",
            "dataset":
            "scierc",
            "sentences": [['hello', "world", "!"],
                          ["I", "like", "you", "world", "."]],
            "predicted_relations": [[[0, 0, 1, 1, "TO_THE", 0.89, 1.45]],
                                    [[3, 3, 5, 5, "LIKE", 0.76, 1.49],
                                     [3, 3, 6, 6, "LIKE", 0.45, 3.548]]]
        }

        self.one_doc_compound_triples = {
            "doc_key":
            "PMID3_abstract",
            "dataset":
            "scierc",
            "sentences": [['hello', "world", "!"],
                          ["I", "like", "you", "world", "."]],
            "predicted_relations": [[[0, 0, 1, 1, "TO_THE", 0.89, 1.45]],
                                    [[3, 3, 5, 6, "LIKE", 0.76, 1.49]]]
        }

    def test_get_triples_one_doc_no_triples(self):
        """
        Tests that there are no triples returned when the doc's list is empty
        """
        test_result = dd.get_triples([self.one_doc_no_triples])

        right_answer = []

        self.assertEqual(test_result, right_answer)

    def test_get_triples_one_doc_one_triple(self):
        """
        Tests function when there is one doc with one single words triple
        """
        test_result = dd.get_triples([self.one_doc_one_triple])

        right_answer = [("hello", "TO_THE", "world")]

        self.assertEqual(test_result, right_answer)

    def test_get_triples_one_doc_multiple_triples(self):
        """
        Tests function when there is one doc with multiple triples with single 
        word entities
        """
        test_result = dd.get_triples([self.one_doc_multiple_triples])

        right_answer = [("hello", "TO_THE", "world"), ("I", "LIKE", "you"),
                        ("I", "LIKE", "world")]

        self.assertEqual(test_result, right_answer)

    def test_get_triples_one_doc_compound_triples(self):
        """
        Tests that the function successfully merges compound entities
        """
        test_result = dd.get_triples([self.one_doc_compound_triples])

        right_answer = [("hello", "TO_THE", "world"),
                        ("I", "LIKE", "you world")]

        self.assertEqual(test_result, right_answer)

    def test_get_triples_multi_doc_mixed(self):
        """
        Test function when all three individual doc cases are mixed
        """
        docs = [
            self.one_doc_no_triples, self.one_doc_one_triple,
            self.one_doc_multiple_triples, self.one_doc_compound_triples
        ]
        test_result = dd.get_triples(docs)

        right_answer = [("hello", "TO_THE", "world"),
                        ("hello", "TO_THE", "world"), ("I", "LIKE", "you"),
                        ("I", "LIKE", "world"), ("hello", "TO_THE", "world"),
                        ("I", "LIKE", "you world")]

        self.assertEqual(test_result, right_answer)


class TestGetLooseEnts(unittest.TestCase):
    """
    Test get_loose_ents()
    """
    def setUp(self):
        """
        Set up triple lists and docs 
        """
        self.triples = [("hello", "TO_THE", "world"), ("I", "LIKE", "you")]

        self.no_overlap = {
            "doc_key":
            "PMID3_abstract",
            "dataset":
            "scierc",
            "sentences": [['hello', "world", "!"],
                          ["I", "like", "you", "world", "."]],
            "predicted_ner": [[],
                              [[4, 4, "TYPE", 0.345, 1.345],
                               [5, 6, "TYPE2", 0.43, 1.34]]]
        }

        self.overlap = {
            "doc_key":
            "PMID4_abstract",
            "dataset":
            "scierc",
            "sentences": [['hello', "world", "!"],
                          ["I", "like", "you", "world", "."]],
            "predicted_ner": [[[0, 0, "TYPE3", 0.3457, 1.34]],
                              [[4, 4, "TYPE", 0.345, 1.345],
                               [5, 6, "TYPE2", 0.43, 1.34]]]
        }

        self.right_answer = ["like", "you world"]

    def test_get_loose_ents_no_overlap(self):
        """
        Test that all loose ents get returned
        """
        test_result = dd.get_loose_ents([self.no_overlap], self.triples)

        self.assertEqual(test_result, self.right_answer)

    def test_get_loose_ents_overlap(self):
        """
        Test that entities already included in triples aren't included
        """
        test_result = dd.get_loose_ents([self.overlap], self.triples)

        self.assertEqual(test_result, self.right_answer)


class TestWriteDotFile(unittest.TestCase):
    """
    Tests the output file
    """
    def setUp(self):
        """
        Set up temp dirs and files
        """
        self.test_dir = os.path.abspath(tempfile.mkdtemp())
        self.triples = [("hello", "TO_THE", "world"),
                        ("hello", "TO_THE", "world"),
                        ("hello", "TO_THE", "world"),
                        ("I", "LIKE", "you world")]
        self.loose_ents = ["you"]
        self.graph_name = "my_graph"
        self.proper_DOT_no_ents = (
            f'strict digraph {self.graph_name} '
            '{\n\thello -> world\t[label=TO_THE,\n'
            '\t\tweight=3];\n\tI -> "you world"\t[label=LIKE,\n'
            '\t\tweight=1];\n}')
        self.proper_DOT_ents = (
            f'strict digraph {self.graph_name} '
            '{\n\thello -> world\t[label=TO_THE,\n'
            '\t\tweight=3];\n\tI -> "you world"\t[label=LIKE,\n'
            '\t\tweight=1];\n\tyou;\n}')

    def tearDown(self):
        """
        Delete directory and files used for testing
        """
        shutil.rmtree(self.test_dir)

    def test_write_dot_file_no_ents(self):
        """
        Test that the file is written properly when there are only triples
        """
        dd.write_dot_file(self.triples, [], self.graph_name, self.test_dir)

        with open(f'{self.test_dir}/{self.graph_name}.gv') as myfile:
            test_result = myfile.read()
        print(test_result, self.proper_DOT_no_ents)
        self.assertEqual(test_result, self.proper_DOT_no_ents)

    def test_write_dot_file_loose_ents(self):
        """
        Test that the file is writen properly when there are loose ents
        """
        dd.write_dot_file(self.triples, self.loose_ents, self.graph_name,
                          self.test_dir)

        with open(f'{self.test_dir}/{self.graph_name}.gv') as myfile:
            test_result = myfile.read()
        print(test_result, self.proper_DOT_ents)
        self.assertEqual(test_result, self.proper_DOT_ents)


if __name__ == "__main__":
    unittest.main()
