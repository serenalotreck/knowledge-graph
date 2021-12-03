"""
Spot checks for unify_annotations.py

Author: Serena G. Lotreck
"""
import unittest
import os
import shutil
import sys

sys.path.append('../annotation/iaa/')

import unify_annotations as ua


class TestUnifyAnnotations(unittest.TestCase):

    def setUp(self):

        self.tmpdir = 'tmp'
        self.annotator1 = 'thilanka'
        self.annotator2 = 'kenia'
        self.iaa_dir_name = 'last_ten'
        os.makedirs(f'{self.tmpdir}/{self.annotator1}/{self.iaa_dir_name}',
                exist_ok=True)
        os.makedirs(f'{self.tmpdir}/{self.annotator2}/{self.iaa_dir_name}',
                exist_ok=True)

        txt = """
        The role of ethylene (ET) signaling in the responses of two hybrid
        aspen (Populus tremula L. x P. tremuloides Michx.) clones to chronic
        ozone (O(3); 75 nL L(-1)) was investigated. The hormonal responses
        differed between the clones; the O(3)-sensitive clone 51 had higher ET
        evolution than the tolerant clone 200 during the exposure, whereas the
        free salicylic acid concentration in clone 200 was higher than in clone
        51. The cellular redox status, measured as glutathione redox balance,
        did not differ between the clones suggesting that the O(3) lesions were
        not a result of deficient antioxidative capacity.
        """
        with open(
            f'{self.tmpdir}/{self.annotator1}/{self.iaa_dir_name}/txt1.txt',
            'w') as myf:
            myf.write(txt)

        with open(
            f'{self.tmpdir}/{self.annotator2}/{self.iaa_dir_name}/txt1.txt',
            'w') as myf:
            myf.write(txt)


        ann1 = """T1\tENTITY 12 20\tethylene
T2\tENTITY 22 24\tET
T3\tENTITY 67 72\taspen
T4\tENTITY 74 116\tPopulus tremula L. x P. tremuloides Michx.
T5\tENTITY 128 141\tchronic ozone
T6\tENTITY 143 148\tO(3);
T7\tENTITY 236 259\tO(3)-sensitive clone 51
T8\tENTITY 271 273\tET
T9\tENTITY 350 364\tsalicylic acid
T10\tENTITY 411 419\tclone 51
"""
        self.ann1 = f'{self.tmpdir}/{self.annotator1}/{self.iaa_dir_name}/txt1.ann'
        with open(self.ann1, 'w') as myf:
            myf.write(ann1)

        ann2 = """T1\tENTITY 12 35\tethylene (ET) signaling
T2\tENTITY 74 92\tPopulus tremula L.
T3\tENTITY 95 116\tP. tremuloides Michx.
T4\tENTITY 136 141\tozone
T5\tENTITY 143 147\tO(3)
T6\tENTITY 236 259\tO(3)-sensitive clone 51
T7\tENTITY 271 273\tET
T8\tENTITY 293 311\ttolerant clone 200
T9\tENTITY 350 364\tsalicylic acid
T10\tENTITY 460 471\tglutathione
"""
        self.ann2 = f'{self.tmpdir}/{self.annotator2}/{self.iaa_dir_name}/txt1.ann'
        with open(self.ann2, 'w') as myf:
            myf.write(ann2)

        # Ordered to reflect the arbitrary but deterministic order in which
        # os.listdir reads in the contents of the directory
        self.right_answer = """T1\tENTITY 12 35\tethylene (ET) signaling
T2\tENTITY 74 92\tPopulus tremula L.
T3\tENTITY 95 116\tP. tremuloides Michx.
T4\tENTITY 136 141\tozone
T5\tENTITY 143 147\tO(3)
T6\tENTITY 236 259\tO(3)-sensitive clone 51
T7\tENTITY 271 273\tET
T8\tENTITY 293 311\ttolerant clone 200
T9\tENTITY 350 364\tsalicylic acid
T10\tENTITY 460 471\tglutathione
T11\tENTITY 12 20\tethylene
T12\tENTITY 22 24\tET
T13\tENTITY 67 72\taspen
T14\tENTITY 74 116\tPopulus tremula L. x P. tremuloides Michx.
T15\tENTITY 128 141\tchronic ozone
T16\tENTITY 143 148\tO(3);
T17\tENTITY 236 259\tO(3)-sensitive clone 51
T18\tENTITY 271 273\tET
T19\tENTITY 350 364\tsalicylic acid
T20\tENTITY 411 419\tclone 51
"""


    def tearDown(self):

        shutil.rmtree(self.tmpdir)


    def test_unify_annotations(self):

        ua.main(self.tmpdir, self.iaa_dir_name, self.tmpdir)

        with open(f'{self.tmpdir}/last_ten_unified/txt1.ann') as myf:
            ann_file = myf.read()

        self.assertEqual(ann_file, self.right_answer)


if __name__ == "__main__":
    unittest.main()
