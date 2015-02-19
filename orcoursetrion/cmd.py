# -*- coding: utf-8 -*-
"""
Command line interface to orchestrion
"""
from __future__ import print_function
import argparse


from orcoursetrion import actions


def run_create_export_repo(args):
    """Run the create_export_repo action using args"""
    repo = actions.create_export_repo(args.course, args.term, args.description)
    print(
        'Newly created repository for exports created at {0}'.format(
            repo['html_url']
        )
    )


def run_create_xml_repo(args):
    """Run the create_xml_repo action using args"""
    repo = actions.create_xml_repo(
        args.course, args.term, args.team, args.description
    )
    print(
        'Newly created repository for XML course created at {0}'.format(
            repo['html_url']
        )
    )


def execute():
    """Execute command line orcoursetrion actions.
    """
    parser = argparse.ArgumentParser(
        prog='orcoursetrion',
        description=('Run an orchestrion action.\n')
    )
    subparsers = parser.add_subparsers(
        title="Actions",
        description='Valid actions',
    )

    # Setup subparsers for each action

    # Create studio repository
    create_export_repo = subparsers.add_parser(
        'create_export_repo',
        help='Create a Studio export git repository'
    )
    create_export_repo.add_argument(
        '-c', '--course', type=str, required=True,
        help='Course to work on (i.e. 6.0001)'
    )
    create_export_repo.add_argument(
        '-t', '--term', type=str, required=True,
        help='Term of the course (i.e. Spring_2015)'
    )
    create_export_repo.add_argument(
        '-d', '--description', type=str,
        help='Description string to set for repository'
    )
    create_export_repo.set_defaults(func=run_create_export_repo)

    # Create XML repository
    create_xml_repo = subparsers.add_parser(
        'create_xml_repo',
        help='Create an XML/latex2edx git repository'
    )
    create_xml_repo.add_argument(
        '-c', '--course', type=str, required=True,
        help='Course to work on (i.e. 6.0001)'
    )
    create_xml_repo.add_argument(
        '-t', '--term', type=str, required=True,
        help='Term of the course (i.e. Spring_2015)'
    )
    create_xml_repo.add_argument(
        '-g', '--team', type=str, required=True,
        help='Name of team in organization that should have access'
    )
    create_xml_repo.add_argument(
        '-d', '--description', type=str,
        help='Description string to set for repository'
    )
    create_xml_repo.set_defaults(func=run_create_xml_repo)

    # Run the action
    args = parser.parse_args()
    args.func(args)
