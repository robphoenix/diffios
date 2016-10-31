import os
import sys

sys.path.append(os.path.abspath("."))
from diffios import DiffiosDiff


def test_different_vlan_interface_config():
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
    assert expected_additional == diff.additional
    assert expected_missing == diff.missing


def test_different_fast_interface_config_ignoring_description(int_baseline, int_comparison):
    expected_additional = [[
        'interface FastEthernet0/5',
        ' switchport trunk native vlan 999',
        ' switchport trunk allowed vlan 510,511,999',
        ' switchport mode trunk'
    ]]
    expected_missing = [[
        'interface FastEthernet0/5',
        ' switchport mode access'
    ]]
    diff = DiffiosDiff(baseline=int_baseline, comparison=int_comparison)
    assert expected_additional == diff.additional
    assert expected_missing == diff.missing


def test_different_aaa_config(aaa_baseline, aaa_comparison):
    expected_additional = [
        ['aaa accounting commands 0 CON start-stop group tacacs+'],
        ['aaa accounting commands 0 VTY start-stop group tacacs+'],
        ['aaa accounting commands 15 CON start-stop group tacacs+'],
        ['aaa accounting commands 15 VTY start-stop group tacacs+'],
        ['aaa accounting exec CON start-stop group tacacs+'],
        ['aaa accounting exec VTY start-stop group tacacs+'],
        ['aaa authentication login CON group tacacs+ local'],
        ['aaa authentication login VTY group tacacs+ local'],
        ['aaa authentication login default group tacacs+ local'],
        ['aaa authorization exec CON group tacacs+ local'],
        ['aaa authorization exec VTY group tacacs+ local'],
        ['aaa authorization exec default group tacacs+ local'],
        ['aaa server radius dynamic-author',
            ' client 10.10.20.1 server-key 7 1234567890ABCDEFGHIJKL']]
    expected_missing = [
        ['aaa accounting exec CON start-stop group radius'],
        ['aaa accounting exec VTY start-stop group radius'],
        ['aaa authentication login CON group radius local'],
        ['aaa authentication login VTY group radius local'],
        ['aaa authorization exec CON group radius local'],
        ['aaa authorization exec VTY group radius local'],
        ['aaa server radius dynamic-author',
            ' client 10.10.21.1 server-key 7 1234567890ABCDEFGHIJKL']]
    diff = DiffiosDiff(baseline=aaa_baseline, comparison=aaa_comparison)
    assert expected_additional == diff.additional
    assert expected_missing == diff.missing
