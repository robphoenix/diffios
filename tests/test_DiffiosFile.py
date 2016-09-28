import os

import sys

sys.path.append(os.path.abspath("../diffios"))
from diffios import DiffiosFile
from utils import candidate_blocks, candidate_partition


configs_dir = os.path.abspath("./configs/")
config = os.path.join(configs_dir, "candidate.conf")
df = DiffiosFile(config)


def test_default_ignore_filename():
    expected = os.path.abspath("../diffios_ignore")
    actual = df.ignore_filename
    assert actual == expected


def test_alt_ignore_filename():
    alt_df = DiffiosFile(config, "alt_ignore_file")
    expected = "alt_ignore_file"
    actual = alt_df.ignore_filename
    assert actual == expected


def test_config_filename():
    actual = config
    expected = df.config_filename
    assert actual == expected


def test_config_lines():
    expected = open(config).readlines()
    actual = df.config_lines
    assert actual == expected


def test_hostname():
    expected = "CANDIDATE01"
    actual = df.hostname
    assert actual == expected


def test_blocks():
    expected = candidate_blocks()
    actual = df.blocks
    assert actual == expected


def test_ignore():
    ignore_file = open("../diffios_ignore").readlines()
    expected = [l.strip().lower() for l in ignore_file]
    actual = df.ignore()
    assert actual == expected


def test_partition():
    expected = candidate_partition()
    actual = df.partition()
    assert actual == expected
