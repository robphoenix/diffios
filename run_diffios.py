import os
import csv

from diffios import DiffiosFile
from diffios import DiffiosDiff

comparison_dir = os.path.join(os.getcwd(), "priv", "jon_comparison")
baseline_filename = "jon_baseline.conf"
baseline_file = os.path.join(os.getcwd(), "priv", baseline_filename)
baseline_diff_file = DiffiosFile(baseline_file)

with open(os.path.join(os.getcwd(), "priv", "diffs.csv"), 'a') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow([
        "Comparison File",
        "Comparison Hostname",
        "Baseline File",
        "Additional",
        "Missing"
    ])
    i = 1
    for fin in os.listdir(comparison_dir):
        print("{0}: Comparing {1} against {2}".format(
            i, fin, os.path.basename(baseline_diff_file.config_filename)))
        comparison_file = os.path.join(comparison_dir, fin)
        comparison_diff_file = DiffiosFile(comparison_file)
        diff = DiffiosDiff(baseline=baseline_file, comparison=comparison_file)
        csvwriter.writerow([
            os.path.basename(comparison_diff_file.config_filename),
            comparison_diff_file.hostname,
            os.path.basename(baseline_diff_file.config_filename),
            "\n\n".join("\n".join(lines) for lines in diff.additional),
            "\n\n".join("\n".join(lines) for lines in diff.missing)
        ])
        i += 1
