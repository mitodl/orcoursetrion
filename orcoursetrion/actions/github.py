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

    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubUnknownError
        orcoursetrion.lib.GitHubNoTeamFound
        orcoursetrion.lib.GitHubRepoExists
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


def create_xml_repo(course, term, team, members=None, description=None):
    """Creates a course repo at
    :py:const:`~orcoursetrion.config.ORC_GH_API_URL` with key
    :py:const:`~orcoursetrion.config.ORC_GH_OAUTH2_TOKEN` and at
    organization :py:const:`~orcoursetrion.config.ORC_XML_ORG`, and
    with ``team`` as a collaborator (Along with
    :py:const:`~orcoursetrion.config.ORC_XML_DEPLOY_TEAM`).

    If ``members`` is provided, the ``team`` membership will be
    *replaced* with the members listed.  It will also create the team if
    it doesn't already exist regardless of the value of ``members``.

    This also adds a github Web hook to the course development
    environment `gitreload <https://github.com/mitodl/gitreload>`_
    server via
    :py:const:`~orcoursetrion.config.ORC_STAGING_GITRELOAD`.

    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubUnknownError
        orcoursetrion.lib.GitHubNoTeamFound
        orcoursetrion.lib.GitHubRepoExists
    Args:
        course (str): Course name to be used to name repo (i.e. 6.004r)
        term (str): Term the course is expected to run (i.e. 2015_Spring)
        team (str): Name of an organizational team that already exists to
                    add read/write access to this repo.
        members (list): Exclusive list of usernames that should be on the team.
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
    repo = github.create_repo(config.ORC_XML_ORG, repo_name, description)
    # Add to the deployment team
    github.add_team_repo(
        config.ORC_XML_ORG, repo_name, config.ORC_XML_DEPLOY_TEAM
    )
    # Setup the passed in team
    github.put_team(config.ORC_XML_ORG, team, False, members)
    github.add_team_repo(config.ORC_XML_ORG, repo_name, team)

    # Add the hook
    github.add_web_hook(
        config.ORC_XML_ORG, repo_name, config.ORC_STAGING_GITRELOAD
    )
    return repo


def put_team(org, team, read_only, members):
    """Create or update a team with the list of ``members``.

    If ``members`` is None, the team will be created if it doesn't
    exist, but membership will not be changed.

    Args:
        org (str): Organization that owns/should own the team.
        team (str): Name of the team.
        read_only (bool): True if pull access, False if push access
        members (list): Exclusive list of usernames that should be on the team.
    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubUnknownError
        orcoursetrion.lib.GitHubRepoExists
    Returns:
        dict: Github team dictionary
                (https://developer.github.com/v3/orgs/teams/#response-1)

    """
    github = GitHub(config.ORC_GH_API_URL, config.ORC_GH_OAUTH2_TOKEN)
    team = github.put_team(org, team, read_only, members)
    return team
