import os
import csv

from diffios import DiffiosDiff

IGNORE_FILE = os.path.join(os.getcwd(), "priv", "diffios_ignore")
COMPARISON_DIR = os.path.join(os.getcwd(), "priv", "anchor")
BASELINE_FILENAME = "sm_sw_baseline.txt"
BASELINE_FILE = os.path.join(os.getcwd(), "priv", "anchor_baselines", BASELINE_FILENAME)

with open(os.path.join(os.getcwd(), "priv", "diffs.csv"), 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow([
        "Comparison File",
        "Comparison Hostname",
        "Baseline File",
        "Additional",
        "Missing"
    ])
    i = 1
    for fin in os.listdir(COMPARISON_DIR):
        comparison_file = os.path.join(COMPARISON_DIR, fin)
        diff = DiffiosDiff(
            baseline=BASELINE_FILE,
            comparison=comparison_file,
            ignore_file=IGNORE_FILE
        )
        print("{0}: Comparing {1} against {2}".format(
            i, fin, os.path.basename(diff.baseline.config_filename)))
        csvwriter.writerow([
            os.path.basename(diff.comparison.config_filename),
            diff.comparison.hostname,
            os.path.basename(diff.baseline.config_filename),
            "\n\n".join("\n".join(lines) for lines in diff.additional),
            "\n\n".join("\n".join(lines) for lines in diff.missing)
        ])
        i += 1
