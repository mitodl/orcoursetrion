Orcoursetrion (a.k.a. Automatic Course Provisioning X)
------------------------------------------------------

Automatic course provisioning for the edx-platform using github and
zendesk.


Quick Start
===========

To get started, clone the repository, and run ``pip install .`` or
just install directory from github.com with ``pip install
git+https://github.com/mitodl/orcoursetrion``.

Once installed, create or acquire an `OAUTH2 token from github
<https://help.github.com/articles/creating-an-access-token-for-command-line-use/>`_.

Add the environment variable ``ORC_GITHUB_OAUTH2_TOKEN=<your token>``
to your environment, and run ``orcoursetrion --help`` for available
commands and actions.

If you are adding an XML course, you will also need to define
``ORC_STAGING_GITRELOAD`` in your environment for where Web hooks
should be sent for push events.
