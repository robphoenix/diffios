#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import namedtuple
import os
import sys
import pytest

sys.path.append(os.path.abspath("."))
from diffios import DiffiosConfig


@pytest.fixture
def config():
    configs_dir = os.path.abspath(os.path.join("tests", "configs"))
    return os.path.join(configs_dir, "baseline.conf")


@pytest.fixture
def ignores():
    return os.path.join(os.getcwd(), 'test_diffios_ignore')


@pytest.fixture
def dc():
    return DiffiosConfig(config(), ignores=ignores())


@pytest.fixture
def baseline():
    config = """version 15.0
no service pad
service tcp-keepalives-in
service tcp-keepalives-out
service timestamps debug datetime msec localtime year
service timestamps log datetime msec localtime year
service password-encryption
service sequence-numbers
!
hostname BASELINE01
!
boot-start-marker
boot-end-marker
!
!
no ip domain-lookup
ip domain-name diffios.dev
!
interface FastEthernet0/1
 description Management
 switchport trunk native vlan 777
 switchport trunk allowed vlan 410,411,777
 switchport mode trunk
 switchport nonegotiate
!
line con 0
 exec-timeout 5 0
 authorization exec CON
 login authentication CON
line vty 0 4
 exec-timeout 5 0
 authorization exec VTY
 login authentication VTY
 transport input telnet ssh
line vty 5 15
 exec-timeout 5 0
 transport input telnet ssh
!
end"""
    return config


@pytest.fixture
def baseline_config():
    content = """version 15.0
no service pad
service tcp-keepalives-in
service tcp-keepalives-out
service timestamps debug datetime msec localtime year
service timestamps log datetime msec localtime year
service password-encryption
service sequence-numbers
hostname BASELINE01
boot-start-marker
boot-end-marker
no ip domain-lookup
ip domain-name diffios.dev
interface FastEthernet0/1
 description Management
 switchport trunk native vlan 777
 switchport trunk allowed vlan 410,411,777
 switchport mode trunk
 switchport nonegotiate
line con 0
 exec-timeout 5 0
 authorization exec CON
 login authentication CON
line vty 0 4
 exec-timeout 5 0
 authorization exec VTY
 login authentication VTY
 transport input telnet ssh
line vty 5 15
 exec-timeout 5 0
 transport input telnet ssh
end"""
    return content


@pytest.fixture
def ignores_file():
    content = """building configuration
hostname
serial number
crypto pki trustpoint
crypto pki certificate
processor board
reload
uptime
current configuration
mac address
version
System restarted at
banner login
banner motd
^end$"""
    return content


@pytest.fixture
def baseline_blocks():
    content = [
        ['boot-end-marker'],
        ['boot-start-marker'],
        ['end'],
        ['hostname BASELINE01'],
        ['interface FastEthernet0/1',
         ' description Management',
         ' switchport trunk native vlan 777',
         ' switchport trunk allowed vlan 410,411,777',
         ' switchport mode trunk',
         ' switchport nonegotiate'],
        ['ip domain-name diffios.dev'],
        ['line con 0',
         ' exec-timeout 5 0',
         ' authorization exec CON',
         ' login authentication CON'],
        ['line vty 0 4',
         ' exec-timeout 5 0',
         ' authorization exec VTY',
         ' login authentication VTY',
         ' transport input telnet ssh'],
        ['line vty 5 15', ' exec-timeout 5 0', ' transport input telnet ssh'],
        ['no ip domain-lookup'],
        ['no service pad'],
        ['service password-encryption'],
        ['service sequence-numbers'],
        ['service tcp-keepalives-in'],
        ['service tcp-keepalives-out'],
        ['service timestamps debug datetime msec localtime year'],
        ['service timestamps log datetime msec localtime year'],
        ['version 15.0']]
    return content


@pytest.fixture
def ignored():
    content = [
        ['end'],
        ['hostname BASELINE01'],
        ['version 15.0']]
    return content


