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


timestamp = datetime.datetime.now().isoformat().split(
        '.')[0].replace(':', '').replace('T', '-')
fout = 'diff-{0}.txt'.format(timestamp)

with open(fout, 'a') as output:
    for f in os.listdir("./cases"):
        case = os.path.join("./cases", f)
        hn = hostname(case)
        diff = difflib.context_diff(filelines(CANDIDATE), filelines(case))
        diff = list(diff)
        missing = '\n'.join(x[2:] for x in diff if x.startswith('- '))
        additional = '\n'.join(x[2:] for x in diff if x.startswith('+ '))
        title = "[ Host: {hn} ] {e:*<{w}}".format(
            hn=hn, e="", w=(79 - (len(hn) + 11)))
        minus = "\n-\n{0}".format(missing)
        plus = "\n+\n{0}\n".format(additional)
        res = "{0}{1}{2}".format(title, minus, plus)
        output.write(res)
        print(res)


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
