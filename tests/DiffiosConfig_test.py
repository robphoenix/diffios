import os
import sys

import pytest

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.abspath("."))

from diffios import DiffiosConfig
from utils import baseline_blocks, baseline_partition


configs_dir = os.path.abspath(os.path.join("tests", "configs"))
config = os.path.join(configs_dir, "baseline.conf")
dc = DiffiosConfig(config)


def test_default_ignore_filename():
    expected = os.path.join(os.getcwd(), "diffios_ignore")
    actual = dc.ignore_filename
    assert expected == actual


def test_alternative_ignore_filename():
    alt_ignore_path = os.path.join(THIS_DIR, "alt_diffios_ignore")
    actual = DiffiosConfig(config, ignores=alt_ignore_path).ignore_filename
    assert alt_ignore_path == actual


def test_raises_error_if_ignore_file_does_not_exist():
    with pytest.raises(RuntimeError):
        DiffiosConfig(config, ignores="alt_ignore_file")


def test_ignore_filename_is_False_if_ignores_is_False():
    assert DiffiosConfig(config, ignores=False).ignore_filename is False


def test_ignore_filename_is_False_if_ignores_is_empty_list():
    assert DiffiosConfig(config, ignores=[]).ignore_filename is False


def test_ignore_filename_is_False_if_ignores_is_empty_string():
    assert DiffiosConfig(config, ignores="").ignore_filename is False


def test_ignore_filename_is_False_if_ignores_is_zero():
    assert DiffiosConfig(config, ignores=0).ignore_filename is False


def test_config_filename():
    assert dc.config_filename == config


def test_config():
    pytest.skip('config property now removes invalid lines')
    expected = [l.rstrip() for l in open(config).readlines()]
    assert expected, dc.config


def test_hostname():
    assert "BASELINE01" == dc.hostname


def test_blocks():
    assert baseline_blocks() == dc.config_blocks


def test_ignore_lines():
    ignore_file = open("diffios_ignore").readlines()
    expected = [l.strip().lower() for l in ignore_file]
    assert expected == dc.ignores


def test_ignored():
    expected = baseline_partition().ignored
    assert expected == dc.ignored


def test_recorded():
    expected = baseline_partition().recorded
    assert expected == dc.recorded