@pytest.fixture
def recorded():
    content = sorted([
        ['no service pad'],
        ['service tcp-keepalives-in'],
        ['service tcp-keepalives-out'],
        ['service timestamps debug datetime msec localtime year'],
        ['service timestamps log datetime msec localtime year'],
        ['service password-encryption'],
        ['service sequence-numbers'],
        ['boot-start-marker'],
        ['boot-end-marker'],
        ['no ip domain-lookup'],
        ['ip domain-name diffios.dev'],
        ['interface FastEthernet0/1',
         ' description Management',
         ' switchport trunk native vlan 777',
         ' switchport trunk allowed vlan 410,411,777',
         ' switchport mode trunk',
         ' switchport nonegotiate'],
        ['line con 0',
         ' exec-timeout 5 0',
         ' authorization exec CON',
         ' login authentication CON'],
        ['line vty 0 4',
         ' exec-timeout 5 0',
         ' authorization exec VTY',
         ' login authentication VTY',
         ' transport input telnet ssh'],
        ['line vty 5 15',
         ' exec-timeout 5 0',
         ' transport input telnet ssh']])
    return content


@pytest.fixture
def baseline_partition():
    Partition = namedtuple("Partition", "ignored recorded")
    bp = Partition(
        ignored=[
            ['banner login ^C'],
            ['banner motd ^C'],
            ['crypto pki certificate chain TP-self-signed-1234567890',
             ' certificate self-signed 01',
             '  1D16574F 1D16574F 1D16574F 1D16574F 1D16574F 1D16574F 1D16574F 1D16574F',
             '  1D16574F 1D16574F 1D16574F 1D16574F 1D16574F 1D16574F 1D16574F 1D16574F',
             '  1D16574F 1D16574F 1D16574F 1D16574F',
             '  \tquit'],
            ['crypto pki trustpoint TP-self-signed-1234567890',
             ' enrollment selfsigned',
             ' subject-name cn=IOS-Self-Signed-Certificate-1234567890',
             ' revocation-check none',
             ' rsakeypair TP-self-signed-1234567890'],
            ['end'],
            ['hostname BASELINE01']],
        recorded=[
            ['#                                                                             #'],
            ['#                                                                             #'],
            ['#                                                                             #'],
            ['#                                   WARNING!!!                                #'],
            ['#                   THIS DEVICE IS PART OF A PRIVATE NETWORK                  #'],
            ['###############################################################################'],
            ['###############################################################################'],
            ['###############################################################################'],
            ['#This system is solely for the use of authorised users for official purposes. #'],
            ['#Use of this system evidences an express consent to such monitoring and       #'],
            ['#You have no expectation of privacy in its use and to ensure that the system  #'],
            ['#agreement that if such monitoring reveals evidence of possible abuse or      #'],
            ['#criminal activity, system personnel may provide the results of such          #'],
            ['#is functioning properly, individuals using this computer system are subject  #'],
            ['#monitoring to appropriate officials.                                         #'],
            ['*                                                                    *'],
            ['*                                                                    *'],
            ['*                                                                    *'],
            ['*                                                                    *'],
            ['* Evidence of unauthorised use collected during monitoring may be    *'],
            ['* If you are not authorised to access this system, terminate this    *'],
            ['* Under the Computer Misuse Act, it is a criminal offence to         *'],
            ['* WARNING. This is a private computer system, unauthorised access to *'],
            ['* and recorded.                                                      *'],
            ['* knowingly access or try to access unauthorised material on this    *'],
            ['* session now.                                                       *'],
            ['* system constitutes consent to monitoring for these purposes.       *'],
            ['* system, or to abuse this system and its data.                      *'],
            ['* this system is prohibited.  All usage of this system is monitored  *'],
            ['* used for administrative, criminal, or other action. Use of this    *'],
            ['**********************************************************************'],
            ['**********************************************************************'],
            ['^C'],
            ['^C'],
            ['aaa accounting dot1x default start-stop group radius'],
            ['aaa accounting exec CON start-stop group radius'],
            ['aaa accounting exec VTY start-stop group radius'],
            ['aaa accounting system default start-stop group radius'],
            ['aaa accounting update periodic 15'],
            ['aaa authentication dot1x default group radius'],
            ['aaa authentication login CON group radius local'],
            ['aaa authentication login VTY group radius local'],
            ['aaa authorization config-commands'],
            ['aaa authorization console'],
            ['aaa authorization exec CON group radius local'],
            ['aaa authorization exec VTY group radius local'],
            ['aaa authorization network default group radius'],
            ['aaa group server radius ISE',
             ' server name xxxxxx12345',
             ' server name yyyyyy67890',
             ' load-balance method least-outstanding'],
            ['aaa new-model'],
            ['aaa server radius dynamic-author',
             ' client 10.20.30.40 server-key 7 xxxxxxxxxxxxxxxxxxxxxx',
             ' client 10.20.30.40 server-key 7 yyyyyyyyyyyyyyyyyyyyyy'],
            ['aaa session-id common'],
            ['authentication critical recovery delay 600'],
            ['authentication mac-move permit'],
            ['boot-end-marker'],
            ['boot-start-marker'],
            ['class-map match-any CONTROL-CLASSIFY',
             '  match access-group name CONTROL-CLASSIFY'],
            ['class-map match-any DEFAULT',
             '  match access-group name DEFAULT-CLASSIFY'],
            ['class-map match-any SCAVENGER-CLASSIFY',
             '  match access-group name SCAVENGER-CLASSIFY'],
            ['class-map match-any TRANSACTIONAL-CLASSIFY',
             '  match access-group name TRANSACTIONAL-CLASSIFY'],
            ['class-map match-any VIDEO-CLASSIFY',
             '  match access-group name VIDEO-CLASSIFY'],
            ['class-map match-any VOICE-CLASSIFY',
             '  match access-group name VOICE-CLASSIFY'],
            ['clock summer-time BST recurring last Sun Mar 2:00 last Sun Oct 2:00'],
            ['dot1x critical eapol'],
            ['dot1x system-auth-control'],
            ['errdisable recovery cause arp-inspection'],
            ['errdisable recovery cause bpduguard'],
            ['errdisable recovery cause channel-misconfig (STP)'],
            ['errdisable recovery cause dhcp-rate-limit'],
            ['errdisable recovery cause dtp-flap'],
            ['errdisable recovery cause gbic-invalid'],
            ['errdisable recovery cause inline-power'],
            ['errdisable recovery cause link-flap'],
            ['errdisable recovery cause loopback'],
            ['errdisable recovery cause mac-limit'],
            ['errdisable recovery cause pagp-flap'],
            ['errdisable recovery cause port-mode-failure'],
            ['errdisable recovery cause pppoe-ia-rate-limit'],
            ['errdisable recovery cause psecure-violation'],
            ['errdisable recovery cause security-violation'],
            ['errdisable recovery cause sfp-config-mismatch'],
            ['errdisable recovery cause small-frame'],
            ['errdisable recovery cause storm-control'],
            ['errdisable recovery cause udld'],
            ['errdisable recovery cause vmps'],
            ['interface FastEthernet0/1',
             ' description Management',
             ' switchport trunk native vlan 777',
             ' switchport trunk allowed vlan 410,411,777',
             ' switchport mode trunk',
             ' switchport nonegotiate',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' storm-control broadcast level 20.00',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/10',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/11',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/12',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/2',
             ' description Management',
             ' switchport trunk native vlan 777',
             ' switchport trunk allowed vlan 410,411,777',
             ' switchport mode trunk',
             ' switchport nonegotiate',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' storm-control broadcast level 20.00',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/3',
             ' description Management',
             ' switchport trunk native vlan 777',
             ' switchport trunk allowed vlan 410,411,777',
             ' switchport mode trunk',
             ' switchport nonegotiate',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' storm-control broadcast level 20.00',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/4',
             ' description Management',
             ' switchport trunk native vlan 777',
             ' switchport trunk allowed vlan 410,411,777',
             ' switchport mode trunk',
             ' switchport nonegotiate',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' storm-control broadcast level 20.00',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/5',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/6',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/7',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/8',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface FastEthernet0/9',
             ' description Data and Voice Access Port',
             ' switchport access vlan 100',
             ' switchport mode access',
             ' switchport nonegotiate',
             ' ip access-group ALLOW-ALL in',
             ' no logging event link-status',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' authentication event fail action next-method',
             ' authentication event server dead action authorize',
             ' authentication event server dead action authorize voice',
             ' authentication event server alive action reinitialize',
             ' authentication host-mode multi-auth',
             ' authentication open',
             ' authentication order dot1x mab',
             ' authentication priority dot1x mab',
             ' authentication port-control auto',
             ' authentication periodic',
             ' authentication timer reauthenticate server',
             ' authentication violation restrict',
             ' mab',
             ' snmp trap mac-notification change added',
             ' no snmp trap link-status',
             ' mls qos trust dscp',
             ' dot1x pae authenticator',
             ' dot1x timeout tx-period 10',
             ' storm-control broadcast level 20.00',
             ' spanning-tree portfast',
             ' spanning-tree bpduguard enable',
             ' service-policy input QOS-CLASSIFY'],
            ['interface GigabitEthernet0/1',
             ' switchport trunk native vlan 778',
             ' switchport trunk allowed vlan 1,100,410,411,501,778,777',
             ' switchport mode trunk',
             ' switchport nonegotiate',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' mls qos trust dscp',
             ' spanning-tree portfast trunk',
             ' spanning-tree bpduguard disable'],
            ['interface GigabitEthernet0/2',
             ' switchport trunk native vlan 778',
             ' switchport trunk allowed vlan 1,100,410,411,501,778,777',
             ' switchport mode trunk',
             ' switchport nonegotiate',
             ' srr-queue bandwidth share 1 30 35 5',
             ' priority-queue out',
             ' mls qos trust dscp',
             ' spanning-tree portfast trunk',
             ' spanning-tree bpduguard disable'],
            ['interface Vlan1', ' no ip address', ' shutdown'],
            ['interface Vlan777', ' ip address 10.20.30.44 255.255.255.0'],
            ['ip access-list extended ALLOW-ALL', ' permit ip any any'],
            ['ip access-list extended CONTROL-CLASSIFY',
             ' permit tcp any any eq 5060',
             ' permit tcp any any eq 5061',
             ' remark CS3/AF31 for Call Signalling,',
             ' permit udp any any eq 5060',
             ' permit udp any any eq 5061',
             ' permit udp any any eq 1719',
             ' permit tcp any any eq 1720',
             ' permit tcp any any range 2000 2002',
             ' deny   ip any any'],
            ['ip access-list extended DEFAULT-CLASSIFY',
             ' permit ip any any'],
            ['ip access-list extended SCAVENGER-CLASSIFY',
             ' permit tcp any 10.20.0.0 0.1.255.255 eq www',
             ' permit tcp any any eq 8080',
             ' permit tcp any any eq ftp',
             ' permit tcp any any eq ftp-data',
             ' permit tcp any any eq 22',
             ' permit tcp any any eq smtp',
             ' permit tcp any any eq 465',
             ' permit tcp any any eq 143',
             ' permit tcp any any eq 993',
             ' permit tcp any any eq pop3',
             ' permit tcp any any eq 995',
             ' deny   ip any any'],
            ['ip access-list extended TRANSACTIONAL-CLASSIFY',
             ' remark AF21 CAPWAP, Cisco ISE Traffic & Other Control & Important Data Such as Citrix.',
             ' permit udp any any eq 1645',
             ' permit udp any any eq 1646',
             ' permit udp any any eq 1812',
             ' permit udp any any eq 1813',
             ' permit udp any any eq snmp',
             ' permit udp any any eq snmptrap',
             ' permit udp any any eq 8905',
             ' permit tcp any any eq 8905',
             ' permit udp any any eq 8909',
             ' permit udp any any eq 1700',
             ' permit udp any any eq 3799',
             ' permit tcp any any eq 8443',
             ' permit udp any any eq 5246',
             ' permit udp any any eq domain',
             ' permit udp any eq bootps any eq bootps',
             ' permit udp any any eq 1494',
             ' permit tcp any any eq 1494',
             ' permit tcp any 10.20.0.0 0.1.255.255 eq 443',
             ' permit tcp any 10.20.0.0 0.1.255.255 eq www',
             ' deny   ip any any'],
            ['ip access-list extended VIDEO-CLASSIFY',
             ' remark AF41',
             ' permit udp any any range 16384 32767 dscp af41',
             ' permit udp any any dscp af41',
             ' deny   ip any any'],
            ['ip access-list extended VOICE-CLASSIFY',
             ' remark EF',
             ' permit udp any any range 16384 32767 dscp ef',
             ' deny   ip any any'],
            ['ip access-list extended VTY-ACCESS',
             ' permit tcp 10.0.0.0 0.255.255.255 any eq 22'],
            ['ip default-gateway 10.20.30.4'],
            ['ip device tracking'],
            ['ip device tracking probe delay 10'],
            ['ip domain-name diffios.dev'],
            ['ip http secure-server'],
            ['ip http server'],
            ['ip name-server 10.20.30.41'],
            ['ip name-server 10.20.30.42'],
            ['ip name-server 10.20.30.43'],
            ['ip radius source-interface Vlan777'],
            ['ip ssh time-out 60'],
            ['ip ssh version 2'],
            ['ip tftp source-interface Vlan777'],
            ['line con 0',
             ' exec-timeout 5 0',
             ' authorization exec CON',
             ' login authentication CON'],
            ['line vty 0 4',
             ' exec-timeout 5 0',
             ' authorization exec VTY',
             ' login authentication VTY',
             ' transport input telnet ssh'],
            ['line vty 5 15',
             ' exec-timeout 5 0',
             ' transport input telnet ssh'],
            ['mls qos'],
            ['mls qos map cos-dscp 0 8 16 24 34 46 48 56'],
            ['mls qos map policed-dscp  0 10 18 26 34 to 8'],
            ['mls qos queue-set output 1 buffers 15 30 35 20'],
            ['mls qos queue-set output 1 threshold 1 100 100 100 100'],
            ['mls qos queue-set output 1 threshold 2 80 90 100 400'],
            ['mls qos queue-set output 1 threshold 3 100 100 100 400'],
            ['mls qos queue-set output 1 threshold 4 60 100 100 400'],
            ['mls qos srr-queue input bandwidth 70 30'],
            ['mls qos srr-queue input dscp-map queue 1 threshold 2 24'],
            ['mls qos srr-queue input dscp-map queue 1 threshold 3 48 56'],
            ['mls qos srr-queue input dscp-map queue 2 threshold 3 32 36 38 40 46'],
            ['mls qos srr-queue input priority-queue 2 bandwidth 30'],
            ['mls qos srr-queue input threshold 1 80 90'],
            ['mls qos srr-queue output dscp-map queue 1 threshold 3 40 46'],
            ['mls qos srr-queue output dscp-map queue 2 threshold 1 16 18 20 22 26 28 30 34'],
            ['mls qos srr-queue output dscp-map queue 2 threshold 1 36 38'],
            ['mls qos srr-queue output dscp-map queue 2 threshold 2 24'],
            ['mls qos srr-queue output dscp-map queue 2 threshold 3 48 56'],
            ['mls qos srr-queue output dscp-map queue 3 threshold 3 0'],
            ['mls qos srr-queue output dscp-map queue 4 threshold 1 8'],
            ['mls qos srr-queue output dscp-map queue 4 threshold 2 10 12 14'],
            ['no aaa accounting system guarantee-first'],
            ['no ip domain-lookup'],
            ['no service pad'],
            ['ntp server 10.20.30.253'],
            ['ntp server 10.20.30.254'],
            ['ntp source Vlan777'],
            ['policy-map QOS-CLASSIFY',
             ' class VOICE-CLASSIFY',
             '   set dscp ef',
             '  police 128000 8000 exceed-action drop',
             ' class VIDEO-CLASSIFY',
             '   set dscp af41',
             '  police 5000000 8000 exceed-action drop',
             ' class TRANSACTIONAL-CLASSIFY',
             '   set dscp af21',
             '  police 10000000 8000 exceed-action policed-dscp-transmit',
             ' class CONTROL-CLASSIFY',
             '   set dscp af31',
             '  police 512000 8000 exceed-action policed-dscp-transmit',
             ' class SCAVENGER-CLASSIFY',
             '   set dscp af11',
             '  police 10000000 8000 exceed-action policed-dscp-transmit',
             ' class DEFAULT',
             '   set dscp default',
             '  police 10000000 8000 exceed-action policed-dscp-transmit'],
            ['radius server xxxxxxxxxxx',
             ' address ipv4 10.20.30.1 auth-port 1812 acct-port 1813',
             ' timeout 3',
             ' automate-tester username testise',
             ' key 7 xxxxxxxxxxxxxxxxxxxxxx'],
            ['radius server yyyyyyyyyyy',
             ' address ipv4 10.20.30.3 auth-port 1812 acct-port 1813',
             ' timeout 3',
             ' automate-tester username testise',
             ' key 7 yyyyyyyyyyyyyyyyyyyyyy'],
            ['radius-server attribute 25 access-request include'],
            ['radius-server attribute 6 on-for-login-auth'],
            ['radius-server attribute 6 support-multiple'],
            ['radius-server attribute 8 include-in-access-req'],
            ['radius-server dead-criteria time 30 tries 3'],
            ['radius-server deadtime 10'],
            ['radius-server load-balance method least-outstanding'],
            ['radius-server timeout 15'],
            ['radius-server vsa send accounting'],
            ['radius-server vsa send authentication'],
            ['service password-encryption'],
            ['service sequence-numbers'],
            ['service tcp-keepalives-in'],
            ['service tcp-keepalives-out'],
            ['service timestamps debug datetime msec localtime year'],
            ['service timestamps log datetime msec localtime year'],
            ['snmp-server community Diffios! RW'],
            ['snmp-server contact Network Team $VARIABLE'],
            ['snmp-server enable traps auth-framework sec-violation'],
            ['snmp-server enable traps bridge newroot topologychange'],
            ['snmp-server enable traps cluster'],
            ['snmp-server enable traps config'],
            ['snmp-server enable traps config-copy'],
            ['snmp-server enable traps config-ctid'],
            ['snmp-server enable traps cpu threshold'],
            ['snmp-server enable traps dot1x auth-fail-vlan guest-vlan no-auth-fail-vlan no-guest-vlan'],
            ['snmp-server enable traps energywise'],
            ['snmp-server enable traps entity'],
            ['snmp-server enable traps envmon fan shutdown supply temperature status'],
            ['snmp-server enable traps errdisable'],
            ['snmp-server enable traps flash insertion removal'],
            ['snmp-server enable traps fru-ctrl'],
            ['snmp-server enable traps license'],
            ['snmp-server enable traps mac-notification change move threshold'],
            ['snmp-server enable traps port-security'],
            ['snmp-server enable traps power-ethernet group 1'],
            ['snmp-server enable traps power-ethernet police'],
            ['snmp-server enable traps rep'],
            ['snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart'],
            ['snmp-server enable traps stpx inconsistency root-inconsistency loop-inconsistency'],
            ['snmp-server enable traps syslog'],
            ['snmp-server enable traps transceiver all'],
            ['snmp-server enable traps tty'],
            ['snmp-server enable traps vlan-membership'],
            ['snmp-server enable traps vlancreate'],
            ['snmp-server enable traps vlandelete'],
            ['snmp-server enable traps vstack'],
            ['snmp-server enable traps vtp'],
            ['snmp-server group MON v3 auth'],
            ['snmp-server group MON v3 priv'],
            ['snmp-server location $VARIABLE'],
            ['spanning-tree extend system-id'],
            ['spanning-tree mode rapid-pvst'],
            ['spanning-tree vlan 1,100,410-411,501,777 priority 4096'],
            ['system mtu routing 1500'],
            ['udld enable'],
            ['username diffios privilege 5 secret 5 xxxxxxxxxxxxxxxxxxxxxxx'],
            ['version 15.0'],
            ['vlan 100', ' name data'],
            ['vlan 410', ' name wifi'],
            ['vlan 411', ' name guest'],
            ['vlan 501', ' name wan'],
            ['vlan 770', ' name shut'],
            ['vlan 777', ' name management'],
            ['vlan 778', ' name native'],
            ['vlan internal allocation policy ascending'],
            ['vtp domain diffios'],
            ['vtp mode transparent']])
    return bp


@pytest.fixture
def int_baseline():
    return """interface FastEthernet0/5
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


@pytest.fixture
def int_comparison():
    return """interface FastEthernet0/5
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


@pytest.fixture
def aaa_baseline():
    return """aaa group server radius ISE
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


@pytest.fixture
def aaa_comparison():
    return """aaa group server radius ISE
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
