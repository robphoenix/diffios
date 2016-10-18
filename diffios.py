import re
import os
from collections import namedtuple
# import csv
# from pprint import pprint


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
            ignore_filename = os.path.abspath("diffios_ignore")
            # TODO: confirm presence of files
        self.ignore_filename = ignore_filename
        self.config_filename = os.path.abspath(config_filename)
        self.config_lines = self._file_lines(self.config_filename)
        self.blocks = self._group_into_blocks(self._remove_invalid_lines())
        self.hostname = self._hostname()

    def _file_lines(self, fin):
        with open(fin) as fl:
            return fl.readlines()

    def _remove_invalid_lines(self):
        return [l.rstrip() for l in self.config_lines if self._valid_line(l)]

    def _valid_line(self, line):
        lstrip = line.strip()
        return len(lstrip) > 0 and not lstrip.startswith("!")

    def _group_into_blocks(self, conf_lines):
        previous, groups = [], []
        for i, line in enumerate(conf_lines):
            if line.startswith(" "):
                previous.append(line)
            else:
                groups.append(previous)
                previous = [line]
        return sorted(groups)[1:]

    def _hostname(self):
        for line in self.config_lines:
            if "hostname" in line.lower():
                return line.split()[1]

    def ignore_lines(self):
        il = self._file_lines(self.ignore_filename)
        return [line.strip().lower() for line in il]

    def partition(self):
        Partition = namedtuple("Partition", "ignored recorded")
        ignore = self.ignore_lines()
        ignore_removed = self._remove_invalid_lines()
        config_blocks = self._group_into_blocks(ignore_removed)
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
        p = Partition(ignored, [line for line in config_blocks if line])
        return p

    def ignored(self):
        return self.partition().ignored

    def recorded(self):
        return self.partition().recorded


class DiffiosDiff(object):

    def __init__(self, baseline, comparison):
        # TODO: make it so DiffiosFile objects can be passed in also
        # TODO: confirm existence of files
        self.baseline = DiffiosFile(baseline)
        self.comparison = DiffiosFile(comparison)
        self.translated_comparison = self._translated(self.comparison)
        self.translated_baseline = self._translated(self.baseline)
        self.original_comparison = self._original(self.comparison)
        self.original_baseline = self._original(self.baseline)
        self.additional = self._find_changes(
            self.translated_comparison, self.translated_baseline)
        self.missing = self._find_changes(
            self.translated_baseline, self.translated_comparison)

    def _translate_partials(self, block):
        Partials = namedtuple("Partials", "translated originals")
        translated, original = [], [block[0]]
        for line in block:
            for pattern in PARTIALS:
                if re.search(pattern, line):
                    original.append(line)
                    line = re.search(pattern, line).group('non_var')
                    break
            translated.append(line)
        if len(original) == 1:
            original = ()
        if len(original) == 2:
            original = set(original)
        return Partials(translated, tuple(original))

    def _translated(self, df):
        return [self._translate_partials(b).translated for b in df.recorded()]

    def _original(self, df):
        originals = []
        for block in df.recorded():
            original = self._translate_partials(block).originals
            if original:
                originals.append(original)
        return originals

    def _find_changes(self, dynamic, static):
        head = [line[0] for line in static]
        changes = []
        for dynamic_index, dynamic_block in enumerate(dynamic):
            if len(dynamic_block) == 1:
                if dynamic_block not in static:
                    changes.append(dynamic[dynamic_index])
            else:
                first_line = dynamic_block[0]
                if first_line in head:
                    static_block = static[head.index(first_line)]
                    additional = [first_line]
                    for dynamic_block_index, line in enumerate(dynamic_block):
                        if line not in static_block:
                            additional.append(
                                dynamic[dynamic_index][dynamic_block_index])
                    if len(additional) > 1:
                        changes.append(additional)
                else:
                    changes.append(dynamic[dynamic_index])
        return sorted(changes)


# def diffios_diff_to_csv():
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
