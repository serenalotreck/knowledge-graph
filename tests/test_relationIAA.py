"""
Spot checks for relationIAA.py

Author: Serena G. Lotreck
"""
import unittest
import os
import shutil
import sys


sys.path.append('../annotation/iaa')

import pandas as pd
from pandas.testing import assert_frame_equal
import relationIAA as riaa


class TestGetOffsets(unittest.TestCase):


    def setUp(self):

        self.one_offset = '24 29\tPROT1\n'
        self.multiple_offsets = '24 29;42 44;79 82\tPROT1\n'

        self.right_answer_single = [('24', '29')]
        self.right_answer_multiple = [('24', '29'), ('42', '44'), ('79', '82')]


    def test_get_offstes_single(self):

        offsets = riaa.get_offsets(self.one_offset, [])

        self.assertEqual(offsets, self.right_answer_single)


    def test_get_offsets_multiple(self):

        offsets = riaa.get_offsets(self.multiple_offsets, [])

        self.assertEqual(offsets, self.right_answer_multiple)


class TestFormatRelation(unittest.TestCase):


    def setUp(self):

        self.rel = '\tinteracts-indirect Arg1:T1 Arg2:T4\n'

        self.line_dict = {'T1':'\tPROTEIN 24 29\tPROT1\n',
                          'T4':'\tDNA 42 44\tPRO1\n',
                          'R1':'\tinteracts-indirect Arg1:T1 Arg2:T4\n'}

        self.right_answer = ['interacts-indirect', ([('24','29')], 'PROTEIN'),
                                                    ([('42','44')], 'DNA')]


    def test_format_relation(self):

        rel = riaa.format_relation(self.rel, self.line_dict)

        self.assertEqual(rel, self.right_answer)


class TestMakeAnnDF(unittest.TestCase):


    def setUp(self):

        self.tmpdir = "tmp"
        os.makedirs(self.tmpdir, exist_ok=True)

        ann_full = """T1\tBiochemical_pathway 12 35\tethylene (ET) signaling
T4\tInorganic_compound_other 136 141\tozone
T5\tInorganic_compound_other 143 147\tO(3)
T6\tMulticellular_organism 236 259\tO(3)-sensitive clone 51
T7\tPlant_hormone 271 273\tET
R1\tinteracts-indirect Arg1:T1 Arg2:T7
R2\tinteracts-direct Arg1:T4 Arg2:T5"""

        ann_empty = ""

        self.ann_full_path = f'{self.tmpdir}/ann_full.ann'
        with open(self.ann_full_path, 'w') as myf:
            myf.write(ann_full)

        self.ann_empty_path = f'{self.tmpdir}/ann_empty.ann'
        with open(self.ann_empty_path, 'w') as myf:
            myf.write(ann_empty)


        self.ann_full_df = pd.DataFrame({'Type':['interacts-indirect',
                                            'interacts-direct'],
                                    'Arg1':[([('12','35')], 'Biochemical_pathway'),
                                            ([('136','141')],
                                            'Inorganic_compound_other')],
                                    'Arg2':[([('271','273')], 'Plant_hormone'),
                                            ([('143','147')],
                                            'Inorganic_compound_other')]})

        self.ann_empty_df = pd.DataFrame([], columns=['Type','Arg1','Arg2'])


    def tearDown(self):

        shutil.rmtree(self.tmpdir)


    def test_make_ann_df_full(self):

        ann_df = riaa.make_ann_df(self.ann_full_path)

        assert_frame_equal(ann_df, self.ann_full_df)


    def test_make_ann_df_empty(self):

        ann_df = riaa.make_ann_df(self.ann_empty_path)

        assert_frame_equal(ann_df, self.ann_empty_df)



if __name__ == "__main__":
    unittest.main()

