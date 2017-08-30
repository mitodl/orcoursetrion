# -*- coding: utf-8 -*-
"""
Test core functionality
"""
import unittest

import semantic_version


class TestCore(unittest.TestCase):
    """Test common and core components to the package.
    """
    # pylint: disable=too-few-public-methods

    @staticmethod
    def test_version():
        """Validate version matches proper format"""
        import orcoursetrion
        semantic_version.Version(orcoursetrion.VERSION)
