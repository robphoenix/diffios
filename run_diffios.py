#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv

from diffios import DiffiosDiff

IGNORE_FILE = os.path.join(os.getcwd(), "priv", "diffios_ignore")
COMPARISON_DIR = os.path.join(os.getcwd(), "priv", "anchor")
BASELINE_FILENAME = "sm_sw_baseline.txt"
BASELINE_FILE = os.path.join(os.getcwd(), "priv", "anchor_baselines", BASELINE_FILENAME)

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
    for fin in files:
        comparison_file = os.path.join(COMPARISON_DIR, fin)
        diff = DiffiosDiff(
            baseline=BASELINE_FILE,
            comparison=comparison_file,
            ignore_file=IGNORE_FILE
        )
        print("{0} of {1}: {2} => {3}".format(
            i, len(files), fin, os.path.basename(diff.baseline.config_filename)))
        csvwriter.writerow([
            os.path.basename(diff.comparison.config_filename),
            diff.comparison.hostname,
            os.path.basename(diff.baseline.config_filename),
            diff.pprint_additional(),
            diff.pprint_missing()
        ])
        i += 1
