#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from collections import namedtuple


PARTIALS = [
    "^(?P<non_var> ip address )\d+\.\d+\.\d+\.\d+\s\d+\.\d+\.\d+\.\d+",
    "^(?P<non_var> description ).+",
    "(?P<non_var>ip dhcp snooping vlan ).+",
    "(?P<non_var>ip default-gateway ).+",
    "(?P<non_var>switchport trunk allowed vlan ).+"
]


class DiffiosConfig(object):

    """DiffiosConfig prepares a Cisco IOS Config to diff.

    DiffiosConfig takes a Cisco IOS config, as a file or a
    list, extracts the device hostname, removes any invalid
    lines, such as comments, breaks the config into a
    hierarchical block structure and partitions the config
    according to a list of lines to ignore.

    Attributes:
        ignore_filename (str): None or Absolute path of
            ignores file, if being used
        config_filename (str): None or Absolute path of
            config file, if being used
        ignores (list): None or list of lines to ignore
        config (list): None or list of config lines with
            invalid lines removed

    Kwargs:
        config (str|list): Path to config file, or list
            containing lines of config
        ignores (str|list): Path to ignores file, or list
            containing lines to ignore

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
    >>> conf = DiffiosConfig(config=config, ignores=ignores)
    >>> conf.ignore_filename
    >>> conf.config_filename
    >>> conf.ignores
    ['hostname', '^ description']
    >>> conf.config
    ['hostname ROUTER', 'interface FastEthernet0/1', ' description **Link to Core**', ' ip address 192.168.0.1 255.255.255.0']
    >>> conf.ignored
    [['hostname ROUTER'], [' description **Link to Core**']]
    >>> conf.recorded
    [['interface FastEthernet0/1', ' ip address 192.168.0.1 255.255.255.0']]

    """

    def __init__(self, config=None, ignores=None):
        self.ignore_filename = None
        self.config_filename = None
        self.ignores = None
        self.config = None

        diffios_ignore_exists = os.path.exists(os.path.join(os.getcwd(), "diffios_ignore"))
        if ignores is None and diffios_ignore_exists:
            ignores = os.path.join(os.getcwd(), "diffios_ignore")

        if bool(ignores):
            if isinstance(ignores, list):
                self.ignores = ignores
            elif os.path.isfile(os.path.abspath(ignores)):
                try:
                    f = open(os.path.abspath(ignores))
                    self.ignores = [l.strip().lower() for l in f.readlines()]
                    f.close()
                except IOError:
                    print("[FATAL] Diffios could not open '{}".format(config))
                    raise RuntimeError
                else:
                    self.ignore_filename = ignores
            else:
                raise RuntimeError(
                    ("[FATAL] DiffiosConfig() received an "
                     "invalid argument: ignores={}\n").format(ignores))

        if isinstance(config, list):
            self.config = self._remove_invalid_lines(config)
        elif os.path.isfile(os.path.abspath(config)):
            try:
                with open(os.path.abspath(config)) as f:
                    self.config = self._remove_invalid_lines(f.readlines())
            except IOError:
                print("[FATAL] Diffios could not open '{}".format(config))
                raise RuntimeError
            else:
                self.config_filename = config
        else:
            raise RuntimeError(
                ("[FATAL] DiffiosConfig() received an "
                    "invalid argument: config={}\n").format(config))

    def _remove_invalid_lines(self, lines):
        """TODO: Docstring for _remove_invalid_lines.

        Returns: TODO

        """
        return [l.rstrip() for l in lines if self._valid_line(l)]

    @staticmethod
    def _valid_line(line):
        """TODO: Docstring for _valid_line.

        Args:
            line (TODO): TODO

        Returns: TODO

        """
        lstrip = line.strip()
        return len(lstrip) > 0 and not lstrip.startswith("!")

    @staticmethod
    def _group_into_blocks(config):
        """TODO: Docstring for _group_into_blocks.

        Args:
            config (TODO): TODO

        Returns: TODO

        """
        current_group, groups = [], []
        for line in config:
            if not line.startswith(' ') and current_group:
                groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)
        if current_group:
            groups.append(current_group)
        return sorted(groups)

    @property
    def config_blocks(self):
        """TODO: Docstring for blocks.

        Returns: TODO

        """
        return self._group_into_blocks(self.config)

    @property
    def hostname(self):
        """TODO: Docstring for _hostname.

        Returns: TODO

        """
        for line in self.config:
            if "hostname" in line.lower():
                return line.split()[1]

    def _partition(self):
        """TODO: Docstring for partition.

        Returns: TODO

        """
        Partition = namedtuple("Partition", "ignored recorded")
        ignore = self.ignores
        config_blocks = self._group_into_blocks(self.config)
        ignored = []
        for i, block in enumerate(config_blocks):
            for j, line in enumerate(block):
                for line_to_ignore in ignore:
                    if re.findall(line_to_ignore, line.lower()):
                        if j == 0:
                            ignored.append(config_blocks[i])
                            config_blocks[i] = []
                        else:
                            ignored.append([block[j]])
                            block[j] = ""
        recorded = [[line for line in block if line] for block in config_blocks if block]
        return Partition(ignored, recorded)

    @property
    def ignored(self):
        """TODO: Docstring for ignored.

        Returns: TODO

        """
        return self._partition().ignored

    @property
    def recorded(self):
        """TODO: Docstring for recorded.

        Returns: TODO

        """
        return self._partition().recorded


class DiffiosDiff(object):

    """Docstring for DiffiosDiff. """

    def __init__(self, baseline=None, comparison=None, ignore_file=None):
        """TODO: Docstring for __init__.

        Kwargs:
            baseline (TODO): TODO
            comparison (TODO): TODO
            ignore_file (TODO): TODO

        """
        # TODO: make it so DiffiosConf objects can be passed in also
        # TODO: confirm existence of files
        self.baseline = DiffiosConfig(baseline, ignore_file)
        self.comparison = DiffiosConfig(comparison, ignore_file)
        self.partials = PARTIALS

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
            if len(dynamic_block) == 1 and dynamic_block not in translated_static:
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
        comparison = self.comparison.recorded
        baseline = self.baseline.recorded
        additional = self._changes(comparison, baseline)
        return additional

    @property
    def missing(self):
        """TODO: Docstring for missing.

        Returns: TODO

        """
        comparison = self.comparison.recorded
        baseline = self.baseline.recorded
        missing = self._changes(baseline, comparison)
        return missing

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
