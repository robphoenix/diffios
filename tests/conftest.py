#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pytest


sys.path.insert(0, os.path.abspath('../diffios'))

from diffios import DiffiosConfig


@pytest.fixture
def config():
    configs_dir = os.path.abspath(os.path.join("tests", "configs"))
    return os.path.join(configs_dir, "baseline.conf")


@pytest.fixture
def dc():
    return DiffiosConfig(config(), ignores=ignores_file())


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
def int_baseline():
    return """interface FastEthernet0/5
 description {{ description }}
 switchport access vlan 101
 switchport mode access
 switchport nonegotiate""".splitlines()


@pytest.fixture
def int_comparison():
    return """interface FastEthernet0/5
 description Data and Voice Access Port
 switchport access vlan 101
 switchport trunk native vlan 999
 switchport trunk allowed vlan 510,511,999
 switchport mode trunk
 switchport nonegotiate""".split('\n')


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
