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
    author='MIT Office of Digital Learning',
    author_email='odl-engineering@mit.edu',
    url="http://orcoursetrion.rtfd.com",
    description=("Automatic course provisioning for the edx-platform using "
                 "github and zendesk."),
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
    entry_points={'console_scripts': [
        'orcoursetrion = orcoursetrion.cmd:execute',
    ]},
    zip_safe=True,
)
