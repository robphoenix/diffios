#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import progressbar

from diffios import DiffiosDiff


class DiffiosDir(object):

    """Docstring for DiffiosDir. """

    def __init__(self, baseline, comparison_dir, ignore_lines):
        """TODO: to be defined1.

        Args:
            baseline (TODO): TODO
            comparison_dir (TODO): TODO
            ignore_lines (TODO): TODO


        """
        self._baseline = baseline
        self._comparison_dir = comparison_dir
        self._ignore_lines = ignore_lines
        self._files = sorted(os.listdir(self._comparison_dir))

    def diff(self):
        for fin in progressbar.ProgressBar(self._files):
            comparison = os.path.join(self._comparison_dir, fin)
            delta = DiffiosDiff(
                self._baseline,
                comparison,
                self._ignore_lines)
            yield delta
