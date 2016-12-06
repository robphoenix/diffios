#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

from diffios import DiffiosConfig

DELIMITER = r'{{[^{}]+}}'


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

    def _search(self):
        queue = self._baseline_queue()
        hash_table = self._comparison_hash_table()
        missing = []
        while queue:
            baseline_group = queue.pop()
            baseline_parent = group[0]
            baseline_children = group[1:]
            baseline_family = ' '.join(group)
            if '{{' in baseline_family:
                # binary search
                pass
            else:
                missing_group = []
                comparison_children = hash_table.pop(baseline_parent, -1)
                if comparison_children == -1:
                    missing.append(baseline_group)
                elif comparison_children:
                    comparison_parent = baseline_parent
                    for baseline_child in baseline_children:
                        if baseline_child not in comparison_children and not missing_group:
                            missing_group.append(baseline_parent)
                            missing_group.append(baseline_child)
                        elif baseline_child not in comparison_children:
                            missing_group.append(baseline_child)
                    if missing_group:
                        missing.append(missing_group)
        additional = hash_table

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
