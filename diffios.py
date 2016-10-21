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

    def __init__(self, baseline=None, comparison=None, ignore_file=None):
        # TODO: make it so DiffiosFile objects can be passed in also
        # TODO: confirm existence of files
        self.baseline = DiffiosFile(baseline, ignore_file)
        self.comparison = DiffiosFile(comparison, ignore_file)
        self.partials = PARTIALS
        self.additional = self._changes(
            self.comparison.recorded(), self.baseline.recorded())
        self.missing = self._changes(
            self.baseline.recorded(), self.comparison.recorded())

    def _translate_block(self, block):
        post_translation_block = []
        for i, line in enumerate(block):
            match = None
            for pattern in self.partials:
                if re.search(pattern, line):
                    match = re.search(pattern, line).group('non_var')
                    post_translation_block.append(match)
            if match is None:
                post_translation_block.append(line)
        return post_translation_block

    def _translated(self, data):
        return [self._translate_block(block) for block in data]

    def _changes(self, dynamic, static):
        translated_dynamic = self._translated(dynamic)
        translated_static = self._translated(static)
        head = [line[0] for line in static]
        changes = []
        for dynamic_index, dynamic_block in enumerate(translated_dynamic):
            if len(dynamic_block) == 1:
                if dynamic_block not in translated_static:
                    changes.append(dynamic[dynamic_index])
            else:
                first_line = dynamic_block[0]
                if first_line in head:
                    static_block = translated_static[head.index(first_line)]
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
