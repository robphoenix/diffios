import re
import os
import csv
from pprint import pprint


PARTIALS = [
    "^(?P<non_var> ip address )\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+",
    "^(?P<non_var> description ).+",
    "(?P<non_var>ip dhcp snooping vlan ).+",
    "(?P<non_var>ip default-gateway ).+",
    "(?P<non_var>switchport trunk allowed vlan ).+"
]


class DiffiosFile(object):

    def __init__(self, config_filename, ignore_filename=None):
        if ignore_filename is None:
            ignore_filename = os.path.abspath("../diffios_ignore")
        self.ignore_filename = ignore_filename
        self.config_filename = os.path.abspath(config_filename)
        self.config_lines = self._file_lines(self.config_filename)

    def _file_lines(self, fin):
        with open(fin) as cf:
            return cf.readlines()

    def _remove_invalid_lines(self):
        return [l.rstrip() for l in self.config_lines if self._valid_line(l)]

    def _valid_line(self, line):
        lstrip = line.strip()
        return len(lstrip) > 0 and not lstrip.startswith("!")

    def group_into_blocks(self, conf_lines):
        previous, groups = [], []
        for i, line in enumerate(conf_lines):
            if line.startswith(" "):
                previous.append(line)
            else:
                groups.append(previous)
                previous = [line]
        return sorted(groups)[1:]

    def lines_to_ignore(self):
        ignore_lines = self._file_lines(self.ignore_filename)
        return [line.strip().lower() for line in ignore_lines]

    def hostname(self):
        for line in self.config_lines:
            if "hostname" in line.lower():
                return line.split()[1]

    def partition_ignored_lines(self):
        ignore = self.lines_to_ignore()
        ignored_removed = self._remove_invalid_lines()
        config_blocks = self.group_into_blocks(ignored_removed)
        ignored = []
        for i, block in enumerate(config_blocks):
            for j, line in enumerate(block):
                for line_to_ignore in ignore:
                    if re.findall(line_to_ignore, line.lower()):
                        if j == 0:
                            ignored.append(config_blocks[i])
                            config_blocks[i] = []
                        else:
                            ignored.append(block[j])
                            block[j] = ""
        partitioned = {
            "ignored": ignored,
            "recorded": [line for line in config_blocks if line]
        }
        return partitioned

    def ignored_lines(self):
        return self.partition_ignored_lines()["ignored"]

    def recorded_lines(self):
        return self.partition_ignored_lines()["recorded"]


# class DiffiosDiff(object):

    # def __init__(self, baseline_file, comparison_file):
        # self.config_file = config_file
        # self.ignore_file = ignore_file

    # def clean_partials(group):
        # cleaned, dirt = [], []
        # for line in group:
            # for pattern in PARTIALS:
                # if re.search(pattern, line):
                    # dirt.append(line)
                    # line = re.search(pattern, line).group('non_var')
                    # break
            # cleaned.append(line)
        # return {"cleaned": cleaned, "dirt": dirt}

    # def find_changes(comparison, baseline):
        # comparison_cleaned = [clean_partials(l)["cleaned"] for l in comparison if len(l)]
        # baseline_cleaned = [clean_partials(l)["cleaned"] for l in baseline if len(l)]
        # head = [line[0] for line in baseline_cleaned]
        # changes = []
        # for i, comparison_block in enumerate(comparison_cleaned):
            # if len(comparison_block) == 1:
                # if comparison_block not in baseline_cleaned:
                    # changes.append(comparison[i])
            # else:
                # first_line = comparison_block[0]
                # if first_line in head:
                    # baseline_block = baseline_cleaned[head.index(first_line)]
                    # additional = [first_line]
                    # for j, line in enumerate(comparison_block):
                        # if line not in baseline_block:
                            # additional.append(comparison[i][j])
                    # if len(additional) > 1:
                        # changes.append(additional)
                # else:
                    # changes.append(comparison[i])
        # return sorted(changes)


    # def diff(candidate, case):
        # additional = find_changes(case, candidate)
        # missing = find_changes(candidate, case)
        # return (additional, missing)


    # def diff_to_csv_format(changes):
        # return ["\n".join(["\n".join(l) for l in c]) for c in changes]






# anchor_directory = os.path.join(os.getcwd(), "anchor")
# candidate_filename = "10.145.63.91.conf"
# candidate_file = os.path.join(anchor_directory, candidate_filename)

# partitioned_candidate_file = partition_ignored_lines(candidate_file)
# candidate = partitioned_candidate_file['recorded']
# candidate_ignored = partitioned_candidate_file['ignored']
# candidate_hn = fetch_hostname(remove_invalid_lines(candidate_file))

# with open("diffs.csv", 'a') as csvfile:
    # csvwriter = csv.writer(csvfile, lineterminator='\n')
    # csvwriter.writerow([
        # "Case File", "Case Hostname", "Candidate File", "Additional", "Missing"
    # ])
    # i = 1
    # for fin in os.listdir(anchor_directory):
        # print("{0}:\t{1}".format(i, fin))
        # case_file = os.path.join(anchor_directory, fin)
        # partitioned_case_file = partition_ignored_lines(case_file)
        # case = partitioned_case_file['recorded']
        # case_ignored = partitioned_case_file['ignored']
        # case_hn = fetch_hostname(remove_invalid_lines(case_file))
        # content = diff_to_csv_format(diff(candidate, case))
        # csvwriter.writerow([fin, case_hn, candidate_filename] + content)
        # i += 1
