#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from unittest import mock

import pytest

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.abspath("."))

from diffios import DiffiosConfig


def test_raises_error_if_config_not_given():
    with pytest.raises(TypeError):
        DiffiosConfig()


def test_raises_error_if_provided_ignore_file_does_not_exist(config):
    with pytest.raises(RuntimeError):
        DiffiosConfig(config, ignores='file_that_does_not_exist')


@mock.patch('diffios.os.path')
def test_ignores_is_empty_list_if_no_default_ignore_file(mock_path):
    mock_path.exists.return_value = False
    config = ['hostname ROUTER']
    assert DiffiosConfig(config).ignores == []


def test_raises_error_if_not_valid_config_file():
    with pytest.raises(RuntimeError):
        DiffiosConfig('file_that_does_not_exist')


def test_uses_default_ignores_file_if_it_exists(config):
    with open(os.path.join(os.getcwd(), 'diffios_ignore')) as i:
        ignores = [l.strip().lower() for l in i]
    assert DiffiosConfig(config).ignores == ignores


def test_config(dc, config):
    pytest.skip('config property now removes invalid lines')
    expected = [l.rstrip() for l in open(config).readlines()]
    assert expected, dc.config


def test_hostname(dc):
    assert "BASELINE01" == dc.hostname


def test_blocks(dc, baseline_blocks):
    assert baseline_blocks == dc.config_blocks


def test_ignore_lines(dc):
    ignore_file = open("test_diffios_ignore").readlines()
    expected = [l.strip().lower() for l in ignore_file]
    assert expected == dc.ignores


def test_ignored(dc, baseline_partition):
    expected = baseline_partition.ignored
    assert expected == dc.ignored


def test_recorded(dc, baseline_partition):
    expected = baseline_partition.recorded
    assert expected == dc.recorded


def test_parent_line_is_ignored():
    config = ['!', 'hostname ROUTER']
    ignores = ['hostname']
    d = DiffiosConfig(config=config, ignores=ignores)
    assert d.config == ['hostname ROUTER']
    assert d.recorded == []
    assert d.ignored == [['hostname ROUTER']]


def test_child_line_is_ignored():
    config = [
        '!',
        'interface FastEthernet0/1',
        ' description **Link to Core**',
        ' ip address 192.168.0.1 255.255.255.0',
        '!'
    ]
    ignores = [' description']
    d = DiffiosConfig(config=config, ignores=ignores)
    assert d.config == [
        'interface FastEthernet0/1',
        ' description **Link to Core**',
        ' ip address 192.168.0.1 255.255.255.0'
    ]
    assert d.recorded == [['interface FastEthernet0/1',
                           ' ip address 192.168.0.1 255.255.255.0']]
    assert d.ignored == [[' description **Link to Core**']]


def test_whole_block_is_ignored():
    config = [
        'hostname ROUTER',
        '!',
        'interface FastEthernet0/1',
        ' description **Link to Core**',
        ' ip address 192.168.0.1 255.255.255.0',
        '!'
    ]
    ignores = ['fastethernet0/1']
    d = DiffiosConfig(config=config, ignores=ignores)
    assert d.config == [
        'hostname ROUTER',
        'interface FastEthernet0/1',
        ' description **Link to Core**',
        ' ip address 192.168.0.1 255.255.255.0',
    ]
    assert d.ignored == [[
        'interface FastEthernet0/1',
        ' description **Link to Core**',
        ' ip address 192.168.0.1 255.255.255.0',
    ]]
    assert d.recorded == [['hostname ROUTER']]
