import os
import sys

sys.path.append(os.path.abspath("."))
sys.path.insert(0, os.path.abspath('..'))

from diffios.diff import DiffiosDiff


def test_basic_comparison_without_variables():
    baseline = [
        'interface FastEthernet0/1',
        ' description link to core',
        ' no ip address',
        ' shutdown',
        'interface Vlan1',
        ' ip address 10.10.10.10'
    ]
    comparison = [
        'interface FastEthernet0/1',
        ' description link to core',
        ' ip address 192.168.0.1 255.255.255.0',
    ]
    expected_additional = [[
        'interface FastEthernet0/1',
        ' ip address 192.168.0.1 255.255.255.0',
    ]]
    expected_missing = sorted([
        ['interface FastEthernet0/1',
         ' no ip address',
         ' shutdown'],
        ['interface Vlan1',
         ' ip address 10.10.10.10']
    ])
    diff = DiffiosDiff(baseline, comparison)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_basic_comparison_with_variables():
    baseline = [
        'interface FastEthernet0/1',
        ' description {{ description }}',
        ' no ip address',
        ' shutdown',
        'interface Vlan1',
        ' ip address {{ ip address }}'
    ]
    comparison = [
        'interface FastEthernet0/1',
        ' description link to core',
        ' ip address 192.168.0.1 255.255.255.0',
    ]
    expected_additional = [[
        'interface FastEthernet0/1',
        ' ip address 192.168.0.1 255.255.255.0',
    ]]
    expected_missing = sorted([
        ['interface FastEthernet0/1',
         ' no ip address',
         ' shutdown'],
        ['interface Vlan1',
         ' ip address {{ ip address }}']
    ])
    diff = DiffiosDiff(baseline, comparison)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_different_vlan_interface_config(ignores):
    baseline = [
        'hostname {{ hostname }}',
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
    diff = DiffiosDiff(baseline=baseline, comparison=comparison, ignore_lines=ignores)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


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
    diff = DiffiosDiff(baseline=int_baseline, comparison=int_comparison, ignore_lines=[])
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


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
        ['aaa server radius dynamic-author', ' client 10.10.20.1 server-key 7 1234567890ABCDEFGHIJKL']]
    expected_missing = [
        ['aaa accounting exec CON start-stop group radius'],
        ['aaa accounting exec VTY start-stop group radius'],
        ['aaa authentication login CON group radius local'],
        ['aaa authentication login VTY group radius local'],
        ['aaa authorization exec CON group radius local'],
        ['aaa authorization exec VTY group radius local'],
        ['aaa server radius dynamic-author', ' client 10.10.21.1 server-key 7 1234567890ABCDEFGHIJKL']]
    diff = DiffiosDiff(baseline=aaa_baseline, comparison=aaa_comparison)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_multiple_vars_ip_route():
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.1 tag 100']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_vars_ip_route_without_splaces():
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.1 tag 100']
    baseline = ['ip route {{LAN_NET}} 255.255.0.0 {{VLAN_99_IP}} tag 100']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_vars_ip_route_duplicated_ip():
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.10 tag 100']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_vars_ip_route_similar_ip():
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.100 tag 100']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_triple_vars_ip_route():
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.1 tag 100 and this']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100 and {{ this }}']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_vars_with_regex_metacharacters():
    baseline = ['description *** ADSL {{PSTN_NO}} {{CCT_ID}} ***',
                'description *** FTTC on PSTN:{{PSTN_NO}} CCT:{{CCT_ID}} ***']
    config = ['description *** ADSL 12345 67890 ***',
              'description *** FTTC on PSTN:12345 CCT:67890 ***']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_single_multiple_word_vars():
    baseline = ['interface FastEthernet0/5', ' description {{ DESCRIPTION }}']
    config = ['interface FastEthernet0/5', ' description Data and Voice Access Port']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_multiple_word_vars():
    baseline = ['interface FastEthernet0/5', ' description {{ VLAN }} connection to {{ BACKUP }}']
    config = ['interface FastEthernet0/5', ' description Vlan 99 connection to Core Backup']
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_bgp_config_lines_with_same_first_word():
    baseline = [
        'router bgp {{BGP_AS}}',
        ' network {{LAN_NET}} mask 255.255.248.0',
        ' network {{LOOPBACK_IP}} mask 255.255.255.255',
        ' neighbour {{PE_IP}} remote-as 1234',
        # ' neighbour {{PE_IP}} ebgp-multihop 2',
        ' neighbour {{PE_IP}} update-source GigabitEthernet0/0',
        # ' neighbour {{PE_IP}} timers 10 30',
        # ' neighbour {{PE_IP}} send-community',
        # ' neighbour {{PE_IP}} soft-reconfiguration inbound'
    ]
    config = [
        'router bgp 65500',
        ' network 10.100.10.0 mask 255.255.248.0',
        ' network 10.200.10.0 mask 255.255.255.255',
        ' neighbour 10.200.10.10 remote-as 1234',
        # ' neighbour 10.200.10.10 ebgp-multihop 2',
        ' neighbour 10.200.10.10 update-source GigabitEthernet0/0',
        # ' neighbour 10.200.10.10 timers 10 30',
        # ' neighbour 10.200.10.10 send-community',
        # ' neighbour 10.200.10.10 soft-reconfiguration inbound'
    ]
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    # assert [] == diff.missing()


def test_prefix_lists_with_seq_value_in_ip_address():
    baseline = [
        'ip prefix-list bgp-routes-out seq 5 permit {{IP_ADDRESS}}',
        'ip prefix-list bgp-routes-out seq 10 permit {{IP_ADDRESS}}',
        'ip prefix-list bgp-routes-out seq 15 permit {{IP_ADDRESS}}'
    ]
    config = [
        'ip prefix-list bgp-routes-out seq 5 permit 10.14.4.0/23',
        'ip prefix-list bgp-routes-out seq 10 permit 10.25.0.12/32',
        'ip prefix-list bgp-routes-out seq 15 permit 10.14.5.64/27'
    ]
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_dialer_interface():
    baseline = [
        'interface Dialer1',
        ' description *** FTTC on PSTN:{{PSTN_NO}} CCT:{{CCT_ID}} ***'
    ]
    config = [
        'interface Dialer1',
        ' description *** FTTC on PSTN:020 8777 1953  CCT:IEUK644252 ***'
    ]
    diff = DiffiosDiff(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()
