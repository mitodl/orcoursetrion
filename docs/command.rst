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
=================

:create_export_repo:

   This will create a new repository with the content deployment team
   from :py:attr:`~orcoursetrion.config.ORC_STUDIO_DEPLOY_TEAM` added to
   the repository.

:create_xml_repo:

   This will create a new repository with the
   :py:attr:`~orcoursetrion.config.ORC_XML_DEPLOY_TEAM` and a command
   line specified team added to repository.  It will also set up a git
   hook to the URL specified with
   :py:attr:`~orcoursetrion.config.ORC_STAGING_GITRELOAD`.
