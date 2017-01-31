#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import diffios

IGNORE_FILE = os.path.join(os.getcwd(), "ignores.txt")
COMPARISON_DIR = os.path.join(os.getcwd(), "configs", "comparisons")
BASELINE_FILE = os.path.join(
    os.getcwd(), "configs", "baselines", "baseline.txt")

output = os.path.join(os.getcwd(), "diffs.csv")

with open(output, 'w') as csvfile:
    csvwriter = csv.writer(csvfile, lineterminator='\n')
    csvwriter.writerow(["Comparison", "Baseline", "Additional", "Missing"])
    files = sorted(os.listdir(COMPARISON_DIR))
    num_files = len(files)
    for i, fin in enumerate(files):
        #  print("diffios: {:>3}/{} Processing: {}".format(i, num_files, fin),
        #        end="\r")
        comparison_file = os.path.join(COMPARISON_DIR, fin)
        diff = diffios.Compare(BASELINE_FILE, comparison_file, IGNORE_FILE)
        csvwriter.writerow([
            fin,
            os.path.basename(BASELINE_FILE),
            diff.pprint_additional(),
            diff.pprint_missing()
        ])
        print(diff.delta())
    print("diffios: Report: {}".format(output))
