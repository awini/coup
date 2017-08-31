#!/usr/bin/env python
from distutils.core import setup

setup(
    name='coup',
    version='0.0.46',
    description='BP Compas Coup Project',
    author='BP Compas Andrew Andreev-Krasnoselsky',
    author_email='aa.veter@gmail.com',
    packages=['coup', 'coup.objecter_core', 'coup.swift', 'coup.py', 'coup.php',
              'coup.common', 'coup.js'],
    scripts=[],
    package_data={'coup': [
        'external/highlight/styles/*.css',
        'external/highlight/highlight.pack.js',
        'common/*.abc'
    ]},
)