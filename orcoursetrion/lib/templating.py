# -*- coding: utf-8 -*-
"""
Template class for constructing OLX courses via cookiecutter.

Args:
    course_info (dict): Contains the parameters required for the
        `cookiecutter.json` file at https://github.com/mitodl/template-mit-demo.
    author_type (str): A string that will declare either `xml`, `latex`, or
        `studio`, it will check out the respective branch at
        https://github.com/mitodl/template-mit-demo.

"""
import tarfile
import os
from cookiecutter.main import cookiecutter
from git import Repo


class TemplateCourse:
    def __init__(self, course_info, author_type):
        self.course_info = course_info
        self.author_type = author_type

    def new_course(self):
        """
        Creates a course from the cookiecutter templates
        at https://github.com/mitodl/template-mit-demo.

        Args:
            None

        Raises:
            None

        Returns:
            A path where the newly generated course folder resides.

        """
        path = os.path.dirname(os.path.abspath(__file__))
        course_info = self.course_info
        cookiecutter("gh:itsbenweeks/template-mit-demo",  # FIX:Get on ODL repo.
                     checkout=self.author_type,
                     no_input=True,
                     extra_context=course_info
                     )
        return os.path.join(path, course_info['course_number'])

    def file_course(self, course_path):
        """
        Creates a tarball of a course at the given path.
        Returns a path to the tarball.

        Args:
            course_path(str): A path where a course folder resides.

        Raises:
            shutil.exceptions.badfile
        Returns:
            str: A path to the tarball.
        """
        file_name = self.course_info["course_number"] + ".tar.gz"
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 file_name)
        export_file = tarfile.open(file_path, "w:gz")
        export_file.add(course_path)
        export_file.close()
        return file_path

    def init_repo(self, course_path, git_url):
        """
        Begins a repository at the course path.

        Args:
            course_path (str): A path where a course folder resides.
            git_url (str): A url that the git repository's remote will be.

        Raises:
            git.exceptions.badsshkey
            git.exceptions.bedremote

        Returns:
            None
        """

        course_repo = Repo.init(course_path, bare=True)
        course_repo.create_remote("origin", git_url)
        course_repo.git.add("-A")
        course_repo.git.commit("-m", "Initializing Repo")
        course_repo.git.push("origin", "master")
        course_repo.git.checkout("-b", "live")
        course_repo.git.push("origin", "live")
