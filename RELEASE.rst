Release Notes
=============

Version 0.2.0
-------------

- commit initial course.xml when running create_export_repo (#44)
- add PR template (#43)
- Switched from pyflakes to pylint Added tox support Resolved minor pylint issues
- Explaining some optional environment variables.
- Added the creation of a .gitgnore file for studio courses Closes #37
- Splitting tests, closes #24.
- More tests so httpretty won&#39;t break them
- defaul=None
- Style changes &amp; better tests
- line break before binary operator
- Making the -g flag optional for `create_xml_repo`
- Pylint cleanup
- Convert configuration from list of tuples to dictionary
- Shallow copy of repo
- Adds `release_studio` and `release_xml` actions and commands In this commit, these will only add production Web hooks to the course. Closes #12
- Add delete hooks and start of rerun_xml and rerun_studio commands Closes #13
- Correct doc string raises to the correct exception class
- Team names are case insensitive memberhip is not membership
- Documentation for ``put_team`` and team membership in ``create_xml_course``
- Add ``put_team`` command and add membership to ``create_xml_repo`` command
- Add ``put_team`` action and add team creation to ``create_xml_repo```
- Add library function to manage github teams
- Requests must be 2.4.2 or greater due to use of json parameter
- Because you can never have too many badges

