#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from diffios import DiffiosDir

IGNORE_FILE = os.path.join(os.getcwd(), "priv", "diffios_ignore")
COMPARISON_DIR = os.path.join(os.getcwd(), "priv", "anchor")
BASELINE_FILENAME = "sm_sw_baseline.txt"
BASELINE_FILE = os.path.join(
    os.getcwd(), "priv", "anchor_baselines", BASELINE_FILENAME)

diffs = DiffiosDir(BASELINE_FILE, COMPARISON_DIR, IGNORE_FILE)
for diff in diffs.diffs():
    print(diff.compare())
