# -*- coding: utf-8 -*-
"""
This module implements the class that deals with the full document.

..  :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

import os
import subprocess
import errno
from .base_classes import Container, Command
from .package import Package
from .utils import dumps_list, rm_temp_dir


class Document(Container):

    r"""
    A class that contains a full LaTeX document.

    If needed, you can append stuff to the preamble or the packages.

    :param default_filepath: the default path to save files
    :param documentclass: the LaTeX class of the document
    :param fontenc: the option for the fontenc package
    :param inputenc: the option for the inputenc package
    :param author: the author of the document
    :param title: the title of the document
    :param date: the date of the document
    :param data:
    :param maketitle: whether `\\maketitle` command is activated or not.

    :type default_filepath: str
    :type documentclass: str or :class:`~pylatex.base_classes.command.Command`
        instance
    :type fontenc: str
    :type inputenc: str
    :type author: str
    :type title: str
    :type date: str
    :type data: list
    :type maketitle: bool
    """

    def __init__(self, default_filepath='default_filepath',
                 documentclass='article', fontenc='T1', inputenc='utf8',
                 author='', title='', date='', data=None, maketitle=False):

        self.default_filepath = default_filepath
        self.maketitle = maketitle

        if isinstance(documentclass, Command):
            self.documentclass = documentclass
        else:
            self.documentclass = Command('documentclass',
                                         arguments=documentclass)

        fontenc = Package('fontenc', options=fontenc)
        inputenc = Package('inputenc', options=inputenc)
        lmodern = Package('lmodern')
        packages = [fontenc, inputenc, lmodern]

        self.preamble = []

        self.preamble.append(Command('title', title))
        self.preamble.append(Command('author', author))
        self.preamble.append(Command('date', date))

        super().__init__(data, packages=packages)

    def dumps(self):
        """Represent the document as a string in LaTeX syntax.

        :return:
        :rtype: str
        """

        document = r'\begin{document}' + os.linesep

        if self.maketitle:
            document += r'\maketitle' + os.linesep

        document += super().dumps() + os.linesep

        document += r'\end{document}' + os.linesep

        head = self.documentclass.dumps() + os.linesep
        head += self.dumps_packages() + os.linesep
        head += dumps_list(self.preamble) + os.linesep

        return head + os.linesep + document

    def generate_tex(self, filepath=''):
        super().generate_tex(self.select_filepath(filepath))

    def generate_pdf(self, filepath='', clean=True, compiler='pdflatex',
                     silent=True):
        """Generate a pdf file from the document.

        :param filepath: the name of the file
        :param clean: whether non-pdf files created by `pdflatex` must be
            removed or not
        :param silent: whether to hide compiler output

        :type filepath: str
        :type clean: bool
        :type silent: bool
        """

        filepath = self.select_filepath(filepath)
        filepath = os.path.join('.', filepath)

        cur_dir = os.getcwd()
        dest_dir = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        os.chdir(dest_dir)

        self.generate_tex(basename)

        command = [compiler, '--interaction', 'nonstopmode',
                   '--jobname', basename, basename + '.tex']

        try:
            output = subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            print(e.output.decode())
            raise e
        else:
            if not silent:
                print(output.decode())

        if clean:
            for ext in ['aux', 'log', 'out', 'tex']:
                try:
                    os.remove(basename + '.' + ext)
                except (OSError, IOError) as e:
                    # Use FileNotFoundError when python 2 is dropped
                    if e.errno != errno.ENOENT:
                        raise

            rm_temp_dir()
        os.chdir(cur_dir)

    def select_filepath(self, filepath):
        """Make a choice between `filepath` and `self.default_filepath`.

        :param filepath: the filepath to be compared with
            `self.default_filepath`

        :type filepath: str

        :return: The selected filepath
        :rtype: str
        """

        if filepath == '':
            return self.default_filepath
        else:
            if os.path.basename(filepath) == '':
                filepath = os.path.join(filepath, os.path.basename(
                    self.default_filepath))
            return filepath
