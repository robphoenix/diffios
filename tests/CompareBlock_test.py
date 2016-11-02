#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

import pytest

sys.path.append(os.path.abspath("."))

from diffios import CompareBlock


def test_True_when_single_line_block_is_present():
    block = 'aaa authentication dot1x default group radius'
    config = ''' aaa authentication login vty group radius local
aaa authentication login con group radius local
aaa authentication dot1x default group radius
aaa authorization console'''
    cb = CompareBlock(block, config)
    assert cb.present is True


def test_False_when_single_line_block_is_not_present():
    block = 'aaa authorization exec VTY group radius local'
    config = ''' aaa authentication login vty group radius local
aaa authentication login con group radius local
aaa authentication dot1x default group radius
aaa authorization console'''
    cb = CompareBlock(block, config)
    assert cb.present is False
