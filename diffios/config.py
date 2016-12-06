#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
from collections import namedtuple


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
    ... ' description *** Link to Core ***',
    ... ' ip address 192.168.0.1 255.255.255.0']
    >>> ignore = [
    ... 'hostname',
    ... '^ description']
    >>> conf = DiffiosConfig(config, ignore)
    >>> conf.hostname
    'ROUTER'
    >>> conf.config
    ['!', 'hostname ROUTER', '!', 'interface FastEthernet0/1', ' description \
*** Link to Core ***', ' ip address 192.168.0.1 255.255.255.0']
    >>> conf.ignore_lines
    ['hostname', '^ description']
    >>> conf.ignored()
    [['hostname ROUTER'], [' description *** Link to Core ***']]
    >>> conf.included()
    [['interface FastEthernet0/1', ' ip address 192.168.0.1 255.255.255.0']]

    """

    def __init__(self, config, ignore_lines=None):
        if ignore_lines is None and os.path.exists(os.path.join(os.getcwd(), 'diffios_ignore')):
            ignore_lines = os.path.join(os.getcwd(), "diffios_ignore")
            print('ignore_lines: ', ignore_lines)
        elif ignore_lines is None:
            ignore_lines = []
        self.config = self._check_data(config)
        self.ignore_lines = self._ignore(self._check_data(ignore_lines))

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

    def _ignore(self, ignore):
        """Transforms given ignores data into usable format.

        Args:
            ignores (list|file): ignores as either list or file.

        Returns:
            list: Lines to ignore.

        """
        ignore = [line.strip().lower() for line in ignore]
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


class Baseline(object):

    """Docstring for Baseline. """

    def __init__(self, config, ignore_lines=None):
        """TODO: to be defined1.

        Args:
            config (TODO): TODO
            ignore_lines (TODO): TODO


        """
        self._config = config
        self._ignore_lines = ignore_lines
        self.config = DiffiosConfig(self._config, self._ignore_lines)
