#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
from itertools import product

from diffios import DiffiosConfig

DELIMITER = r'{{[^{}]+}}'


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
