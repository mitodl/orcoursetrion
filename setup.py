#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package installer for orcoursetrion
"""
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as testcommand


VERSION = __import__('orcoursetrion').VERSION

with open('README.rst') as readme:
    README = readme.read()

with open('test_requirements.txt') as test_reqs:
    TESTS_REQUIRE = test_reqs.readlines(),


class PyTest(testcommand):
    """PyTest class to enable running `python setup.py test`."""
    user_options = testcommand.user_options[:]
    user_options += [
        ('coverage', 'C', 'Produce a coverage report for orcoursetrion'),
        ('pep8', 'P', 'Produce a pep8 report for orcoursetrion'),
        ('pylint', 'l', 'Produce a pylint report for orcoursetrion'),
    ]
    coverage = None
    pep8 = None
    lint = None
    test_suite = False
    test_args = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        self.test_suite = True
        self.test_args = []
        if self.coverage:
            self.test_args.extend(['--cov', 'orcoursetrion'])
        if self.pep8:
            self.test_args.append('--pep8')
        if self.lint:
            self.test_args.append('--lint')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        # Needed in order for pytest_cache to load properly
        # Alternate fix: import pytest_cache and pass to pytest.main
        import _pytest.config

        plugin_manager = _pytest.config.get_plugin_manager()
        plugin_manager.consider_setuptools_entrypoints()
        sys.exit(pytest.main(self.test_args))


setup(
    name='orcoursetrion',
    version=VERSION,
    packages=find_packages(),
    package_data={},
    license='BSD Simplified',
    author='MIT Office of Digital Learning',
    author_email='odl-engineering@mit.edu',
    url="http://orcoursetrion.rtfd.org",
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
        'requests>=2.4.2',
        'sh>=1.11',
        ],
    entry_points={'console_scripts': [
        'orcoursetrion = orcoursetrion.cmd:execute',
    ]},
    zip_safe=True,
    test_suite="orcoursetrion.tests",
    tests_require=TESTS_REQUIRE,
    cmdclass={"test": PyTest},
)
