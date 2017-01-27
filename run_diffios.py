#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv

from diffios import Diffios

IGNORE_FILE = os.path.join(os.getcwd(), "priv", "diffios_ignore")
COMPARISON_DIR = os.path.join(os.getcwd(), "priv", "anchor")
BASELINE_FILENAME = "sm_sw_baseline.txt"
BASELINE_FILE = os.path.join(
    os.getcwd(), "priv", "anchor_baselines", BASELINE_FILENAME)

with open(os.path.join(os.getcwd(), "priv", "diffs.csv"), 'w') as csvfile:
    csvwriter = csv.writer(csvfile, lineterminator='\n')
    csvwriter.writerow(["Comparison", "Baseline", "Additional", "Missing"])
    files = sorted(os.listdir(COMPARISON_DIR))
    for fin in files:
        print("Processing: ", fin)
        comparison_file = os.path.join(COMPARISON_DIR, fin)
        diff = Diffios(BASELINE_FILE, comparison_file, IGNORE_FILE)
        csvwriter.writerow([
            fin,
            os.path.basename(BASELINE_FILE),
            diff.pprint_additional(),
            diff.pprint_missing()
        ])
