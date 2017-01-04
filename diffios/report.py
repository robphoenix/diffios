#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class DiffiosReport(object):

    """Docstring for DiffiosReport. """

    def __init__(self, additional, missing):
        """TODO: to be defined1.

        Args:
            additional (TODO): TODO
            missing (TODO): TODO


        """
        self._additional = additional
        self._missing = missing

    @staticmethod
    def _pprint_format(data):
        """TODO: Docstring for _pprint_format.
        Args:
            data (TODO): TODO
        Returns: TODO
        """
        deltas = ""
        for i, group in enumerate(data, 1):
            deltas += "\n{:>3}: {}".format(i, group[0])
            if len(group) > 1:
                deltas += "\n      {}\n".format("\n      ".join(group[1:]))
        return deltas

    def pprint_diff(self):
        """TODO: Docstring for diff.

        Returns: TODO

        """
        additional = self._pprint_format(self._additional)
        missing = self._pprint_format(self._missing)
        return ("\n--- Additional ---\n"
                "{0}"
                "\n\n--- Missing ---\n"
                "{1}"
                "\n\n--- END ---\n").format(additional, missing)
