# -*- coding: utf-8 -*-
# Because pylint doesn't do dynamic attributes for orcoursetrion.config
# pylint: disable=no-member
"""
Github based actions for orchestrion to take. i.e. "Create a studio
course export repo", "Add course team to github", etc
"""
from orcoursetrion import config
from orcoursetrion.lib import GitHub

COMMITTER = {'email': config.ORC_GH_EMAIL, 'name': config.ORC_GH_NAME}
GITIGNORE_CONTENTS = '''
drafts/
'''
GITIGNORE_MESSAGE = 'Automatic .gitignore from Orcoursetrion'
GITIGNORE_PATH = '.gitignore'


def create_export_repo(course, term, description=None):
    """Creates a studio based course repo at
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

    # Add .gitignore file
    github.add_repo_file(
        org=config.ORC_STUDIO_ORG,
        repo=repo_name,
        committer=COMMITTER,
        message=GITIGNORE_MESSAGE,
        path=GITIGNORE_PATH,
        contents=GITIGNORE_CONTENTS
    )
    
    # Add initial course.xml file
    github.add_repo_file(
        org=config.ORC_STUDIO_ORG,
        repo=repo_name,
        committer=COMMITTER,
        message='initial commit of course.xml with term "{term}"'.format(term=term),
        path="course.xml",
        contents='<course url_name="{term}" org="MITx" course="{course}"/>\n'.format(term=term,course=course) 
    )

    return repo


def rerun_studio(course, term, new_term, description=None):
    """Run any actions needed to re-run a Studio course.

    This will remove the hooks from the specified term, and then create a new
    export repo for the ``new_term``.  It finds the repo based on
    :py:const:`~orcoursetrion.config.ORC_STUDIO_ORG` as the organization,
    :py:const:`~orcoursetrion.config.ORC_COURSE_PREFIX` as the prefix,
    replacing all the dots in ``course`` and appending "-``term``".

    Args:
        course (str): Course name to be used to name repo (i.e. 6.004r)
        term (str): Term the course is last run (i.e. 2015_Spring)
        new_term (str): Term the course is expected to run
            again (i.e. 2018_Spring)
        description (str): Optional description for repo to show up on github
    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubRepoDoesNotExist
        orcoursetrion.lib.GitHubUnknownError
    Returns:
        dict: Github dictionary of the newly created repo
                (https://developer.github.com/v3/repos/#create)

    """
    github = GitHub(config.ORC_GH_API_URL, config.ORC_GH_OAUTH2_TOKEN)

    # Find and clean up the old
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.ORC_COURSE_PREFIX,
        course=course.replace('.', ''),
        term=term
    )
    github.delete_web_hooks(config.ORC_STUDIO_ORG, repo_name)

    # Name the new and create it
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.ORC_COURSE_PREFIX,
        course=course.replace('.', ''),
        term=new_term
    )
    repo = github.create_repo(config.ORC_STUDIO_ORG, repo_name, description)

    # Add repo to team
    github.add_team_repo(
        config.ORC_STUDIO_ORG, repo_name, config.ORC_STUDIO_DEPLOY_TEAM
    )
    # Add .gitignore file
    github.add_repo_file(
        org=config.ORC_STUDIO_ORG,
        repo=repo_name,
        committer=COMMITTER,
        message=GITIGNORE_MESSAGE,
        path=GITIGNORE_PATH,
        contents=GITIGNORE_CONTENTS
    )
    return repo


def release_studio(course, term):
    """Moves a studio course to be ready for production.

    Currently this will just add a hook to the production server, but
    it will eventually take care of everything else needed for a
    transfer as well.

    Args:
        course (str): Course name of the repo to release to production
                      (i.e. 6.001)
        term (str): Term the course is currently running in (i.e. 2015_Spring)
    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubUnknownError
    Returns:
        None: Nothing returned, raises on failure
    """
    github = GitHub(config.ORC_GH_API_URL, config.ORC_GH_OAUTH2_TOKEN)
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.ORC_COURSE_PREFIX,
        course=course.replace('.', ''),
        term=term
    )
    # Add the hook
    github.add_web_hook(
        config.ORC_STUDIO_ORG, repo_name, config.ORC_PRODUCTION_GITRELOAD
    )


def create_xml_repo(course, term, team=None, members=None, description=None):
    """Creates a course repo at
    :py:const:`~orcoursetrion.config.ORC_GH_API_URL` with key
    :py:const:`~orcoursetrion.config.ORC_GH_OAUTH2_TOKEN` and at
    organization :py:const:`~orcoursetrion.config.ORC_XML_ORG`, and
    with ``team`` as a collaborator (Along with
    :py:const:`~orcoursetrion.config.ORC_XML_DEPLOY_TEAM`).

    If ``team`` is not provided, then it will be generated with
    :py:const:`~orcoursetrion.config.ORC_COURSE_PREFIX`, ``course``,
    and ``term``

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

    # Team matches repo_name if no team is passed.
    if team is None:
        team = repo_name

    # Setup the team
    github.put_team(config.ORC_XML_ORG, team, False, members)
    github.add_team_repo(config.ORC_XML_ORG, repo_name, team)

    # Add the hook
    github.add_web_hook(
        config.ORC_XML_ORG, repo_name, config.ORC_STAGING_GITRELOAD
    )
    return repo


def rerun_xml(course, term):
    """Run any actions needed to re-run an XML course.

    Currently this only deletes the Web hooks, but eventually it will
    also copy the repo to a history clean one, and setup up that new
    one with hooks. It finds the repo based on
    :py:const:`~orcoursetrion.config.ORC_XML_ORG` as the organization,
    :py:const:`~orcoursetrion.config.ORC_COURSE_PREFIX` as the prefix,
    replacing all the dots in ``course`` and appending "-``term``".

    Args:
        course (str): Course name to be used to name repo (i.e. 6.004r)
        term (str): Term the course is expected to run (i.e. 2015_Spring)
    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubUnknownError
    Returns:
        int: Number of hooks removed

    """
    github = GitHub(config.ORC_GH_API_URL, config.ORC_GH_OAUTH2_TOKEN)
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.ORC_COURSE_PREFIX,
        course=course.replace('.', ''),
        term=term
    )
    return github.delete_web_hooks(config.ORC_XML_ORG, repo_name)


def release_xml(course, term):
    """Moves an XML course to be ready for production.

    Currently this will just add a hook to the production server, but
    it will eventually take care of everything else needed for a
    transfer as well (i.e. making live branch, import it to lms...).

    Args:
        course (str): Course name of the repo to release to production
                      (i.e. 6.001)
        term (str): Term the course is currently running in (i.e. 2015_Spring)
    Raises:
        requests.RequestException
        orcoursetrion.lib.GitHubUnknownError
    Returns:
        None: Nothing returned, raises on failure
    """
    github = GitHub(config.ORC_GH_API_URL, config.ORC_GH_OAUTH2_TOKEN)
    repo_name = '{prefix}-{course}-{term}'.format(
        prefix=config.ORC_COURSE_PREFIX,
        course=course.replace('.', ''),
        term=term
    )
    # Add the hook
    github.add_web_hook(
        config.ORC_XML_ORG, repo_name, config.ORC_PRODUCTION_GITRELOAD
    )


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
