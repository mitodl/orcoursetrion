Command Line
============

There is an exposed command line interface that is available upon
installation of the repository.  It can be run with ``orcoursetrion``, and
``orcoursetrion --help`` will provide the most up to date help information.

The command allows you to run commands that correspond to actions,
currently the only supported action is ``create_export_repo``, and if
your configuration is setup correctly (see :ref:`configuration`), and
at least minimally have set
:py:attr:`~orcoursetrion.config.ORC_GH_OAUTH2_TOKEN` and you run
``orcoursetrion create_export_repo -t Spring_2030 -c DevOps.001 -d 'My
awesome class repo'`` you should see it respond with the URL of the
repo that it just created for you.


Available Actions
~~~~~~~~~~~~~~~~~

:create_export_repo:

   This will create a new repository with the content deployment team
   from :py:attr:`~orcoursetrion.config.ORC_STUDIO_DEPLOY_TEAM` added to
   the repository.

:rerun_studio:

   This will remove all Web hooks from the course specified by
   ``term`` and then create a new repo with the ``new_term``, along
   with the :py:attr:`~orcoursetrion.config.ORC_STUDIO_DEPLOY_TEAM` added.

:create_xml_repo:

   This will create a new repository with the
   :py:attr:`~orcoursetrion.config.ORC_XML_DEPLOY_TEAM` and a command
   line specified team added to repository.  It will also set up a git
   hook to the URL specified with
   :py:attr:`~orcoursetrion.config.ORC_STAGING_GITRELOAD`. The
   membership of the team can also be specified, and will replace the
   existing membership of the team if it already exists.

:rerun_xml:

   This will rerun an XML course.  Currently this will just remove any
   Web hooks that are currently attached to the repository.

:put_team:

   This will create or update a team specified in the specified
   organization.  If the team doesn't exist, there is an option to
   give the team either push or pull access, otherwise the
   ``read_only`` flag is ignored.  It optionally takes a list of
   members of the team that should replace the existing team.
