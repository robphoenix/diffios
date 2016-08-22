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
    return contextual


c = context_list("./jon_candidate.conf")
for line in sorted(c):
    if len(line) == 1:
        pprint(line)


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
