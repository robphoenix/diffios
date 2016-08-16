import os
import argparse
import datetime
import difflib

CANDIDATE = "./candidate.txt"


def filelines(fp):
    with open(fp, 'r') as f:
        fl = [line.rstrip() for line in f.readlines()]
    return fl


def hostname(f):
    fl = filelines(f)
    hn_lines = list(ln for ln in fl if 'hostname' in ln.lower())
    return hn_lines[0].split()[1]


now = datetime.datetime.now().isoformat().split(
        '.')[0].replace(':', '').replace('T', '-')
fout = 'diff-{0}.txt'.format(now)
with open(fout, 'a') as output:
    for f in os.listdir("./cases"):
        case = os.path.join("./cases", f)
        hn = hostname(case)
        diff = difflib.context_diff(filelines(CANDIDATE), filelines(case))
        diff = list(diff)
        missing = '\n'.join(x[2:] for x in diff if x.startswith('- '))
        additional = '\n'.join(x[2:] for x in diff if x.startswith('+ '))
        h = "[Host: {0}]".format(hn)
        output.write(h + " " + ("*" * (79 - len(h))))
        print(h + " " + ("*" * (79 - len(h))))
        output.write("\n-\n")
        print("\n-\n")
        output.write(missing)
        print(missing)
        output.write("\n+\n")
        print("\n+\n")
        output.write(additional)
        print(additional)
        output.write("\n\n")
        print("\n")


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
