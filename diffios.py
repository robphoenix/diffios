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


def ignore_list(ignore_file=None):
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


def compare(candidate, case):
    diff = {"plus": [], "minus": []}
    case_grp_head = [line[0] for line in case if len(line) > 1]
    cand_grp_head = [line[0] for line in candidate if len(line) > 1]
    for case_line in case:
        if len(case_line) == 1 and case_line not in candidate:
            diff["plus"].append(case_line)
        if len(case_line) > 1:
            first_line = case_line[0]
            if first_line in cand_grp_head:
                for cand_line in candidate:
                    if len(cand_line) > 1:
                        if case_line[0] == cand_line[0]:
                            plus = [case_line[0]]
                            minus = [cand_line[0]]
                            for case_grp_line in case_line:
                                if case_grp_line not in cand_line:
                                    plus.append(case_grp_line)
                            for cand_grp_line in cand_line:
                                if cand_grp_line not in case_line:
                                    minus.append(cand_grp_line)
                            if len(plus) > 1:
                                diff["plus"].append(plus)
                            if len(minus) > 1:
                                diff["minus"].append(minus)
            else:
                diff["plus"].append(case_line)
    for cand_line in candidate:
        if len(cand_line) == 1 and cand_line not in case:
            diff["minus"].append(cand_line)
        if len(cand_line) > 1:
            first_line = cand_line[0]
            if first_line in case_grp_head:
                for case_line in case:
                    if len(case_line) > 1:
                        if cand_line[0] == case_line[0]:
                            plus = [cand_line[0]]
                            minus = [case_line[0]]
                            for cand_grp_line in cand_line:
                                if cand_grp_line not in case_line:
                                    plus.append(cand_grp_line)
                            for case_grp_line in case_line:
                                if case_grp_line not in cand_line:
                                    minus.append(case_grp_line)
                            if len(plus) > 1:
                                diff["plus"].append(plus)
                            if len(minus) > 1:
                                diff["minus"].append(minus)
            else:
                diff["minus"].append(cand_line)
    return diff


candidate = context_list("./jon_candidate.conf")
case = context_list("./jon_cases/10.1.240.19.conf")

for line in candidate:
    print(line)

# diff = compare(candidate, case)
# pprint(diff)
