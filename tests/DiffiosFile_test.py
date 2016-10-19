import os
import sys
import unittest

sys.path.append(os.path.abspath("."))
from diffios import DiffiosFile
from utils import baseline_blocks, baseline_partition


class DiffiosFileTest(unittest.TestCase):

    def setUp(self):
        self.configs_dir = os.path.abspath(os.path.join("tests", "configs"))
        self.config = os.path.join(self.configs_dir, "baseline.conf")
        self.df = DiffiosFile(self.config)

    def test_default_ignore_filename(self):
        expected = os.path.abspath("diffios_ignore")
        actual = self.df.ignore_filename
        self.assertEqual(expected, actual)

    def test_alt_ignore_filename(self):
        alt_df = DiffiosFile(self.config, "alt_ignore_file")
        expected = "alt_ignore_file"
        actual = alt_df.ignore_filename
        self.assertEqual(expected, actual)

    def test_config_filename(self):
        actual = self.config
        expected = self.df.config_filename
        self.assertEqual(expected, actual)

    def test_config_lines(self):
        expected = open(self.config).readlines()
        actual = self.df.config_lines
        self.assertEqual(expected, actual)

    def test_hostname(self):
        expected = "BASELINE01"
        actual = self.df.hostname
        self.assertEqual(expected, actual)

    def test_blocks(self):
        expected = baseline_blocks()
        actual = self.df.blocks
        self.assertEqual(expected, actual)

    def test_ignore_lines(self):
        ignore_file = open("diffios_ignore").readlines()
        expected = [l.strip().lower() for l in ignore_file]
        actual = self.df.ignore_lines()
        self.assertEqual(expected, actual)

    def test_partition(self):
        expected = baseline_partition()
        actual = self.df.partition()
        self.assertEqual(expected, actual)

    def test_ignored(self):
        expected = baseline_partition().ignored
        actual = self.df.ignored()
        self.assertEqual(expected, actual)

    def test_recorded(self):
        expected = baseline_partition().recorded
        actual = self.df.recorded()
        self.assertEqual(expected, actual)
