#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package installer for orcoursetrion
"""
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test


VERSION = __import__('orcoursetrion').VERSION

with open('README.rst') as readme:
    README = readme.read()

with open('test_requirements.txt') as test_reqs:
    tests_require = test_reqs.readlines(),


class PyTest(test):
    """
    Test runner for package.
    """
    user_options = test.user_options[:]
    user_options += [
        ('coverage', 'C', 'Produce a coverage report for orcoursetrion'),
        ('pep8', 'P', 'Produce a pep8 report for orcoursetrion'),
        ('flakes', 'F', 'Produce a flakes report for orcoursetrion'),

    ]
    coverage = None
    pep8 = None
    flakes = None
    test_suite = False
    test_args = []

    def initialize_options(self):
        test.initialize_options(self)

    def finalize_options(self):
        test.finalize_options(self)
        self.test_suite = True
        self.test_args = []
        if self.coverage:
            self.test_args.append('--cov')
            self.test_args.append('orcoursetrion')
        if self.pep8:
            self.test_args.append('--pep8')
        if self.flakes:
            self.test_args.append('--flakes')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        # Needed in order for pytest_cache to load properly
        # Alternate fix: import pytest_cache and pass to pytest.main
        import _pytest.config

        pm = _pytest.config.get_plugin_manager()
        pm.consider_setuptools_entrypoints()
        pm.config.option.color = True
        errno = pytest.main(self.test_args)
        sys.exit(errno)


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
    test_suite="orcoursetrion.tests",
    tests_require=tests_require,
    cmdclass={"test": PyTest},
)
