# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='diffios',
    version='0.0.1',
    description='Diff Cisco device configurations.',
    long_description=readme,
    author='Rob Phoenix',
    author_email='rob@robphoenix.com',
    url='https://github.com/robphoenix/diffios',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
