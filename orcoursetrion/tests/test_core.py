# -*- coding: utf-8 -*-
"""
Test core functionality
"""
import unittest

import semantic_version


class TestCore(unittest.TestCase):
    """Test common and core components to the package.
    """

    def test_version(self):
        """Validate version matches proper format"""
        # Will raise ValueError if not a semantic version
        import orcoursetrion
        semantic_version.Version(orcoursetrion.VERSION)
