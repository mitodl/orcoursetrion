Orcoursetrion API Docs
----------------------

For convenient reference in development, here are the Orcoursetrion
API docs.

Actions
=======

The actions that are available to use.

.. automodule:: orcoursetrion.actions
    :members:
    :undoc-members:
    :show-inheritance:
    :imported-members:

Library
=======

API libraries.

.. automodule:: orcoursetrion.lib
    :members:
    :undoc-members:
    :show-inheritance:
    :imported-members:

.. _configuration:

Configuration
=============

Configuration options

.. automodule:: orcoursetrion.config

.. autoattribute:: orcoursetrion.config.ORC_GH_OAUTH2_TOKEN
   :annotation: = GitHub OAUTH2 Token

.. autoattribute:: orcoursetrion.config.ORC_GH_API_URL
   :annotation: = GitHub API URL

.. autoattribute:: orcoursetrion.config.ORC_COURSE_PREFIX
   :annotation: = Prefix to use in repository name

.. autoattribute:: orcoursetrion.config.ORC_STUDIO_ORG
   :annotation: = Organization to use for Studio export repos

.. autoattribute:: orcoursetrion.config.ORC_STUDIO_DEPLOY_TEAM
   :annotation: = Deployment team for Studio Export repos

.. autoattribute:: orcoursetrion.config.ORC_XML_ORG
    :annotation: = Organization to use for XML/latex2edx courses

.. autoattribute:: orcoursetrion.config.ORC_XML_DEPLOY_TEAM
    :annotation: = Deployment team for XML/latex2edx courses

.. autoattribute:: orcoursetrion.config.ORC_STAGING_GITRELOAD
    :annotation: = `gitreload <https://github.com/mitodl/gitreload>`_
                 server URL (including username and password) for the
                 course development LMS.

