#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
from collections import namedtuple

from diffios import DiffiosConfig

DELIMITER = r'{{[^{}]+}}'
DELIMITER_START = '{{'
DELIMITER_END = '}}'


class DiffiosDiff(object):

    """Docstring for DiffiosDiff. """

    def __init__(self, baseline, comparison, ignore_lines=None):
        """TODO: Docstring for __init__.

        Kwargs:
            baseline (TODO): TODO
            comparison (TODO): TODO
            ignore_file (TODO): TODO

        """
        self._baseline = baseline
        self._comparison = comparison
        self._ignore_lines = ignore_lines
        self.baseline = DiffiosConfig(self._baseline, self._ignore_lines)
        self.comparison = DiffiosConfig(self._comparison, self._ignore_lines)

    @staticmethod
    def _check_lines(xline, yline):
        re_metacharacters = ['*', '.']
        for char in re_metacharacters:
            if char in xline:
                xline = xline.replace(char, '\{}'.format(char))
        xline_re = re.sub(r'{{[^{}]+}}', '(.+)', xline)
        match = re.search(xline_re, yline)
        if match:
            return match.group(0) == yline
        else:
            return False

    def _baseline_queue(self):
        return self.baseline.included()

    def _comparison_hash_table(self):
        return {group[0]: group[1:] for group in self.comparison.included()}

    def _child_lookup(self, baseline_parent, baseline_children, comparison_children):
        ChildComparison = namedtuple('ChildComparison', 'additional missing')
        missing = []
        for baseline_child in baseline_children:
            # if the baseline child is not in the comparison
            # children list then we add it to the list of missing
            # lines. If it's the first one, missing will be
            # empty, and we have to add it's parent as well.
            if baseline_child not in comparison_children and not missing:
                missing.append(baseline_parent)
                missing.append(baseline_child)
            elif baseline_child not in comparison_children:
                missing.append(baseline_child)
            # if the line is in both baseline and comparison
            # children then we need to remove it from comparison
            # children
            elif baseline_child in comparison_children:
                comparison_children.remove(baseline_child)
        # any lines left in comparison children are additional so
        # we need to add them, along with their parent, to the list
        # of additional lines
        if comparison_children:
            additional = [baseline_parent] + comparison_children
        else:
            additional = []
        return ChildComparison(additional, missing)

    def _search(self):
        baseline = self._baseline_queue()
        comparison = self._comparison_hash_table()
        missing = []
        additional = []
        while baseline:
            baseline_group = baseline.pop()
            baseline_parent = baseline_group[0]
            baseline_children = baseline_group[1:]
            baseline_family = ' '.join(baseline_group)
            if DELIMITER_START in baseline_family:
                # binary search
                return 'not implemented yet'
            else:
                # check the presence of the baseline parent in the comparison
                # hash table
                comparison_children = comparison.pop(baseline_parent, -1)
                # if -1 returned then the baseline parent and any children are
                # not present in the comparison hash table
                if comparison_children == -1:
                    missing.append(baseline_group)
                # if comparison_children is not an empty list or -1 then we
                # have to compare them against the baseline children
                elif comparison_children:
                    child_lookup = self._child_lookup(baseline_parent, baseline_children, comparison_children)
                    if child_lookup.additional:
                        additional.append(child_lookup.additional)
                    if child_lookup.missing:
                        missing.append(child_lookup.missing)
        additional = sorted([[k] + v for k, v in comparison.items()] + additional)
        return {'missing': missing, 'additional': additional}

    def additional(self):
        return sorted(self._search()['additional'])

    def missing(self):
        return sorted(self._search()['missing'])

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
