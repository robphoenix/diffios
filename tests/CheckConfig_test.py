#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# import pytest

sys.path.append(os.path.abspath("."))

from diffios import CheckConfig


def test_parent_and_children_of_single_line_block():
    block = ['aaa authentication dot1x default group radius']
    config = [['aaa authentication login vty group radius local'],
              ['aaa authentication login con group radius local'],
              ['aaa authentication dot1x default group radius'],
              ['aaa authorization console']]
    cb = CheckConfig(block, config)
    assert cb.parent == block[0]
    assert cb.children == []


def test_parent_and_children_of_multiple_line_block():
    block = ['interface Vlan1',
             ' no ip address',
             ' shutdown']
    config = [['interface Vlan1',
               ' no ip address',
               ' shutdown']]
    cb = CheckConfig(block, config)
    assert cb.parent == block[0]
    assert cb.children == block[1:]


def test_parent_child_config_dict():
    block = ['interface Vlan1',
             ' no ip address',
             ' shutdown']
    config = [['interface Vlan1',
               ' no ip address',
               ' shutdown'],
              ['ip default-gateway 192.168.0.1']]
    expected = {'interface Vlan1': [' no ip address', ' shutdown'],
                'ip default-gateway 192.168.0.1': []}
    cb = CheckConfig(block, config)
    assert expected == cb._parent_child_config_dict()


def test_single_line_block_is_present():
    block = ['aaa authentication dot1x default group radius']
    config = [['aaa authentication login vty group radius local'],
              ['aaa authentication login con group radius local'],
              ['aaa authentication dot1x default group radius'],
              ['aaa authorization console']]
    cb = CheckConfig(block, config)
    assert cb.present == block
    assert cb.not_present == []


def test_single_line_block_is_not_present():
    block = ['aaa authorization exec VTY group radius local']
    config = [['aaa authentication login vty group radius local'],
              ['aaa authentication login con group radius local'],
              ['aaa authentication dot1x default group radius'],
              ['aaa authorization console']]
    cb = CheckConfig(block, config)
    assert cb.present == []
    assert cb.not_present == block


def test_multiple_line_block_is_same_as_config():
    block = ['interface Vlan1',
             ' no ip address',
             ' shutdown']
    config = [['interface Vlan1',
               ' no ip address',
               ' shutdown']]
    cb = CheckConfig(block, config)
    assert cb.present == block
    assert cb.not_present == []


# def test_True_when_multiple_line_block_is_present_in_config():
    # block = ['interface Vlan1',
             # ' no ip address',
             # ' shutdown']
    # config = [['interface Vlan1',
               # ' no ip address',
               # ' shutdown'],
              # ['ip default-gateway 192.168.0.1'],
              # ['ip http server'],
              # ['ip http secure-server']]
    # cb = CheckConfig(block, config)
    # assert cb.present is True


# def test_True_when_
