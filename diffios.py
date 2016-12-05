#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
from collections import namedtuple
from itertools import product

DELIMITER = r'{{[^{}]+}}'


class DiffiosConfig(object):

    """DiffiosConfig prepares a Cisco IOS Config to diff.

    DiffiosConfig takes a Cisco IOS config, as a file or a
    list, extracts the device hostname, removes any invalid
    lines, such as comments, breaks the config into a
    hierarchical block structure and partitions the config
    according to a list of lines to ignore.

    Attributes:
        ignores (list): List of lines to ignore
        config (list): List of valid config lines

    Args:
        config (str|list): Path to config file, or list
            containing lines of config

    Kwargs:
        ignores (str|list): Path to ignores file, or list
            containing lines to ignore. Defaults to ignores
            file in current working directory.

    >>> config = [
    ... '!',
    ... 'hostname ROUTER',
    ... '!',
    ... 'interface FastEthernet0/1',
    ... ' description **Link to Core**',
    ... ' ip address 192.168.0.1 255.255.255.0']
    >>> ignores = [
    ... 'hostname',
    ... '^ description']
    >>> conf = DiffiosConfig(config, ignores=ignores)
    >>> conf.config
    ['hostname ROUTER', \
'interface FastEthernet0/1', \
' description **Link to Core**', \
' ip address 192.168.0.1 255.255.255.0']
    >>> conf.ignores
    ['hostname', '^ description']
    >>> conf.config_blocks
    [['hostname ROUTER'], \
['interface FastEthernet0/1', \
' description **Link to Core**', \
' ip address 192.168.0.1 255.255.255.0']]
    >>> conf.ignored
    [['hostname ROUTER'], [' description **Link to Core**']]
    >>> conf.recorded
    [['interface FastEthernet0/1', \
' ip address 192.168.0.1 255.255.255.0']]

    """

    def __init__(self, config, ignore_lines=None):
        if ignore_lines is None and os.path.exists(os.path.join(os.getcwd(), 'diffios_ignore')):
            ignore_lines = os.path.join(os.getcwd(), "diffios_ignore")
        elif ignore_lines is None:
            ignore_lines = []
        self.config = self._check_data(config)
        self.ignore_lines = self._check_data(ignore_lines)

    def _valid_config(self):
        valid = [l.rstrip() for l in self.config if self._valid_line(l)]
        return valid

    def _group_config(self):
        """Group config into hierarchical groups.

        Groups are defined as a parent/child relationship,
        where children lines start with a ' ', and parents
        are the immediately preceding line that doesn't start
        with a ' '. Blocks can be single lines where there
        is no children. Returns the groups sorted.

        Example Groups:
            interface FastEthernet0/1
             ip address 192.168.0.1 255.255.255.0
             no shutdown

            hostname ROUTER

        Args:
            config (list): config as a list of lines.

        Returns:
            list: config as a sorted list of lists, each list
                representing a hierarchical block of config.

        """
        current_group, groups = [], []
        for line in self._valid_config():
            if not line.startswith(' ') and current_group:
                groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)
        if current_group:
            groups.append(current_group)
        return sorted(groups)

    def _partition_group(self, group):
        """Check for any lines to be ignored in a given group.
        Args:
            group (list): A single hierarchical group of config
        Returns:
            tuple: ignored and recorded (not ignored) lines in group
        """
        Partition = namedtuple("Partition", "ignored included")
        ignored, included = [], []
        for i, line in enumerate(group):
            if self._ignore_line(line) and i == 0:
                return Partition(group, included)
            elif self._ignore_line(line):
                ignored.append(line)
            else:
                included.append(line)
        return Partition(ignored, included)

    def _partition_config(self):
        Partition = namedtuple("Partition", "ignored included")
        included, ignored = [], []
        for group in self._group_config():
            partition = self._partition_group(group)
            if partition.included:
                included.append(partition.included)
            if partition.ignored:
                ignored.append(partition.ignored)
        return Partition(ignored, included)

    def included(self):
        return self._partition_config().included

    def ignored(self):
        return self._partition_config().ignored

    @property
    def hostname(self):
        """The hostname of the given config.

        Returns:
            str: hostname of the given config
                or None if not found.

        """
        for line in self.config:
            if "hostname" in line.lower():
                return line.split()[1]
        return None

    def ignore(self):
        """Transforms given ignores data into usable format.

        Args:
            ignores (list|file): ignores as either list or file.

        Returns:
            list: Lines to ignore.

        """
        ignore = [line.strip().lower() for line in self.ignore_lines]
        return ignore

    @staticmethod
    def _check_data(data):
        """Check type of data and convert it if necessary.

        Args:
            data (list|file): input data as either list or file.

        Returns:
            list: The input data as a list.

        Raises:
            RuntimeError: If file cannot be opened or given data
                is not a list or file.

        """
        invalid_arg = "DiffiosConfig() received an invalid argument: config={}\n"
        unable_to_open = "DiffiosConfig() could not open '{}'"
        if isinstance(data, list):
            return data
        elif os.path.isfile(data):
            try:
                with open(data) as fin:
                    return fin.readlines()
            except IOError:
                raise RuntimeError((unable_to_open.format(data)))
        else:
            raise RuntimeError(invalid_arg.format(data))

    @staticmethod
    def _valid_line(line):
        """Assert whether a given line is valid.

        Lines considered invalid are those which are empty
        or begin with a '!' to indicate a comment.

        Args:
            line (str): A single line from a config.

        Returns:
            bool: True if line is valid, False if not.

        """
        line = line.strip()
        return len(line) > 0 and not line.startswith("!") and line != '^' and line != '^C'

    def _ignore_line(self, line):
        """Check if a line should be ignored.

        Args:
            line (str): line to check

        Returns:
            bool: True if line should be ignored,
                False otherwise.

        """
        for line_to_ignore in self.ignore_lines:
            if re.search(line_to_ignore, line.lower()):
                return True
        return False


