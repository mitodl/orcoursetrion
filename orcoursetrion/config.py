# -*- coding: utf-8 -*-
"""
Configuration needed for Orchestrion to function (i.e. API keys)
"""
import os


CONFIG_KEYS = {
    # GitHub API Key
    'ORC_GH_OAUTH2_TOKEN': None,

    # GitHub API URL
    'ORC_GH_API_URL': 'https://github.mit.edu/api/v3/',

    # GitHub Committer Name
    'ORC_GH_NAME': 'Orcoursetrion',

    # GitHub Committer Email
    'ORC_GH_EMAIL': 'orcoursetrion@example.com',

    # Course repo prefix
    'ORC_COURSE_PREFIX': 'content-mit',

    # Org to use for Export Repos
    'ORC_STUDIO_ORG': 'MITx-Studio2LMS',

    # Deployment team for studio
    'ORC_STUDIO_DEPLOY_TEAM': 'mitx-studio-export',

    # Org to use for XML/latex2edx courses
    'ORC_XML_ORG': 'mitx',

    # Deployment team for XML/latex2edx
    'ORC_XML_DEPLOY_TEAM': 'mitx-content-deployment',

    # Web hook URL including basic auth for course development LMS
    'ORC_STAGING_GITRELOAD': None,

    # Web hook URL (including basic auth) for course production LMS
    'ORC_PRODUCTION_GITRELOAD': None,
}


def configure():
    """
    Configure the application using os.environ.
    """
    config = os.environ
    for key, default_value in list(CONFIG_KEYS.items()):        
        value = config.get(key,default_value)
        globals()[key] = value

configure()
