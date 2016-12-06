#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
try:
    from unittest import mock
except ImportError:
    from mock import mock

import pytest

sys.path.insert(0, os.path.abspath('..'))

from diffios import DiffiosConfig, Baseline


def test_baseline_property_is_instance_of_DiffiosConfig():
    config = ['hostname ROUTER']
    baseline = Baseline(config, [])
    assert isinstance(baseline.config, DiffiosConfig)