class DiffiosDiff(object):

    """Docstring for DiffiosDiff. """

    def __init__(self, baseline=None, comparison=None, ignore_file=None):
        """TODO: Docstring for __init__.

        Kwargs:
            baseline (TODO): TODO
            comparison (TODO): TODO
            ignore_file (TODO): TODO

        """
        self.baseline = DiffiosConfig(baseline, ignore_file)
        self.comparison = DiffiosConfig(comparison, ignore_file)
        self.delimiter = DELIMITER

    def _baseline_var_blocks(self):
        var_blocks = []
        for block in self.baseline.recorded:
            for line in block:
                if re.search(self.delimiter, line):
                    var_blocks.append(block)
        return var_blocks

    @staticmethod
    def _check_lines(xline, yline):
        """TODO: Docstring for _check_lines.

        Args:
            xline (TODO): TODO
            yline (TODO): TODO

        Returns: TODO

        """
        re_metacharacters = ['*', '.']
        for char in re_metacharacters:
            if char in xline:
                xline = xline.replace(char, '\{}'.format(char))
        print(xline)
        xline_re = re.sub(r'{{[^{}]+}}', '(.+)', xline)
        match = re.search(xline_re, yline)
        if match:
            return match.group(0) == yline
        else:
            return False

    def _translate_comparison(self):
        d = self.delimiter
        prod = product(self._baseline_var_blocks(), self.comparison.recorded)
        filter_prod = [(x, y) for (x, y) in prod if d[0] in ''.join(x) or d[0] in ''.join(y)]
        similar = [(x, y) for (x, y) in filter_prod if x[0].split()[0] == y[0].split()[0]]
        more_similar = []
        # We need to ensure that if the parent line in a block is
        # not a variable line, that the parents of the x & y blocks
        # match fully, otherwise we get issues where different blocks
        # are matched up together as they have the same first word
        # in their parents.
        for x, y in similar:
            if d[0] not in x[0] and d[0] not in y[0] and x[0] == y[0]:
                more_similar.append((x, y))
            elif d[0] in x[0] or d[0] in y[0]:
                more_similar.append((x, y))
        translation = {}
        for (x, y) in more_similar:
            for xline in x:
                for yline in y:
                    translated_yline = self._check_lines(xline, yline)
                    if translated_yline:
                        translation[yline] = xline
        translated = []
        for block in self.comparison.recorded:
            translated_block = []
            for line in block:
                if translation.get(line):
                    translated_block.append(translation[line])
                else:
                    translated_block.append(line)
            translated.append(translated_block)
        return translated

    @staticmethod
    def _comparator(measurable, reference, translation):
        """TODO: Docstring for _comparator.

        Args:
            measurable (TODO): TODO
            reference (TODO): TODO

        Returns: TODO

        """
        head = [line[0] for line in reference]
        changes = []
        for mi, mb in enumerate(measurable):
            if len(mb) == 1 and mb not in reference:
                changes.append(translation[mi])
            elif len(mb) > 1:
                first_line = mb[0]
                if first_line in head:
                    rb = reference[head.index(first_line)]
                    additional = [first_line]
                    for mbi, line in enumerate(mb):
                        if line not in rb:
                            additional.append(translation[mi][mbi])
                    if len(additional) > 1:
                        changes.append(additional)
                else:
                    changes.append(translation[mi])
        return sorted(changes)

    @staticmethod
    def _format_changes(data):
        """TODO: Docstring for _format_changes.

        Args:
            data (TODO): TODO

        Returns: TODO

        """
        return "\n\n".join("\n".join(lines) for lines in data)

    @property
    def additional(self):
        """TODO: Docstring for additional.

        Returns: TODO

        """
        measurable = self._translate_comparison()
        reference = self.baseline.recorded
        translation = self.comparison.recorded
        return self._comparator(measurable, reference, translation)

    @property
    def missing(self):
        """TODO: Docstring for missing.

        Returns: TODO

        """
        measurable = self.baseline.recorded
        reference = self._translate_comparison()
        translation = self.baseline.recorded
        return self._comparator(measurable, reference, translation)

    @property
    def pprint_additional(self):
        """TODO: Docstring for pprint_additional.

        Returns: TODO

        """
        return self._format_changes(self.additional)

    @property
    def pprint_missing(self):
        """TODO: Docstring for pprint_missing.

        Returns: TODO

        """
        return self._format_changes(self.missing)

    def diff(self):
        """TODO: Docstring for diff.

        Returns: TODO

        """
        print("\nComparing {comparison} against baseline: {baseline}".format(
            comparison=os.path.basename(self.comparison.config),
            baseline=os.path.basename(self.baseline.config)
        ))
        print("\n[+] additional [+]\n")
        print("{}".format(self.pprint_additional()))
        print("\n[-] missing [-]\n")
        print("{}".format(self.pprint_missing()))
        print("\n--- END ---\n")
