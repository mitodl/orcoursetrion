Orcoursetrion (a.k.a. Automatic Course Provisioning X)
------------------------------------------------------
.. image:: https://img.shields.io/travis/mitodl/orcoursetrion.svg
    :target: https://travis-ci.org/mitodl/orcoursetrion
.. image:: https://img.shields.io/coveralls/mitodl/orcoursetrion.svg
    :target: https://coveralls.io/r/mitodl/orcoursetrion
.. image:: https://img.shields.io/pypi/dm/orcoursetrion.svg
    :target: https://pypi.python.org/pypi/orcoursetrion
.. image:: https://img.shields.io/pypi/v/orcoursetrion.svg
    :target: https://pypi.python.org/pypi/orcoursetrion
.. image:: https://img.shields.io/github/issues/mitodl/orcoursetrion.svg
    :target: https://github.com/mitodl/orcoursetrion/issues
.. image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: https://github.com/mitodl/orcoursetrion/blob/master/LICENSE
.. image:: https://readthedocs.org/projects/orcoursetrion/badge/?version=latest
    :target: http://orcoursetrion.rtfd.org/en/latest
.. image:: https://readthedocs.org/projects/orcoursetrion/badge/?version=release
    :target: http://orcoursetrion.rtfd.org/en/release


Automatic course provisioning for the edx-platform using github and
zendesk.


Quick Start
===========

To install the latest release, run ``pip install orcoursetrion``.

If you want to be on the development edge (generally stable), clone
the repository, and run ``pip install .`` or just install directory
from github.com with ``pip install
git+https://github.com/mitodl/orcoursetrion``.

Once installed, create or acquire an `OAUTH2 token from github
<https://help.github.com/articles/creating-an-access-token-for-command-line-use/>`_.
That at least has the ``repo``, ``write:repo_hook``, ``admin:org``,
and ``write:org`` permissions.

Add the environment variable ``ORC_GH_OAUTH2_TOKEN=<your token>``
to your environment, and run ``orcoursetrion --help`` for available
commands and actions.

If you are adding an XML course, you will also need to define
``ORC_STAGING_GITRELOAD`` in your environment for where Web hooks
should be sent for push events.

Optional
========

There are a few other environment variables to add if you want to use the
release command, or if you would like orcoursetrion's commits to be from on
particular user.

``ORC_PRODUCTION_GITRELOAD`` for where Web hooks related to a production run of
your course should be sent for push events.

``ORC_GH_NAME`` for how you want commits from orcoursetrion to be identified.

``ORC_GH_EMAIL`` for what email address you want associated with commits from
orcoursetrion.
