import re
import os
import csv
from pprint import pprint


IGNORE_FILE = "./diffios_ignore"
PARTIALS = [
    "^(?P<non_var> ip address )\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+",
    "^(?P<non_var> description ).+",
    "(?P<non_var>ip dhcp snooping vlan ).+",
    "(?P<non_var>ip default-gateway ).+",
    "(?P<non_var>switchport trunk allowed vlan ).+"
]


def remove_invalid_lines(config_file):
    data = open(config_file).readlines()
    return [line.rstrip() for line in data if valid_line(line)]


def valid_line(line):
    lstrip = line.strip()
    return len(lstrip) > 0 and not lstrip.startswith("!")


def group_into_blocks(conf_lines):
    previous, groups = [], []
    for i, line in enumerate(conf_lines):
        if line.startswith(" "):
            previous.append(line)
        else:
            groups.append(previous)
            previous = [line]
    return sorted(groups)[1:]


def lines_to_ignore(ignore_file):
    return [line.strip().lower() for line in open(ignore_file).readlines()]


def fetch_hostname(config_lines):
    for line in config_lines:
        if "hostname" in line.lower():
            return line.split()[1]


def partition_ignored_lines(config_file, ignore_file=None):
    if not ignore_file:
        ignore_file = IGNORE_FILE
    ignore = lines_to_ignore(ignore_file)
    config_blocks = group_into_blocks(remove_invalid_lines(config_file))
    ignored = []
    for i, block in enumerate(config_blocks):
        for j, line in enumerate(block):
            for line_to_ignore in ignore:
                if re.findall(line_to_ignore, line.lower()):
                    if j == 0:
                        ignored.append(config_blocks[i])
                        config_blocks[i] = []
                    else:
                        ignored.append(block[j])
                        block[j] = ""
    partitioned = {
        "ignored": ignored,
        "recorded": [line for line in config_blocks if line]
    }
    return partitioned


def clean_partials(group):
    cleaned, dirt = [], []
    for line in group:
        for pattern in PARTIALS:
            if re.search(pattern, line):
                dirt.append(line)
                line = re.search(pattern, line).group('non_var')
                break
        cleaned.append(line)
    return {"cleaned": cleaned, "dirt": dirt}


def find_changes(comparison, baseline):
    comparison_cleaned = [clean_partials(line)["cleaned"] for line in comparison if len(line)]
    baseline_cleaned = [clean_partials(line)["cleaned"] for line in baseline if len(line)]
    head = [line[0] for line in baseline_cleaned]
    changes = []
    for i, comparison_block in enumerate(comparison_cleaned):
        if len(comparison_block) == 1:
            if comparison_block not in baseline_cleaned:
                changes.append(comparison[i])
        else:
            first_line = comparison_block[0]
            if first_line in head:
                for baseline_block in baseline_cleaned:
                    if first_line == baseline_block[0]:
                        additional = [first_line]
                        for j, line in enumerate(comparison_block):
                            if line not in baseline_block:
                                additional.append(comparison[i][j])
                        if len(additional) > 1:
                            changes.append(additional)
            else:
                changes.append(comparison[i])
    return changes


def diff(candidate, case):
    additional = find_changes(case, candidate)
    missing = find_changes(candidate, case)
    return (additional, missing)


def diff_to_csv_format(changes):
    return ["\n".join(["\n".join(l) for l in c]) for c in changes]

anchor_directory = os.path.join(os.getcwd(), "anchor_small")
candidate_filename = "10.145.63.91.conf"
candidate_file = os.path.join(anchor_directory, candidate_filename)

partitioned_candidate_file = partition_ignored_lines(candidate_file)
candidate = partitioned_candidate_file['recorded']
candidate_ignored = partitioned_candidate_file['ignored']
candidate_hn = fetch_hostname(remove_invalid_lines(candidate_file))

with open("diffs.csv", 'a') as csvfile:
    csvwriter = csv.writer(csvfile, lineterminator='\n')
    csvwriter.writerow(["Case File", "Case Hostname", "Candidate File", "Additional", "Missing"])
    i = 1
    for fin in os.listdir(anchor_directory):
        print("{0}:\t{1}".format(i, fin))
        case_file = os.path.join(anchor_directory, fin)
        partitioned_case_file = partition_ignored_lines(case_file)
        case = partitioned_case_file['recorded']
        case_ignored = partitioned_case_file['ignored']
        case_hn = fetch_hostname(remove_invalid_lines(case_file))
        content = diff_to_csv_format(diff(candidate, case))
        csvwriter.writerow([fin, case_hn, candidate_filename] + content)
        i += 1
