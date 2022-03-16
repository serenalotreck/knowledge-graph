"""
Spot checks for run_dygiepp.py

Doesn't check functions fotmat_data, run_models, or evaluate models, because
these require input of a true dygiepp path, and their main functionality is
just to call code that's already been tested elsewhere.

Author: Serena G. Lotreck
"""
import unittest
import sys
import os
from os.path import abspath
from tempfile import mkdtemp
import filecmp
import shutil

sys.path.append('../models/neural_models/')

import run_dygiepp as rd


class TestCheckMakeFiletree(unittest.TestCase):

    def setUp(self):

        # Set up tempdir
        self.tmpdir = mkdtemp()

        # Add existing filetree with all correct subdirs
        self.filetree1 = abspath(f'{self.tmpdir}/filetree1')
        os.makedirs(self.filetree1)
        for subdir in ['formatted_data', 'model_predictions',
                'allennlp_output', 'performance']:
            os.makedirs(f'{self.filetree1}/{subdir}')

        # Add existing filetree missing two dirs
        self.filetree2 = abspath(f'{self.tmpdir}/filetree2')
        os.makedirs(self.filetree2)
        for subdir in ['formatted_data', 'performance']:
            os.makedirs(f'{self.filetree2}/{subdir}')

        # Define location for the nonexistent tree
        self.testtree = abspath(f'{self.tmpdir}/testtree')

        # Right answer
        self.subdirs = sorted(['formatted_data', 'model_predictions',
                'allennlp_output', 'performance'])


    def tearDown(self):

        shutil.rmtree(self.tmpdir)


    def test_check_make_filetree_all_exist(self):

        topdir_abspath = self.filetree1
        out = rd.check_make_filetree(topdir_abspath)

        subdirs = sorted(os.listdir(topdir_abspath))

        self.assertEqual(subdirs, self.subdirs)
        self.assertEqual(out, True)


    def test_check_make_filetree_some_exist(self):

        topdir_abspath = self.filetree2
        out = rd.check_make_filetree(topdir_abspath)

        subdirs = sorted(os.listdir(topdir_abspath))

        self.assertEqual(subdirs, self.subdirs)
        self.assertEqual(out, True)


    def test_check_make_filetree_none_exist(self):

        topdir_abspath = self.testtree
        out = rd.check_make_filetree(topdir_abspath)

        subdirs = sorted(os.listdir(topdir_abspath)) # Fails if topdir isn't created

        self.assertEqual(subdirs, self.subdirs)
        self.assertEqual(out, False)


class TestCheckPrefix(unittest.TestCase):

    def setUp(self):

        # Set up tempdir
        self.tmpdir = mkdtemp()

        # Add existing filetree with no prefix present
        self.filetree1 = abspath(f'{self.tmpdir}/filetree1')
        os.makedirs(self.filetree1)
        for subdir in ['formatted_data', 'model_predictions',
                'allennlp_output', 'performance']:
            os.makedirs(f'{self.filetree1}/{subdir}')
        arbitrary_file_path = (
        abspath(f'{self.tmpdir}/filetree1/formatted_data/hello_world.py'))
        os.system(f"touch {arbitrary_file_path}")

        # Add existing filetree with prefix present
        self.filetree2 = abspath(f'{self.tmpdir}/filetree2')
        os.makedirs(self.filetree2)
        for subdir in ['formatted_data', 'model_predictions',
                'allennlp_output', 'performance']:
            os.makedirs(f'{self.filetree2}/{subdir}')
        self.prefix = 'my_prefix'
        prefix_file_path = (
                abspath(f'{self.filetree2}/formatted_data/{self.prefix}_other_stuff.py'))
        os.system(f"touch {prefix_file_path}")


    def tearDown(self):

        shutil.rmtree(self.tmpdir)


    def test_check_prefix_no_prefix(self):

        try:
            rd.check_prefix(self.filetree1, self.prefix)
        except:
            self.fail('Check prefix raised an exception')


    def test_check_prefix_with_prefix(self):

        with self.assertRaises(rd.PrefixError):
            rd.check_prefix(self.filetree2, self.prefix)


class TestCheckModels(unittest.TestCase):


    def setUp(self):

        # Set up tempdir
        self.tmpdir = mkdtemp()

        # Make dygiepp dirs
        self.dygiepp_path1 = abspath(f'{self.tmpdir}/dygiepp1')
        os.makedirs(self.dygiepp_path1)

        self.dygiepp_path2 = abspath(f'{self.tmpdir}/dygiepp2')
        os.makedirs(self.dygiepp_path2)

        # Make model folders and files
        self.models1 = ['genia', 'scierc-light']
        os.makedirs(f'{self.dygiepp_path1}/pretrained')
        for model in self.models1:
            os.system(f'touch {self.dygiepp_path1}/pretrained/{model}.tar.gz')

        self.models2 = ['genia', 'scierc', 'ace05']
        os.makedirs(f'{self.dygiepp_path2}/pretrained')
        for model in self.models2[:2]:
            os.system(f'touch {self.dygiepp_path2}/pretrained/{model}.tar.gz')


    def tearDown(self):

        shutil.rmtree(self.tmpdir)


    def test_check_models_models_present(self):

        try:
            rd.check_models(self.models1, self.dygiepp_path1)
        except:
            self.fail('Check models raised an exception')


    def test_check_models_models_missing(self):

        with self.assertRaises(rd.ModelNotFoundError):
            rd.check_models(self.models2, self.dygiepp_path2)


class TestReplaceSeeds(unittest.TestCase):

    def setUp(self):

        # Make template string
        self.template = ('Hi my name is Sparty and I like random_seed: 12746, '
        'numpy_seed: 1274, and pytorch_seed: 127, and I like green.')

        # Make seed dict
        main_seed = 94857
        self.rand_seeds = {
                 'random_seed: ': main_seed,
                 'numpy_seed: ': main_seed // 10,
                 'pytorch_seed: ': main_seed // 100
                 }

        # Define right answer
        self.right_answer = (f'Hi my name is Sparty and I like random_seed: {main_seed}, '
        f'numpy_seed: {main_seed//10}, and pytorch_seed: {main_seed//100}, and I like green.')


    def test_replace_seeds(self):

        new_template = rd.replace_seeds(self.template, self.rand_seeds)

        self.assertEqual(new_template, self.right_answer)

if __name__ == "__main__":
    unittest.main()



