from pprint import pprint


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
    # this needs recursion yo
    diff = {"plus": [], "minus": []}
    for i in case:
        if len(i) == 1:
            if i not in candidate:
                diff["plus"].append(i)
        if len(i) > 1:
            for j in candidate:
                if len(j) > 1:
                    if i[0] == j[0]:
                        plus = [i[0]]
                        minus = [j[0]]
                        for k in i[1:]:
                            if k not in j[1:]:
                                plus.append(k)
                        for l in j[1:]:
                            if l not in i[1:]:
                                minus.append(l)
                        if len(plus) > 1:
                            diff["plus"].append(plus)
                        if len(minus) > 1:
                            diff["minus"].append(minus)
    for line in candidate:
        if len(line) == 1:
            if line not in case:
                diff["minus"].append(line)
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
