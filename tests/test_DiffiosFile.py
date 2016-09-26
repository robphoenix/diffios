import os
import sys
sys.path.append(os.path.abspath("../diffios"))
from diffios import DiffiosFile


configs_dir = os.path.abspath("./configs/")
configs = sorted(os.path.join(configs_dir, f) for f in os.listdir(configs_dir))
dfs = [DiffiosFile(config) for config in configs]


def test_default_ignore_filename():
    expected = [os.path.abspath("../diffios_ignore") for x in range(len(dfs))]
    actual = [df.ignore_filename for df in dfs]
    assert actual == expected


def test_config_filename():
    actual = configs
    expected = [df.config_filename for df in dfs]
    assert actual == expected


def test_hostname():
    expected = [
        "CANDIDATE01",
        "CASE01",
    ]
    actual = [df.hostname() for df in dfs]
    assert actual == expected
