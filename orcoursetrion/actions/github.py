# -*- coding: utf-8 -*-
"""
Github based actions for orchestrion to take. i.e. "Create a studio
course export repo", "Add course team to github", etc
"""
from orcoursetrion import config
from orcoursetrion.lib import GitHub


def create_export_repo(course, term, description=None):
    """Creates a course repo at
    :py:const:`~orcoursetrion.config.ORC_GH_API_URL` with key
    :py:const:`~orcoursetrion.config.ORC_GH_OAUTH2_TOKEN`, at
    organization :py:const:`~orcoursetrion.config.ORC_STUDIO_ORG`,
    and with collabarator
    :py:const:`~orcoursetrion.config.ORC_STUDIO_DEPLOY_TEAM`

    Args:
        course (str): Course name to be used to name repo (i.e. 6.004r)
        term (str): Term the course is expected to run (i.e. 2015_Spring)
        description (str): Optional description for repo to show up on github
    Returns:
        dict: Github dictionary of a repo
                (https://developer.github.com/v3/repos/#create)

    """

    github = GitHub(config.ORC_GH_API_URL, config.ORC_GH_OAUTH2_TOKEN)
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.ORC_COURSE_PREFIX,
        course=course.replace('.', ''),
        term=term
    )
    repo = github.create_repo(config.ORC_STUDIO_ORG, repo_name, description)

    # Add repo to team
    github.add_team_repo(
        config.ORC_STUDIO_ORG, repo_name, config.ORC_STUDIO_DEPLOY_TEAM
    )
    return repo
