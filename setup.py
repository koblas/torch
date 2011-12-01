#!/usr/bin/env python

from setuptools import setup

setup(
    name='Torch',
    version='0.1',
    description='Tornado Exention Libraries',
    author='David Koblas',
    author_email='david@koblas.com',
    url='http://github.com/koblas/torch',
    #package_dir = {'torch' : 'py/thistle' },
    packages=['torch'],
    test_suite='test',
)

