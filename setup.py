# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


with open(path.join(here, 'LICENSE'), encoding='utf-8') as f:
    license = f.read()

setup(
    name='diffios',
    version='0.0.2',
    description='Compare Cisco device configurations against a baseline.',
    long_description=long_description,
    author='Rob Phoenix',
    author_email='rob@robphoenix.com',
    url='https://github.com/robphoenix/diffios',
    license=license,
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Network Engineers',
        'Topic :: Network Automation :: Configuration Management',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cisco configuration management',
    packages=find_packages(exclude=('tests', 'docs'))
)
