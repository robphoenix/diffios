#!/usr/bin/env python3
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

    def __init__(self, config, ignores=None):
        ignores = ignores or os.path.join(os.getcwd(), "diffios_ignore")
        self.config = self._config(config)
        self.ignores = self._ignores(ignores)

    def _config(self, data):
        """Transforms given config data into usable format,
            with only valid lines.

        Args:
            data (list|file): config as either list or file.

        Returns:
            list: The config as a list of valid lines.

        """
        return self._remove_invalid_lines(self._check_data(data))

    def _ignores(self, data):
        """Transforms given ignores data into usable format.

        Args:
            ignores (list|file): ignores as either list or file.

        Returns:
            list: Lines to ignore.

        """
        return [l.strip().lower() for l in self._check_data(data)]

    def _check_data(self, data):
        """Check type of data and convert it if necessary.

        Args:
            data (list|file): input data as either list or file.

        Returns:
            list: The input data as a list.

        Raises:
            RuntimeError: If file cannot be opened or given data
                is not a list or file.

        """
        if isinstance(data, list):
            return data
        elif os.path.isfile(data):
            try:
                with open(data) as fin:
                    return fin.readlines()
            except IOError:
                raise RuntimeError(("DiffiosConfig could not open '{}".format(data)))
        else:
            raise RuntimeError(("[FATAL] DiffiosConfig() received an "
                                "invalid argument: config={}\n").format(data))

    def _remove_invalid_lines(self, config):
        """Remove invalid lines from a given config.

        Args:
            config (list): Config as a list of lines.

        Returns:
            list: Only valid lines in given config.

        """
        return [l.rstrip() for l in config if self._valid_line(l)]

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
        lstrip = line.strip()
        return len(lstrip) > 0 and not lstrip.startswith("!")

    @staticmethod
    def _group_into_blocks(config):
        """Group config into hierarchical blocks.

        Blocks are defined as a parent/child relationship,
        where children lines start with a ' ', and parents
        are the immediately preceding line that doesn't start
        with a ' '. Blocks can be single lines where there
        is no children. Returns the blocks sorted.

        Example Blocks:
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
        """The config as sorted list of hierarchical blocks.

        Returns:
            list: self.config as a sorted list of lists, each list
                representing a hierarchical block of config.

        """
        return self._group_into_blocks(self.config)

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

    def _partition(self):
        """Partition lines to ignore out from the config.

        Returns:
            namedtuple: list of ignored lines and list of
                recorded (not ignored) lines

        """
        Partition = namedtuple("Partition", "ignored recorded")
        config_blocks = self._group_into_blocks(self.config)
        ignored = []
        for i, block in enumerate(config_blocks):
            for j, line in enumerate(block):
                for line_to_ignore in self.ignores:
                    match = re.findall(line_to_ignore, line.lower())
                    if match and j == 0:
                        ignored.append(config_blocks[i])
                        config_blocks[i] = []
                    elif match:
                        ignored.append([block[j]])
                        block[j] = ""
        recorded = [[line for line in block if line] for block in config_blocks if block]
        return Partition(ignored, recorded)

    @property
    def ignored(self):
        """Lines in the config that are being ignored.

        Returns:
            list: ignored lines

        """
        return self._partition().ignored

    @property
    def recorded(self):
        """Lines in the config that are being recorded (not ignored).

        Returns:
            list: recorded (not ignored) lines

        """
        return self._partition().recorded


class CheckConfig(object):

    """Docstring for CheckConfig. """

    def __init__(self, block, config):
        """TODO: to be defined1.

        Args:
            block (TODO): TODO
            config (TODO): TODO

        """
        self._block = block
        self._config = config
        self.present = []
        self.not_present = []
        self.parent = self._block[0]
        self.children = self._block[1:]
        self.check()

    def _parent_child_config_dict(self):
        return {el[0]: el[1:] for el in self._config}

    def check(self):
        if not self.children and self._block in self._config:
            self.present.append(self.parent)
        elif not self.children:
            self.not_present.append(self.parent)
        elif self.parent in self._parent_child_config_dict().keys():
                self.present.append(self.parent)
                config_children = self._parent_child_config_dict()[self.parent]
                for i, child in enumerate(self.children):
                    if child in config_children:
                        self.present.append(child)
                    elif i == 0:
                        self.not_present.append(self.parent)
                        self.not_present.append(child)
                    else:
                        self.not_present.append(child)


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
