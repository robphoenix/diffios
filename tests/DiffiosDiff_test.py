import os
import sys
from unittest import TestCase

sys.path.append(os.path.abspath("."))
from diffios import DiffiosDiff


class DiffiosDiffTest(TestCase):

    def test_different_vlan_interface_config(self):
        baseline = [
            'hostname BASELINE',
            'interface Vlan1',
            ' no ip address',
            ' shutdown'
        ]
        comparison = [
            'hostname COMPARISON',
            'interface Vlan1',
            ' ip address 192.168.0.1 255.255.255.0',
            ' no shutdown'
        ]
        expected_additional = [[
            'interface Vlan1',
            ' ip address 192.168.0.1 255.255.255.0',
            ' no shutdown'
        ]]
        expected_missing = [[
            'interface Vlan1',
            ' no ip address',
            ' shutdown'
        ]]
        diff = DiffiosDiff(baseline=baseline, comparison=comparison)
        actual_additional = diff.additional
        actual_missing = diff.missing
        self.assertEqual(expected_additional, actual_additional)
        self.assertEqual(expected_missing, actual_missing)
