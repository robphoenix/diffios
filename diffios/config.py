#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: config.py
Author: Rob Phoenix
Email: rob@robphoenix.com
Github: https://github.com/robphoenix
Description: Prepare Cisco IOS configs for comparison

"""
import os
import re
from collections import namedtuple

import diffios


class Config(object):
    """Config prepares a Cisco IOS Config to diff.

    Config takes a Cisco IOS config, as a file or a
    list, removes any invalid lines, such as comments,
    breaks the config into a hierarchical block structure
    and partitions the config according to a list of
    lines to ignore.

    Attributes:
        config (list): List of valid config lines
        ignore_lines (list): List of lines to ignore

    Args:
        config (str|list): Path to config file, or list
            containing lines of config

    Kwargs:
        ignore_lines (str|list): Path to ignores file, or list
            containing lines to ignore. Defaults to empty list.

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
    >>> conf = Config(config, ignore)
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
        self.config = self._check_data('config', config)
        if ignore_lines is None:
            ignore_lines = []
        self.ignore_lines = self._ignore(
            self._check_data('ignore_lines', ignore_lines))

    def _valid_config(self):
        return [l.rstrip() for l in self.config if self._valid_line(l)]

    def _group_config(self):
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
        """Lines from the original config that are not ignored. """
        return self._partition_config().included

    def ignored(self):
        """Lines from the original config that are ignored. """
        return self._partition_config().ignored

    @staticmethod
    def _ignore(ignore):
        return [line.strip().lower() for line in ignore]

    @staticmethod
    def _check_data(name, data):
        invalid_arg = "diffios.Config() received an invalid argument: {}={}\n"
        unable_to_open = "diffios.Config() could not open '{}'"
        if isinstance(data, list):
            return data
        try:
            with open(data) as fin:
                return fin.read().splitlines()  # remove '\n' from lines
        except IOError:
            raise RuntimeError((unable_to_open.format(data)))
        except:
            raise RuntimeError(invalid_arg.format(name, data))

    @staticmethod
    def _valid_line(line):
        line = line.strip()
        return len(line) > 0 and not line.startswith(
            "!") and line != '^' and line != '^C'

    def _ignore_line(self, line):
        for line_to_ignore in self.ignore_lines:
            for metacharacter in diffios.REGEX_METACHARACTERS:
                if metacharacter in line_to_ignore:
                    line_to_ignore = line_to_ignore.replace(
                        metacharacter, '\{}'.format(metacharacter))
            if re.search(line_to_ignore, line.lower()):
                return True
        return False
