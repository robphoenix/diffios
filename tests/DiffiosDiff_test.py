import os
import sys
from unittest import TestCase

sys.path.append(os.path.abspath("."))
from diffios import DiffiosDiff

int_baseline = """interface FastEthernet0/5
 description Data and Voice Access Port
 switchport access vlan 101
 switchport mode access
 switchport nonegotiate
 ip access-group ALLOW-ALL in
 no logging event link-status
 srr-queue bandwidth share 1 30 35 5
 priority-queue out
 authentication event fail action next-method
 authentication event server dead action authorize
 authentication event server dead action authorize voice
 authentication event server alive action reinitialize
 authentication host-mode multi-auth
 authentication open
 authentication order dot1x mab
 authentication priority dot1x mab
 authentication port-control auto
 authentication periodic
 authentication timer reauthenticate server
 authentication violation restrict
 mab
 snmp trap mac-notification change added
 no snmp trap link-status
 mls qos trust dscp
 dot1x pae authenticator
 dot1x timeout tx-period 10
 storm-control broadcast level 20.00
 spanning-tree portfast
 spanning-tree bpduguard enable
 service-policy input QOS-CLASSIFY""".split('\n')

int_comparison = """interface FastEthernet0/5
 description Cisco AP
 switchport access vlan 101
 switchport trunk native vlan 999
 switchport trunk allowed vlan 510,511,999
 switchport mode trunk
 switchport nonegotiate
 ip access-group ALLOW-ALL in
 no logging event link-status
 srr-queue bandwidth share 1 30 35 5
 priority-queue out
 authentication event fail action next-method
 authentication event server dead action authorize
 authentication event server dead action authorize voice
 authentication event server alive action reinitialize
 authentication host-mode multi-auth
 authentication open
 authentication order dot1x mab
 authentication priority dot1x mab
 authentication port-control auto
 authentication periodic
 authentication timer reauthenticate server
 authentication violation restrict
 mab
 snmp trap mac-notification change added
 no snmp trap link-status
 mls qos trust dscp
 dot1x pae authenticator
 dot1x timeout tx-period 10
 storm-control broadcast level 20.00
 spanning-tree portfast
 spanning-tree bpduguard enable
 service-policy input QOS-CLASSIFY""".split('\n')

aaa_baseline = """aaa group server radius ISE
 server name bob
 server name alice
 load-balance method least-outstanding
!
aaa authentication login VTY group radius local
aaa authentication login CON group radius local
aaa authentication dot1x default group radius
aaa authorization console
aaa authorization config-commands
aaa authorization exec VTY group radius local
aaa authorization exec CON group radius local
aaa authorization network default group radius
aaa accounting update periodic 15
aaa accounting dot1x default start-stop group radius
aaa accounting exec VTY start-stop group radius
aaa accounting exec CON start-stop group radius
aaa accounting system default start-stop group radius
no aaa accounting system guarantee-first
!
aaa server radius dynamic-author
 client 10.10.21.1 server-key 7 1234567890ABCDEFGHIJKL
 client 10.20.20.1 server-key 7 1234567890ABCDEFGHIJKL
!
aaa session-id common
clock summer-time BST recurring last Sun Mar 2:00 last Sun Oct 2:00
system mtu routing 1500
authentication mac-move permit
authentication critical recovery delay 600""".split('\n')

aaa_comparison = """aaa group server radius ISE
 server name bob
 server name alice
 load-balance method least-outstanding
!
aaa authentication login default group tacacs+ local
aaa authentication login VTY group tacacs+ local
aaa authentication login CON group tacacs+ local
aaa authentication dot1x default group radius
aaa authorization console
aaa authorization config-commands
aaa authorization exec default group tacacs+ local
aaa authorization exec VTY group tacacs+ local
aaa authorization exec CON group tacacs+ local
aaa authorization network default group radius
aaa accounting update periodic 15
aaa accounting dot1x default start-stop group radius
aaa accounting exec VTY start-stop group tacacs+
aaa accounting exec CON start-stop group tacacs+
aaa accounting commands 0 VTY start-stop group tacacs+
aaa accounting commands 0 CON start-stop group tacacs+
aaa accounting commands 15 VTY start-stop group tacacs+
aaa accounting commands 15 CON start-stop group tacacs+
aaa accounting system default start-stop group radius
no aaa accounting system guarantee-first
!
!
!
!
!
aaa server radius dynamic-author
 client 10.10.20.1 server-key 7 1234567890ABCDEFGHIJKL
 client 10.20.20.1 server-key 7 1234567890ABCDEFGHIJKL
!
aaa session-id common
clock summer-time BST recurring last Sun Mar 2:00 last Sun Oct 2:00
system mtu routing 1500
authentication mac-move permit
authentication critical recovery delay 600""".split('\n')


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

    def test_different_fast_interface_config_ignoring_description(self):
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
        actual_additional = diff.additional
        actual_missing = diff.missing
        self.assertEqual(expected_additional, actual_additional)
        self.assertEqual(expected_missing, actual_missing)

    def test_different_aaa_config(self):
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
        actual_additional = diff.additional
        print(actual_additional)
        actual_missing = diff.missing
        self.assertEqual(expected_additional, actual_additional)
        self.assertEqual(expected_missing, actual_missing)
