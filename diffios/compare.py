#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from queue import Queue
from collections import namedtuple

from diffios.config import DiffiosConfig

DELIMITER = r'{{[^{}]+}}'
DELIMITER_START = '{{'
DELIMITER_END = '}}'


class DiffiosCompare(object):

    """Docstring for DiffiosDiff. """

    def __init__(self, baseline, comparison, ignore_lines=None):
        self._baseline = baseline
        self._comparison = comparison
        self._ignore_lines = ignore_lines
        self.baseline = DiffiosConfig(self._baseline, self._ignore_lines)
        self.comparison = DiffiosConfig(self._comparison, self._ignore_lines)

    @staticmethod
    def _compare_lines(target, guess):
        re_metacharacters = ['*']
        for char in re_metacharacters:
            if char in target:
                target = target.replace(char, '\{}'.format(char))
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

    def _child_lookup(self, baseline_parent, baseline_children, comparison_children):
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
            child_search = self._binary_search(
                child_target, comparison_children)
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
            if DELIMITER_START in baseline_family:
                with_vars.append(baseline_group)
            else:
                comparison_children = comparison.pop(baseline_parent, -1)
                if comparison_children == -1:
                    missing.append(baseline_group)
                elif comparison_children:
                    child_lookup = self._child_lookup(
                        baseline_parent, baseline_children, comparison_children)
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
            parent_search = self._binary_search(
                target_parent, comparison.keys())
            if parent_search:
                comparison_children = sorted(comparison.pop(parent_search))
                child_search = self._child_search(
                    target_children, comparison_children)
                if child_search.additional:
                    additional.append(
                        [parent_search] + child_search.additional)
                if child_search.missing:
                    missing.append([target_parent] + child_search.missing)
            else:
                missing.append(target)
        return (missing, additional)

    def _search(self):
        baseline = self._baseline_queue()
        comparison = self._comparison_hash()
        missing, additional, with_vars = self._hash_lookup(
            baseline, comparison)
        missing, additional = self._with_vars_search(
            with_vars, comparison, missing, additional)
        additional = sorted(
            [[k] + v for k, v in comparison.items()] + additional)
        return {'missing': missing, 'additional': additional}

    def additional(self):
        return sorted(self._search()['additional'])

    def missing(self):
        return sorted(self._search()['missing'])

    @staticmethod
    def _pprint_format(data, prefix):
        """TODO: Docstring for _pprint_format.
        Args:
            data (TODO): TODO
        Returns: TODO
        """
        deltas = ""
        for i, group in enumerate(data, 1):
            deltas += "\n{} {:>3}: {}".format(prefix, i, group[0])
            if len(group) > 1:
                deltas += "\n{}       {}".format(prefix, "\n      ".join(group[1:]))
        return deltas

    def delta(self):
        """TODO: Docstring for diff.

        Returns: TODO

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
        """TODO: Docstring for _format_changes.
        Args:
            data (TODO): TODO
        Returns: TODO
        """
        return "\n\n".join("\n".join(lines) for lines in data)

    def pprint_additional(self):
        """TODO: Docstring for pprint_additional.
        Returns: TODO
        """
        return self._format_changes(self.additional())

    def pprint_missing(self):
        """TODO: Docstring for pprint_missing.
        Returns: TODO
        """
        return self._format_changes(self.missing())
