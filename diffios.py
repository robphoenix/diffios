#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

    """TODO: Docstring for DiffiosFile. """

    def __init__(self, config_filename, ignore_filename=None):
        """TODO: Docstring for __init__.

        Args:
            config_filename (TODO): TODO

        Kwargs:
            ignore_filename (TODO): TODO

        Returns: TODO

        """
        if ignore_filename is None:
            ignore_filename = os.path.abspath("diffios_ignore")
            # TODO: confirm presence of files
        self.ignore_filename = ignore_filename
        self.config_filename = os.path.abspath(config_filename)
        self.config_lines = self._file_lines(self.config_filename)
        self.blocks = self._group_into_blocks(self._remove_invalid_lines())
        self.hostname = self._hostname()

    def _file_lines(self, fin):
        """TODO: Docstring for _file_lines.

        Args:
            fin (TODO): TODO

        Returns: TODO

        """
        with open(fin) as fl:
            return fl.readlines()

    def _remove_invalid_lines(self):
        """TODO: Docstring for _remove_invalid_lines.

        Returns: TODO

        """
        return [l.rstrip() for l in self.config_lines if self._valid_line(l)]

    def _valid_line(self, line):
        """TODO: Docstring for .

        Returns: TODO

        """
        lstrip = line.strip()
        return len(lstrip) > 0 and not lstrip.startswith("!")

    def _group_into_blocks(self, conf_lines):
        """TODO: Docstring for _group_into_blocks.

        Args:
            conf_lines (TODO): TODO

        Returns: TODO

        """
        previous, groups = [], []
        for i, line in enumerate(conf_lines):
            if line.startswith(" "):
                previous.append(line)
            else:
                groups.append(previous)
                previous = [line]
        return sorted(groups)[1:]

    def _hostname(self):
        """TODO: Docstring for _hostname.

        Returns: TODO

        """
        for line in self.config_lines:
            if "hostname" in line.lower():
                return line.split()[1]

    def ignore_lines(self):
        """TODO: Docstring for ignore_lines.

        Returns: TODO

        """
        il = self._file_lines(self.ignore_filename)
        return [line.strip().lower() for line in il]

    def partition(self):
        """TODO: Docstring for partition.

        Returns: TODO

        """
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
        """TODO: Docstring for ignored.

        Returns: TODO

        """
        return self.partition().ignored

    def recorded(self):
        """TODO: Docstring for recorded.

        Returns: TODO

        """
        return self.partition().recorded


class DiffiosDiff(object):

    """Docstring for DiffiosDiff. """

    def __init__(self, baseline=None, comparison=None, ignore_file=None):
        """TODO: Docstring for __init__.

        Kwargs:
            baseline (TODO): TODO
            comparison (TODO): TODO
            ignore_file (TODO): TODO

        """
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
        """TODO: Docstring for _translate_block.

        Args:
            block (TODO): TODO

        Returns: TODO

        """
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
        """TODO: Docstring for _translated.

        Args:
            data (TODO): TODO

        Returns: TODO

        """
        return [self._translate_block(block) for block in data]

    def _changes(self, dynamic, static):
        """TODO: Docstring for _changes.

        Args:
            dynamic (TODO): TODO
            static (TODO): TODO

        Returns: TODO

        """
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

    def _format_changes(self, data):
        """TODO: Docstring for _format_changes.

        Args:
            data (TODO): TODO

        Returns: TODO

        """
        return "\n\n".join("\n".join(lines) for lines in data)

    def pprint_additional(self):
        return self._format_changes(self.additional)

    def pprint_missing(self):
        return self._format_changes(self.missing)

    def diff(self):
        """TODO: Docstring for diff.

        Returns: TODO

        """
        print("\nComparing {comparison} against baseline: {baseline}".format(
            comparison=os.path.basename(self.comparison.config_filename),
            baseline=os.path.basename(self.baseline.config_filename)
        ))
        print("\n[+] additional [+]\n")
        print("{}".format(self.pprint_additional()))
        print("\n[-] missing [-]\n")
        print("{}".format(self.pprint_missing()))
        print("\n--- END ---\n")
