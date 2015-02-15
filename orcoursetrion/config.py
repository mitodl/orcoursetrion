# -*- coding: utf-8 -*-
"""
Configuration needed for Orchestrion to function (i.e. API keys)
"""
import os

prefer_django = True
try:
    from django.conf import settings
except ImportError:
    prefer_django = False

if prefer_django:
    primary_config = settings
    fallback_config = os.environ
else:
    primary_config = os.environ
    fallback_config = os.environ

CONFIG_KEYS = [
    ('GH_API_KEY', None),  # GitHub API Key
    ('GH_API_URL', 'https://github.mit.edu/api/v3/'),  # GitHub API URL
    ('COURSE_PREFIX', 'content-mit'),  # Course repo prefix
    ('STUDIO_ORG', 'MITx-Studio2LMS'),  # Organization to use for Export Repos
]
for key in CONFIG_KEYS:
    value = primary_config.get(key[0], fallback_config.get(key, key[1]))
    vars()[key[0]] = value
