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


def normalize(config_file):
    data = open(config_file).readlines()
    return [line.rstrip() for line in data if valid_line(line)]


def valid_line(line):
    line = line.strip()
    return len(line) > 0 and not line.startswith("!")


def group(conf):
    prev, grouped = [], []
    for line in conf:
        if line.startswith(" "):
            prev.append(line)
        else:
            grouped.append(prev)
            prev = [line]
    return sorted(grouped)[1:]


def ignore_list(ignore_file):
    return [elem.strip().lower() for elem in open(ignore_file).readlines()]


def context_list(config_file, ignore_file=None):
    if not ignore_file:
        ignore_file = IGNORE_FILE
    ignored = []
    normalized = normalize(config_file)
    for line in normalized:
        if "hostname" in line.lower():
            hostname = line.split()[1]
            break
    to_ignore = ignore_list(ignore_file)
    grouped = group(normalized)
    for group_index, grp in enumerate(grouped):
        for line_index, line in enumerate(grp):
            for ignore in to_ignore:
                if re.findall(ignore, line.lower()):
                    if line_index == 0:
                        ignored.append(grouped[group_index])
                        grouped[group_index] = []
                    else:
                        ignored.append(grp[line_index])
                        grp[line_index] = ""
    return (hostname, [line for line in grouped if line])


def sanitise_variables(group):
    sanitised = []
    for line in group:
        for pattern in PARTIALS:
            if re.search(pattern, line):
                line = re.search(pattern, line).group('non_var')
        sanitised.append(line)
    return sanitised


def build_diff(a, b):
    san_a = [sanitise_variables(line) for line in a if len(line) == 1]
    san_b = [sanitise_variables(line) for line in b if len(line) == 1]
    single_a = [line for line in a if len(line) == 1]
    diff_list = []
    for index, line in enumerate(san_a):
        if line not in san_b:
            diff_list.append(single_a[index])
    groups_a = [line for line in a if len(line) > 1]
    groups_b = [line for line in b if len(line) > 1]
    head = [line[0] for line in groups_b]
    for a_group in groups_a:
        first_line = a_group[0]
        if first_line in head:
            for b_group in groups_b:
                if first_line == b_group[0]:
                    plus = [first_line]
                    sanitised_a = sanitise_variables(a_group)
                    sanitised_b = sanitise_variables(b_group)
                    for index, line in enumerate(sanitised_a):
                        if line not in sanitised_b:
                            plus.append(a_group[index])
                    if len(plus) > 1:
                        diff_list.append(plus)
        else:
            sanitised_groups_b = [sanitise_variables(line) for line in groups_b]
            head = [line[0] for line in sanitised_groups_b]
            diff_list.append(a_group)
    return diff_list


def diff(candidate, case):
    case_plus = build_diff(case, candidate)
    case_minus = build_diff(candidate, case)
    return (case_plus, case_minus)


def diff_to_csv(tup):
    return ["\n".join(["\n".join(el) for el in liszt]) for liszt in tup]

anchor_directory = os.path.join(os.getcwd(), "anchor")
candidate_file = "10.145.63.91.conf"

(candidate_hn, candidate) = context_list(os.path.join(anchor_directory, candidate_file))

with open("diffs.csv", 'a') as csvfile:
    csvwriter = csv.writer(csvfile, lineterminator='\n')
    csvwriter.writerow(["Case File", "Case Hostname", "Candidate File", "Additional", "Missing"])
    i = 1
    for fin in os.listdir(anchor_directory):
        print("{0}:\t{1}".format(i, fin))
        fn = os.path.join(anchor_directory, fin)
        (case_hn, case) = context_list(fn)
        content = diff_to_csv(diff(candidate, case))
        csvwriter.writerow([fin, case_hn, candidate_file] + content)
        i += 1
