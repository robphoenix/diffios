import os
import sys
import unittest

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.abspath("."))

from diffios import DiffiosConfig
from utils import baseline_blocks, baseline_partition


class DiffiosConfigTest(unittest.TestCase):

    def setUp(self):
        self.configs_dir = os.path.abspath(os.path.join("tests", "configs"))
        self.config = os.path.join(self.configs_dir, "baseline.conf")
        self.dc = DiffiosConfig(self.config)

    def test_default_ignore_filename(self):
        expected = os.path.join(os.getcwd(), "diffios_ignore")
        actual = self.dc.ignore_filename
        self.assertEqual(expected, actual)

    def test_alternative_ignore_filename(self):
        alt_ignore_path = os.path.join(THIS_DIR, "alt_diffios_ignore")
        expected = alt_ignore_path
        dc = DiffiosConfig(self.config, ignores=alt_ignore_path)
        actual = dc.ignore_filename
        self.assertEqual(expected, actual)

    def test_raises_error_if_ignore_file_does_not_exist(self):
        with self.assertRaises(RuntimeError) as e:
            DiffiosConfig(self.config, ignores="alt_ignore_file")
        self.assertEqual(
            str(e.exception),
            "[FATAL] DiffiosConfig() received an invalid argument: ignores=alt_ignore_file\n")

    def test_ignore_filename_is_False_if_ignores_is_False(self):
        dc = DiffiosConfig(self.config, ignores=False)
        self.assertFalse(dc.ignore_filename)

    def test_ignore_filename_is_False_if_ignores_is_empty_list(self):
        dc = DiffiosConfig(self.config, ignores=[])
        self.assertFalse(dc.ignore_filename)

    def test_ignore_filename_is_False_if_ignores_is_empty_string(self):
        dc = DiffiosConfig(self.config, ignores="")
        self.assertFalse(dc.ignore_filename)

    def test_ignore_filename_is_False_if_ignores_is_zero(self):
        dc = DiffiosConfig(self.config, ignores=0)
        self.assertFalse(dc.ignore_filename)

    def test_config_filename(self):
        actual = self.config
        expected = self.dc.config_filename
        self.assertEqual(expected, actual)

    # config property now removes invalid lines
    # def test_config(self):
        # expected = [l.rstrip() for l in open(self.config).readlines()]
        # actual = self.df.config
        # self.assertEqual(expected, actual)

    def test_hostname(self):
        expected = "BASELINE01"
        actual = self.dc.hostname
        self.assertEqual(expected, actual)

    def test_blocks(self):
        expected = baseline_blocks()
        actual = self.dc.config_blocks
        self.assertEqual(expected, actual)

    def test_ignore_lines(self):
        ignore_file = open("diffios_ignore").readlines()
        expected = [l.strip().lower() for l in ignore_file]
        actual = self.dc.ignores
        self.assertEqual(expected, actual)

    def test_ignored(self):
        expected = baseline_partition().ignored
        actual = self.dc.ignored
        self.assertEqual(expected, actual)

    def test_recorded(self):
        expected = baseline_partition().recorded
        actual = self.dc.recorded
        self.assertEqual(expected, actual)
