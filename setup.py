# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_description = """
diffios is a Python library which provides a way to compare Cisco IOS configurations
against a baseline template, and generate an output detailing the differences
between them.
"""

setup(
    name='diffios',
    version='0.0.5',
    description='Compare Cisco device configurations against a baseline.',
    long_description=long_description,
    author='Rob Phoenix',
    author_email='rob@robphoenix.com',
    license='MIT',
    url='https://github.com/robphoenix/diffios',
    classifiers=[
        'Development Status :: 4 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=('tests', 'docs')))
