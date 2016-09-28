import os
import sys
import unittest

sys.path.append(os.path.abspath(".."))
from diffios import DiffiosFile
from utils import baseline_blocks, baseline_partition


class DiffiosFileTest(unittest.TestCase):

    def setUp(self):
        self.configs_dir = os.path.abspath("configs")
        self.config = os.path.join(self.configs_dir, "baseline.conf")
        self.df = DiffiosFile(self.config)

    def test_default_ignore_filename(self):
        expected = os.path.abspath("../diffios_ignore")
        actual = self.df.ignore_filename
        self.assertEqual(actual, expected)


    def test_alt_ignore_filename(self):
        alt_df = DiffiosFile(self.config, "alt_ignore_file")
        expected = "alt_ignore_file"
        actual = alt_df.ignore_filename
        self.assertEqual(actual, expected)


    def test_config_filename(self):
        actual = self.config
        expected = self.df.config_filename
        self.assertEqual(actual, expected)


    def test_config_lines(self):
        expected = open(self.config).readlines()
        actual = self.df.config_lines
        self.assertEqual(actual, expected)


    def test_hostname(self):
        expected = "BASELINE01"
        actual = self.df.hostname
        self.assertEqual(actual, expected)


    def test_blocks(self):
        expected = baseline_blocks()
        actual = self.df.blocks
        self.assertEqual(actual, expected)


    def test_ignore(self):
        ignore_file = open("../diffios_ignore").readlines()
        expected = [l.strip().lower() for l in ignore_file]
        actual = self.df.ignore()
        self.assertEqual(actual, expected)


    def test_partition(self):
        expected = baseline_partition()
        actual = self.df.partition()
        self.assertEqual(actual, expected)


    def test_dirty(self):
        expected = baseline_partition()["ignored"]
        actual = self.df.dirty()
        assert actual == expected


    def test_cleaned(self):
        expected = baseline_partition()["recorded"]
        actual = self.df.cleaned()
        assert actual == expected
