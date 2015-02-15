# -*- coding: utf-8 -*-
"""
Github based actions for orchestrion to take. i.e. "Create a studio course export
repo", "Add course team to github", etc
"""
from orcoursetrion import config
from orcoursetrion.lib import GitHub, GitHubRepoExists, GitHubUnknownError

def create_export_repo(course, term, description=None):
    """Creates a course repo at
    :py:const:`orcoursetrion.config.GH_API_URL` with key
    :py:const:`orcoursetrion.config.GH_API_KEY` and at organization
    :py:const:`orcoursetrion.config.STUDIO_ORG`.

    Args:
        course (str): Course name to be used to name repo (i.e. 6.004r)
        term (str): Term the course is expected to run (i.e. 2015_Spring)
        description (str): Optional description for repo to show up on github
    Returns:
        dict: Github dictionary of a repo
                (https://developer.github.com/v3/repos/#create)
    """

    github = GitHub(config.GH_API_URL, config.GH_API_KEY)
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.COURSE_PREFIX,
        course=course.replace('.',''),
        term=term
    )
    repo = github.create_repo(config.STUDIO_ORG, repo_name, description)
    return repo
