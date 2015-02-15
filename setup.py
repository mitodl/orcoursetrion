#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package installer for orcoursetrion
"""

from setuptools import setup, find_packages


VERSION = __import__('orcoursetrion').VERSION

with open('README.rst') as readme:
    README = readme.read()

setup(
    name='orcoursetrion',
    version=VERSION,
    packages=find_packages(),
    package_data={},
    license='BSD Simplified',
    author='Carson Gee',
    author_email='x@carsongee.com',
    url="http://github.com/carsongee/archelon",
    description=("Client connected to archelonc for Web shell history"),
    long_description=README,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=[
        'requests',
        ],
    entry_points={},
    zip_safe=True,
)
