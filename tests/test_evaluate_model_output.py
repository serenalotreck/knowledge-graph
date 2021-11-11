"""
Spot checks for evaluate_model_output.py

Author: Serena G. Lotreck
"""
import unittest
import sys

sys.path.append('../models/')

import evaluate_model_output as emo


class TestGetF1Input(unittest.TestCase):

    def setUp(self):

        self.gold_std = [{"doc_key":"doc1",
                    "sentences":[['Hello', 'world', ',', 'my', 'name', 'is',
                                    'Sparty', '.'],
                                 ['My', 'research', 'is', 'about', 'A.',
                                    'thaliana', 'protein', '5']],
                    "ner":[[[0, 1, "ENTITY"],
                            [6, 6, "ENTITY"]],
                           [[12, 13, "ENTITY"],
                            [14, 15, "ENTITY"]]]
                    },
                    {"doc_key":"doc2",
                    "sentences":[['Hello']],
                    "ner":[[]]
                    }]

        self.predictions_perfect = [{"doc_key":"doc1",
                        "sentences":[['Hello', 'world', ',', 'my', 'name', 'is',
                                    'Sparty', '.'],
                                     ['My', 'research', 'is', 'about', 'A.',
                                    'thaliana', 'protein', '5']],
                        "predicted_ner":[[[0, 1, "ENTITY"],
                                          [6, 6, "ENTITY"]],
                                         [[12, 13, "ENTITY"],
                                          [14, 15, "ENTITY"]]]
                        },
                        {"doc_key":"doc2",
                        "sentences":[['Hello']],
                        "predicted_ner":[[]]
                        }]

        self.predictions_imperfect = [{"doc_key":"doc1",
                        "sentences":[['Hello', 'world', ',', 'my', 'name', 'is',
                                    'Sparty', '.'],
                                     ['My', 'research', 'is', 'about', 'A.',
                                    'thaliana', 'protein', '5']],
                        "predicted_ner":[[[0, 1, "ORG"]],
                                         [[9, 9, "ORG"],
                                          [13, 13, "PERS"],
                                          [14, 15, "PROTEIN"]]]
                        },
                        {"doc_key":"doc2",
                        "sentences":[['Hello']],
                        "predicted_ner":[[[0, 1, "ORG"]]]
                        }]


    def test_get_f1_input_perfect_predicted(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                self.predictions_perfect)

        self.assertEqual(predicted, 4)


    def test_get_f1_input_perfect_gold(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                self.predictions_perfect)

        self.assertEqual(gold, 4)


    def test_get_f1_input_perfect_matched(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                self.predictions_perfect)

        self.assertEqual(matched, 4)


    def test_get_f1_input_imperfect_predicted(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                self.predictions_imperfect)

        self.assertEqual(predicted, 5)

    def test_get_f1_input_imperfect_gold(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                self.predictions_imperfect)

        self.assertEqual(gold, 4)


    def test_get_f1_input_impoerfect_matched(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                self.predictions_imperfect)

        self.assertEqual(matched, 2)


if __name__ == "__main__":
    unittest.main()
