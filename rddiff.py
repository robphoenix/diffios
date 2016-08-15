import os
import argparse
import datetime
import re


CANDIDATE = "./candidate.txt"
IGNORE = "./ignores.txt"


def filelines(fp):
    with open(fp, 'r') as f:
        return [line.rstrip() for line in f.readlines()]


def hostname(fl):
    fl = filelines(fl)
    hn_lines = list(ln for ln in fl if 'hostname' in ln.lower())
    return hn_lines[0].split()[1]


def ignored(ig=IGNORE):
    ig = filelines(ig)
    res = [re.compile(pattern) for pattern in ig]
    return res


def normalize(f):
    f = filelines(f)
    f = [line for line in f if not line.startswith("!")]
    for line in f:
        for i in ignored():
            if i.match(line):
                f.remove(line)
    return f



def compare(base, case):
    base = normalize(base)
    case = normalize(case)
    missing = [line for line in base if line not in case]
    extra = [line for line in case if line not in base]
    res = '[missing]\n\n{0}\n\n[additional]\n\n{1}\n'.format(
        '\n'.join(missing), '\n'.join(extra))
    return res


def append_to_file(content):
    now = datetime.datetime.now().isoformat().split(
        '.')[0].replace(':', '').replace('T', '-')
    f = 'output-{0}.txt'.format(now)
    with open(f, 'a') as output:
        output.write(content)


for f in os.listdir("./cases"):
    case = os.path.join("./cases", f)
    diff = compare(CANDIDATE, case)
    append_to_file('[{0}] {1}\n\n{2}\n'.format(hostname(case), '*' * 50, diff))


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
