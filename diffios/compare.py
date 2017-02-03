#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: compare.py
Author: Rob Phoenix
Email: rob@robphoenix.com
Github: https://github.com/robphoenix
Description: Compare and diff Cisco IOS configs
"""
import re
from collections import namedtuple

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

import diffios


class Compare(object):
    """Compare compares a Cisco IOS config against a baseline.

    Compare takes a baseline config and a comparison config.
    These can be files, lists or diffios.Config objects. If
    they are not diffios.Config objects they will be converted
    to these. Compare can also take a list of lines to ignore,
    as a list or a file, or default to an ignores.txt file in
    the project root.
    Compare will provide a diff between the comparison and
    baseline configs, detailing what is missing from the
    comparison config that is in the baseline config and what
    is additional to the comparison config that is not in the
    baseline config. These diffs will respect the hierarchical
    nature or Cisco IOS configs.
    Compare also provides convenience methods for displaying
    this data or saving it to file.

    Attributes:
        baseline(diffios.Config): A diffios.Config object,
            initialised with the baseline config
        comparison(diffios.Config): A diffios.Config object,
            initialised with the comparison config
        ignore_lines(list): List of lines to ignore

    >>> baseline = [
    ... 'hostname {{ hostname }}',
    ... 'interface FastEthernet 0/1',
    ... ' ip address {{ ip_address }}',
    ... ' switchport mode access',
    ... 'ip domain-name {{ domain }}']
    >>> comparison = [
    ... 'hostname COMPARISON',
    ... 'interface FastEthernet 0/1',
    ... ' ip address 192.168.0.1',
    ... ' switchport mode trunk',
    ... 'interface FastEthernet 0/2',
    ... ' ip address 192.168.0.2']
    >>> diff = diffios.Compare(baseline, comparison)
    >>> diff.additional()
    [['interface FastEthernet 0/1', ' switchport mode trunk'], ['interface FastEthernet 0/2', ' ip address 192.168.0.2']]
    >>> diff.missing()
    [['interface FastEthernet 0/1', ' switchport mode access'], ['ip domain-name {{ domain }}']]
    >>> print(diff.delta())
    --- baseline
    +++ comparison
    <BLANKLINE>
    -   1: interface FastEthernet 0/1
    -       switchport mode access
    -   2: ip domain-name {{ domain }}
    <BLANKLINE>
    +   1: interface FastEthernet 0/1
    +       switchport mode trunk
    +   2: interface FastEthernet 0/2
    +       ip address 192.168.0.2
    <BLANKLINE>
    >>> print(diff.pprint_additional())
    interface FastEthernet 0/1
     switchport mode trunk
    <BLANKLINE>
    interface FastEthernet 0/2
     ip address 192.168.0.2
    >>> print(diff.pprint_missing())
    interface FastEthernet 0/1
     switchport mode access
    <BLANKLINE>
    ip domain-name {{ domain }}

    """

    def __init__(self, baseline, comparison, ignore_lines=None):
        """Initialize a diffios.Compare object with a baseline,
            a comparison and lines to ignore.

        Args:
            baseline (str|list|diffios.Config): Path to baseline
                config file, list containing lines of config,
                or diffios.Config object
            comparison (str|list|diffios.Config): Path to comparison
                config file, list containing lines of config,
                or diffios.Config object

        Kwargs:
            ignore_lines (str|list): Path to ignores file, or list
                containing lines to ignore. Defaults to ignores
                file in current working directory if it exists.

        """
        self._baseline = baseline
        self._comparison = comparison
        self._ignore_lines = ignore_lines

        if isinstance(self._baseline, diffios.Config):
            self.baseline = self._baseline
        else:
            self.baseline = diffios.Config(self._baseline, self._ignore_lines)
        if isinstance(self._comparison, diffios.Config):
            self.comparison = self._comparison
        else:
            self.comparison = diffios.Config(self._comparison,
                                             self._ignore_lines)
        if self.baseline and self.comparison:
            self.ignore_lines = self.baseline.ignore_lines

    @staticmethod
    def _compare_lines(target, guess):
        for metacharacter in diffios.REGEX_METACHARACTERS:
            if metacharacter in target:
                target = target.replace(metacharacter,
                                        '\{}'.format(metacharacter))
        target_re = re.sub(r'{{[^{}]+}}', '(.+)', target)
        match = re.search(target_re, guess)
        if match:
            return match.group(0) == guess
        else:
            return False

    def _baseline_queue(self):
        bq = Queue()
        [bq.put(el) for el in self.baseline.included()]
        return bq

    def _comparison_hash(self):
        return {group[0]: group[1:] for group in self.comparison.included()}

    @staticmethod
    def _child_lookup(baseline_parent, baseline_children, comparison_children):
        ChildComparison = namedtuple('ChildComparison', 'additional missing')
        missing = []
        for baseline_child in baseline_children:
            if baseline_child not in comparison_children and not missing:
                missing.append(baseline_parent)
                missing.append(baseline_child)
            elif baseline_child not in comparison_children:
                missing.append(baseline_child)
            elif baseline_child in comparison_children:
                comparison_children.remove(baseline_child)
        if comparison_children:
            additional = [baseline_parent] + comparison_children
        else:
            additional = []
        return ChildComparison(additional, missing)

    def _child_search(self, target_children, comparison_children):
        ChildComparison = namedtuple('ChildComparison', 'additional missing')
        missing = []
        while target_children:
            child_target = target_children.pop()
            child_search = self._binary_search(child_target,
                                               comparison_children)
            if child_search:
                comparison_children.remove(child_search)
            else:
                missing.append(child_target)
        return ChildComparison(comparison_children, sorted(missing))

    def _binary_search(self, target, search_array):
        if not search_array:
            return None
        sorted_array = sorted(search_array)
        low = 0
        high = len(sorted_array) - 1
        while low <= high:
            mid = (high + low) // 2
            guess = sorted_array[mid]
            compare_lines = self._compare_lines(target, guess)
            if compare_lines:
                return guess
            if target < guess:
                high = mid - 1
            else:
                low = mid + 1
        return None

    def _hash_lookup(self, baseline, comparison):
        missing, additional, with_vars = [], [], []
        while not baseline.empty():
            baseline_group = baseline.get()
            baseline_parent = baseline_group[0]
            baseline_children = baseline_group[1:]
            baseline_family = ' '.join(baseline_group)
            if diffios.DELIMITER_START in baseline_family:
                with_vars.append(baseline_group)
            else:
                comparison_children = comparison.pop(baseline_parent, -1)
                if comparison_children == -1:
                    missing.append(baseline_group)
                elif comparison_children:
                    child_lookup = self._child_lookup(baseline_parent,
                                                      baseline_children,
                                                      comparison_children)
                    if child_lookup.additional:
                        additional.append(child_lookup.additional)
                    if child_lookup.missing:
                        missing.append(child_lookup.missing)
        return (missing, additional, with_vars)

    def _with_vars_search(self, with_vars, comparison, missing, additional):
        while with_vars:
            target = with_vars.pop()
            target_parent = target[0]
            target_children = sorted(target[1:])
            parent_search = self._binary_search(target_parent,
                                                comparison.keys())
            if parent_search:
                comparison_children = sorted(comparison.pop(parent_search))
                child_search = self._child_search(target_children,
                                                  comparison_children)
                if child_search.additional:
                    additional.append([parent_search] +
                                      child_search.additional)
                if child_search.missing:
                    missing.append([target_parent] + child_search.missing)
            else:
                missing.append(target)
        return (missing, additional)

    def _search(self):
        baseline = self._baseline_queue()
        comparison = self._comparison_hash()
        missing, additional, with_vars = self._hash_lookup(baseline,
                                                           comparison)
        missing, additional = self._with_vars_search(with_vars, comparison,
                                                     missing, additional)
        additional = sorted([[k] + v
                             for k, v in comparison.items()] + additional)
        return {'missing': missing, 'additional': additional}

    def additional(self):
        """Lines in the comparison config not present in baseline config.

        Due to the hierarchical nature of Cisco configs,
        lines can be grouped with a parent and it's children.
        Therefore when child lines are additional their parent line
        will also be included here, whether they themselves are
        additional or not, so as to give context for the child line,
        specifying which grouping they belong to.

        Example Group:
            interface FastEthernet0/1               # Parent
             ip address 192.168.0.1 255.255.255.0   # Child
             no shutdown                            # Child

        Returns:
            list: Sorted lines additional to the comparison config.

        """
        return sorted(self._search()['additional'])

    def missing(self):
        """Lines in the baseline config not present in comparison config.

        Due to the hierarchical nature of Cisco configs,
        lines can be grouped with a parent and it's children.
        Therefore when child lines are missing their parent line
        will also be included here, whether they themselves are
        missing or not, so as to give context for the child line,
        specifying which grouping they belong to.

        Example Group:
            interface FastEthernet0/1               # Parent
             ip address 192.168.0.1 255.255.255.0   # Child
             no shutdown                            # Child

        Returns:
            list: Sorted lines missing from the comparison config.

        """
        return sorted(self._search()['missing'])

    @staticmethod
    def _pprint_format(data, prefix):
        deltas = ""
        for i, group in enumerate(data, 1):
            deltas += "\n{} {:>3}: {}".format(prefix, i, group[0])
            if len(group) > 1:
                deltas += "\n{}      {}".format(prefix,
                                                "\n      ".join(group[1:]))
        return deltas

    def delta(self):
        """A human readable diff of the comparison against the baseline.

        A human readable string of the diff. Missing lines are
        prefixed with a '-', additional lines are prefixed with
        a '+'. Each hierarchical grouping is numbered.

        Example:
            --- baseline
            +++ comparison

            -   1: interface FastEthernet 0/1
            -        switchport mode access
            -   2: ip domain-name {{ domain }}

            +   1: interface FastEthernet 0/1
            +        switchport mode trunk
            +   2: interface FastEthernet 0/2
            +        ip address 192.168.0.2

        Returns:
            string: Detail of the diff of comparison against baseline.

        """
        missing = self._pprint_format(self.missing(), '-')
        additional = self._pprint_format(self.additional(), '+')
        return ("--- baseline\n"
                "+++ comparison"
                "\n{0}"
                "\n{1}"
                "\n").format(missing, additional)

    @staticmethod
    def _format_changes(data):
        return "\n\n".join("\n".join(lines) for lines in data)

    def pprint_additional(self):
        """A pretty print format of additional lines

        An output usable for writing to file.

        Example:
            interface FastEthernet 0/1
             switchport mode trunk

            interface FastEthernet 0/2
             ip address 192.168.0.2

        Returns:
            string: Pretty print formatted output

        """
        return self._format_changes(self.additional())

    def pprint_missing(self):
        """A pretty print format of missing lines

        An output usable for writing to file.

        Example:
            interface FastEthernet 0/1
             switchport mode access

            ip domain-name {{ domain }}

        Returns:
            string: Pretty print formatted output

        """
        return self._format_changes(self.missing())
