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
    # GitHub API Key
    ('ORC_GH_OAUTH2_TOKEN', None),

    # GitHub API URL
    ('ORC_GH_API_URL', 'https://github.mit.edu/api/v3/'),

    # Course repo prefix
    ('ORC_COURSE_PREFIX', 'content-mit'),

    # Org to use for Export Repos
    ('ORC_STUDIO_ORG', 'MITx-Studio2LMS'),

    # Deployment team for studio
    ('ORC_STUDIO_DEPLOY_TEAM', 'mitx-studio-export'),
]
for key in CONFIG_KEYS:
    value = primary_config.get(key[0], fallback_config.get(key, key[1]))
    vars()[key[0]] = value
