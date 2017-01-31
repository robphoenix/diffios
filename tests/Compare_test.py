import os
import sys

sys.path.append(os.path.abspath("."))
sys.path.insert(0, os.path.abspath('..'))

from .context import diffios


def test_basic_comparison_without_variables():
    """ Compare two configs without variables """
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
    diff = diffios.Compare(baseline, comparison)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_basic_comparison_with_variables():
    """ Compare two configs with variables """
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
    diff = diffios.Compare(baseline, comparison)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_different_vlan_interface_config(ignores_file):
    """ Compare two vlan configs with variables and ignores file """
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
    diff = diffios.Compare(baseline=baseline, comparison=comparison, ignore_lines=ignores_file.split('\n'))
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_different_fast_interface_config_ignoring_description(int_baseline, int_comparison):
    """ Variable is not a difference """
    expected_additional = [[
        'interface FastEthernet0/5',
        ' switchport mode trunk',
        ' switchport trunk allowed vlan 510,511,999',
        ' switchport trunk native vlan 999'
    ]]
    expected_missing = [[
        'interface FastEthernet0/5',
        ' switchport mode access'
    ]]
    diff = diffios.Compare(baseline=int_baseline, comparison=int_comparison, ignore_lines=[])
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_different_aaa_config(aaa_baseline, aaa_comparison):
    """ Different aaa configs """
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
    diff = diffios.Compare(baseline=aaa_baseline, comparison=aaa_comparison)
    assert expected_additional == diff.additional()
    assert expected_missing == diff.missing()


def test_multiple_variables_ip_route():
    """ Multiple variables in single line with spaces in variable"""
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.1 tag 100']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_variables_ip_route_without_spaces():
    """ Multiple variables in single line without spaces in variable"""
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.1 tag 100']
    baseline = ['ip route {{LAN_NET}} 255.255.0.0 {{VLAN_99_IP}} tag 100']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_variables_ip_route_duplicated_ip():
    """ Multiple variables in single line with repeated IP address """
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.10 tag 100']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_variables_ip_route_similar_ip():
    """ Multiple variables in single line with similar IP addresses """
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.100 tag 100']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_triple_variables_ip_route():
    """ More than 2 variables in a single line """
    config = ['ip route 10.10.10.10 255.255.0.0 10.10.10.1 tag 100 and this']
    baseline = ['ip route {{ LAN_NET }} 255.255.0.0 {{ VLAN_99_IP }} tag 100 and {{ this }}']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_dialer_interface():
    """ Regular expression metacharacters ignored """
    baseline = [
        'interface Dialer1',
        ' description *** FTTC on PSTN:{{PSTN_NO}} CCT:{{CCT_ID}} ***'
    ]
    config = [
        'interface Dialer1',
        ' description *** FTTC on PSTN:020 8777 1953  CCT:IEUK644252 ***'
    ]
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_variables_with_regex_metacharacters():
    """ Regular Expression metacharacters ignored """
    baseline = ['description *** ADSL {{PSTN_NO}} {{CCT_ID}} ***',
                'description *** FTTC on PSTN:{{PSTN_NO}} CCT:{{CCT_ID}} ***']
    config = ['description *** ADSL 12345 67890 ***',
              'description *** FTTC on PSTN:12345 CCT:67890 ***']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_single_multiple_word_variables():
    """ Single variable word can account for multiple words """
    baseline = ['interface FastEthernet0/5', ' description {{ DESCRIPTION }}']
    config = ['interface FastEthernet0/5', ' description Data and Voice Access Port']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_multiple_word_variables():
    """ Multiple single word variables can account for multiple words """
    baseline = ['interface FastEthernet0/5', ' description {{ VLAN }} connection to {{ BACKUP }}']
    config = ['interface FastEthernet0/5', ' description Vlan 99 connection to Core Backup']
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_multiple_bgp_config_lines_with_same_first_word():
    """ Very similar lines starting with same word are different """
    baseline = [
        'router bgp {{BGP_AS}}',
        ' network {{LAN_NET}} mask 255.255.248.0',
        ' network {{LOOPBACK_IP}} mask 255.255.255.255',
        ' neighbour {{PE_IP}} remote-as 1234',
        ' neighbour {{PE_IP}} ebgp-multihop 2',
        ' neighbour {{PE_IP}} update-source GigabitEthernet0/0',
        ' neighbour {{PE_IP}} timers 10 30',
        ' neighbour {{PE_IP}} send-community',
        ' neighbour {{PE_IP}} soft-reconfiguration inbound'
    ]
    config = [
        'router bgp 65500',
        ' network 10.100.10.0 mask 255.255.248.0',
        ' network 10.200.10.0 mask 255.255.255.255',
        ' neighbour 10.200.10.10 remote-as 1234',
        ' neighbour 10.200.10.10 ebgp-multihop 2',
        ' neighbour 10.200.10.10 update-source GigabitEthernet0/0',
        ' neighbour 10.200.10.10 timers 10 30',
        ' neighbour 10.200.10.10 send-community',
        ' neighbour 10.200.10.10 soft-reconfiguration inbound'
    ]
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()


def test_prefix_lists_with_seq_value_in_ip_address():
    """ Very similar lines containing same words are different """
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
    diff = diffios.Compare(baseline, config, [])
    assert [] == diff.additional()
    assert [] == diff.missing()
