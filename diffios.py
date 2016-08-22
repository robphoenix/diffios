import os
import argparse
import datetime
from pprint import pprint


def filelines(fp):
    with open(fp, 'r') as f:
        fl = [line.rstrip() for line in f.readlines()]
    return fl


def hostname(f):
    fl = filelines(f)
    hn_lines = list(ln for ln in fl if 'hostname' in ln.lower())
    return hn_lines[0].split()[1]


def context_list(a):
    normalized_a, prev, context_a = [], [], []
    a = open(a).readlines()
    for line in a:
        if len(line) > 3:
            normalized_a.append(line.rstrip())
    for line in normalized_a:
        if line.startswith(" "):
            prev.append(line)
        else:
            context_a.append(prev)
            prev = [line]
    return context_a


pprint(context_list("./jon_candidate.conf"))


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
