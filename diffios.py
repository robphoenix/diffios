import re
from pprint import pprint


IGNORE_FILE = "./diffios_ignore"


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
    return [elem.strip() for elem in open(ignore_file).readlines()]


def context_list(config_file, ignore_file=None):
    if not ignore_file:
        ignore_file = IGNORE_FILE
    ignored = []
    normalized = normalize(config_file)
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
    return [line for line in grouped if line]


def build_diff(a, b):
    diff_list = [line for line in a if len(line) == 1 and line not in b]
    groups_a = [line for line in a if len(line) > 1]
    groups_b = [line for line in b if len(line) > 1]
    head = [line[0] for line in groups_b]
    for a_group in groups_a:
        first_line = a_group[0]
        if first_line in head:
            for b_group in groups_b:
                if first_line == b_group[0]:
                    plus = [first_line]
                    for line in a_group:
                        if line not in b_group:
                            plus.append(line)
                    if len(plus) > 1:
                        diff_list.append(plus)
        else:
            diff_list.append(a_group)
    return diff_list


def compare(candidate, case):
    case_plus = build_diff(case, candidate)
    case_minus = build_diff(candidate, case)
    return {"plus": case_plus, "minus": case_minus}


candidate = context_list("./jon_candidate.conf")
case = context_list("./jon_cases/10.1.240.19.conf")

diff = compare(candidate, case)
pprint(diff)
