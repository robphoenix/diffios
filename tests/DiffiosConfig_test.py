import os
import sys
import unittest

sys.path.append(os.path.abspath("."))
from diffios import DiffiosConfig
from utils import baseline_blocks, baseline_partition


class DiffiosConfigTest(unittest.TestCase):

    def setUp(self):
        self.configs_dir = os.path.abspath(os.path.join("tests", "configs"))
        self.config = os.path.join(self.configs_dir, "baseline.conf")
        self.df = DiffiosConfig(self.config)

    def test_default_ignore_filename(self):
        expected = os.path.abspath("diffios_ignore")
        actual = self.df.ignore_filename
        self.assertEqual(expected, actual)

    def test_ignore_filename_is_false_if_ignore_file_does_not_exist(self):
        dc = DiffiosConfig(self.config, ignores="alt_ignore_file")
        self.assertFalse(dc.ignore_filename)

    def test_config_filename(self):
        actual = self.config
        expected = self.df.config_filename
        self.assertEqual(expected, actual)

    # config property now removes invalid lines
    # def test_config(self):
        # expected = [l.rstrip() for l in open(self.config).readlines()]
        # actual = self.df.config
        # self.assertEqual(expected, actual)

    def test_hostname(self):
        expected = "BASELINE01"
        actual = self.df.hostname
        self.assertEqual(expected, actual)

    def test_blocks(self):
        expected = baseline_blocks()
        actual = self.df.config_blocks
        self.assertEqual(expected, actual)

    def test_ignore_lines(self):
        ignore_file = open("diffios_ignore").readlines()
        expected = [l.strip().lower() for l in ignore_file]
        actual = self.df.ignores
        self.assertEqual(expected, actual)

    def test_ignored(self):
        expected = baseline_partition().ignored
        actual = self.df.ignored
        self.assertEqual(expected, actual)

    def test_recorded(self):
        expected = baseline_partition().recorded
        actual = self.df.recorded
        self.assertEqual(expected, actual)
