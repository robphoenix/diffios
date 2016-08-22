import re
from pprint import pprint


IGNORE = "./diffios_ignore"


def ignored(ig=IGNORE):
    ig = open(ig).readlines()
    res = [re.compile(pattern) for pattern in ig]
    return res


def context_list(config_file):
    normalize, prev, contextual = [], [], []
    config_file = open(config_file).readlines()
    for line in config_file:
        if not line.startswith("!") and len(line) > 1:
            normalize.append(line.rstrip())
    for line in normalize:
        if line.startswith(" "):
            prev.append(line)
        else:
            contextual.append(prev)
            prev = [line]
    return sorted(contextual)


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

diff = compare(candidate, case)
pprint(diff)

# def main():

#     parser = argparse.ArgumentParser(
#     prog="cscodiff",
#     description="""
#         list differences between multiple Cisco configuration files
#         and a base Cisco configuration file.
#         """,
#     formatter_class=argparse.RawDescriptionHelpFormatter,
#     epilog="""
#         TODO: add epic description
#   	""")
#     parser.add_argument("base_file",
#                         help="Specify the base configuration file you are comparing against")
#     parser.add_argument("comparison_files",
#                         help="Specify the directory containing the Cisco configuration files you want to compare against the base file")
#     #  group = parser.add_mutually_exclusive_group()
#     #  group.add_argument("--csv", help="Output results as CSV file", action="store_true")
#     args = parser.parse_args()


#     base = filelines(args.base_file)
#     for f in os.listdir(args.comparison_files):
#         case = filelines(os.path.join(args.comparison_files, f))
#         diff = compare(base, case)
#         append_to_file('[{0}] {1}\n\n{2}\n'.format(hostname(case), '*' * 50, diff))


# if __name__ == '__main__':
#     main()
