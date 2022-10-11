"""
Spot checks for evaluate_model_output.py

Author: Serena G. Lotreck
"""
import unittest
import sys

sys.path.append('../models/')

import numpy as np
import evaluate_model_output as emo

## Didn't write a test for drawing the samples,
## since it just randomly selects and then uses other funcs
## that already have tests

class TestCalculateCI(unittest.TestCase):
    def setUp(self):
        self.prec_samples = [0.1,0.3,0.3,0.5,0.6,0.9]
        self.rec_samples = [0.2,0.2,0.3,0.4,0.4,0.8]
        self.f1_samples = [0.1,0.3,0.4,0.5,0.7,0.7]

        # Calculated with same method as within func, feels un-kosher
        a = 0.05
        lower_p = 100*(a/2)
        upper_p = 100*(1-a/2)
        self.prec_CI = (np.percentile(self.prec_samples, lower_p),
                np.percentile(self.prec_samples, upper_p))
        self.rec_CI = (np.percentile(self.rec_samples, lower_p),
                np.percentile(self.rec_samples, upper_p))
        self.f1_CI = (np.percentile(self.f1_samples, lower_p),
                np.percentile(self.f1_samples, upper_p))

    def test_calculate_CI(self):
        prec_CI, rec_CI, f1_CI = emo.calculate_CI(self.prec_samples,
                self.rec_samples, self.f1_samples)

        self.assertEqual(prec_CI, self.prec_CI)
        self.assertEqual(rec_CI, self.rec_CI)
        self.assertEqual(f1_CI, self.f1_CI)


class TestGetF1Input(unittest.TestCase):
    def setUp(self):

        self.gold_std = [{
            "doc_key":
            "doc1",
            "sentences":
            [['Hello', 'world', ',', 'my', 'name', 'is', 'Sparty', '.'],
             [
                 'My', 'research', 'is', 'about', 'A.', 'thaliana', 'protein',
                 '5'
             ]],
            "ner": [[[0, 1, "ENTITY"], [6, 6, "ENTITY"]],
                    [[12, 13, "ENTITY"], [14, 15, "ENTITY"]]]
        }, {
            "doc_key": "doc2",
            "sentences": [['Hello']],
            "ner": [[]]
        }]

        self.predictions_perfect = [{
            "doc_key":
            "doc1",
            "sentences":
            [['Hello', 'world', ',', 'my', 'name', 'is', 'Sparty', '.'],
             [
                 'My', 'research', 'is', 'about', 'A.', 'thaliana', 'protein',
                 '5'
             ]],
            "predicted_ner": [[[0, 1, "ENTITY"], [6, 6, "ENTITY"]],
                              [[12, 13, "ENTITY"], [14, 15, "ENTITY"]]]
        }, {
            "doc_key": "doc2",
            "sentences": [['Hello']],
            "predicted_ner": [[]]
        }]

        self.predictions_imperfect = [{
            "doc_key":
            "doc1",
            "sentences":
            [['Hello', 'world', ',', 'my', 'name', 'is', 'Sparty', '.'],
             [
                 'My', 'research', 'is', 'about', 'A.', 'thaliana', 'protein',
                 '5'
             ]],
            "predicted_ner": [[[0, 1, "ORG"]],
                              [[9, 9, "ORG"], [13, 13, "PERS"],
                               [14, 15, "PROTEIN"]]]
        }, {
            "doc_key": "doc2",
            "sentences": [['Hello']],
            "predicted_ner": [[[0, 1, "ORG"]]]
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

    def test_get_f1_input_imperfect_matched(self):

        predicted, gold, matched = emo.get_f1_input(self.gold_std,
                                                    self.predictions_imperfect)

        self.assertEqual(matched, 2)


if __name__ == "__main__":
    unittest.main()
