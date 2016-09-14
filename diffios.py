import re
from pprint import pprint


IGNORE_FILE = "./diffios_ignore"
PARTIALS = [
    "^(?P<non_var> ip address )\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+",
    "^(?P<non_var> description ).+",
    "(?P<non_var>ip dhcp snooping vlan ).+"
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
    return {"plus": case_plus, "minus": case_minus}


def similarity(first, second):
    join_plus = ["\n".join(elem) for elem in first]
    join_minus = ["\n".join(elem) for elem in second]
    split_plus = [elem.split() for elem in join_plus]
    split_minus = [elem.split() for elem in join_minus]
    amber = []
    red = []
    for i, p in enumerate(split_plus):
        high_score = 0
        lines = None
        for j, m in enumerate(split_minus):
            zipped = list(zip(p, m))
            same = [(a, b) for (a, b) in zipped if a == b]
            discontiguous_score = float(len(same)) / float(len(zipped))
            contiguous_score = 0
            for (a, b) in zipped:
                if a == b:
                    contiguous_score += 1
                else:
                    break
            score = discontiguous_score + contiguous_score
            if score >= high_score:
                high_score = score
                if score == 0:
                    lines = (first[i], [])
                else:
                    lines = (score, first[i], second[j])
        if lines[-1] == []:
            red.append(lines)
        else:
            amber.append(lines)
    cleaned_amber = []
    extras = []
    for el1 in amber:
        for el2 in amber:
            if el1 != el2 and el1[2] == el2[2]:
                amber.remove(el1)
                amber.remove(el2)
                if el1[0] > el2[0]:
                    cleaned_amber.append(tuple(el1[1:]))
                    extras.append(tuple(el2[1:]))
                else:
                    cleaned_amber.append(tuple(el2[1:]))
                    extras.append(tuple(el1[1:]))
    amber = [(b, c) for (_, b, c) in amber] + cleaned_amber
    red = red + [(a, []) for (a, _) in extras]
    return (amber, red)


candidate = context_list("./jon_candidate.conf")
case = context_list("./jon_cases/10.1.240.19.conf")

d = diff(candidate, case)
(diff_case, additional) = similarity(d["plus"], d["minus"])
(diff_cand, missing) = similarity(d["minus"], d["plus"])
# pprint(additional)
# pprint(missing)
# pprint(sorted(diff_case))
# pprint(sorted(diff_cand))
# s = []
# for el in sorted(diff_cand):
    # s.append(el[::-1])
# print(sorted(diff_case) == s)
# pprint(list(zip(diff_case, diff_cand)))

print("missing:")
pprint(missing)
print("\n")
print("additional:")
pprint(additional)
print("\n")
print("similar:")
pprint(diff_case)
