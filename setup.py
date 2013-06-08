#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pyixp',
    version='0.0.1',
    description='Client library for the 9p protocol',
    author='Ben Mather',
    author_email='bwhmather@bwhmather.com',
    url='http://github.org/bwhmather/pyixp',
    packages=['pyixp'],
    license='MIT',
    install_requires=[
        'construct',
    ],
)
