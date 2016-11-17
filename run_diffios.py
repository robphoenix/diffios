#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import progressbar

from diffios import DiffiosDiff

IGNORE_FILE = os.path.join(os.getcwd(), "priv", "diffios_ignore")
COMPARISON_DIR = os.path.join(os.getcwd(), "priv", "anchor")
BASELINE_FILENAME = "sm_sw_baseline.txt"
BASELINE_FILE = os.path.join(
    os.getcwd(), "priv", "anchor_baselines", BASELINE_FILENAME)
bar = progressbar.ProgressBar()

with open(os.path.join(os.getcwd(), "priv", "diffs.csv"), 'w') as csvfile:
    csvwriter = csv.writer(csvfile, lineterminator='\n')
    csvwriter.writerow([
        "Comparison File",
        "Comparison Hostname",
        "Baseline File",
        "Additional",
        "Missing"
    ])
    i = 1
    files = sorted(os.listdir(COMPARISON_DIR))
    for fin in bar(files):
        comparison_file = os.path.join(COMPARISON_DIR, fin)
        diff = DiffiosDiff(
            baseline=BASELINE_FILE,
            comparison=comparison_file,
            ignore_file=IGNORE_FILE
        )
        csvwriter.writerow([
            fin,
            diff.comparison.hostname,
            os.path.basename(BASELINE_FILE),
            diff.pprint_additional,
            diff.pprint_missing
        ])
        i += 1
