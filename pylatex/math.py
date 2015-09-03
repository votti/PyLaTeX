# -*- coding: utf-8 -*-
"""
This module implements the classes that deal with math.

..  :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from .base_classes import LatexObject, Command, Container
from pylatex.package import Package


class Math(Container):

    """A class representing a math environment.

    :param data:
    :param inline:

    :type data: list
    :type inline: bool
    """

    def __init__(self, data=None, inline=False):
        self.inline = inline
        super().__init__(data)

    def dumps(self):
        """Return a LaTeX formatted string representing the object.

        :rtype: str
        """

        if self.inline:
            string = '$' + super().dumps(token=' ') + '$'
        else:
            string = '$$' + super().dumps(token=' ') + '$$\n'

        super().dumps()

        return string


class VectorName(Command):

    """A class representing a named vector.

    :param name:

    :type name: str
    """

    def __init__(self, name):
        super().__init__('mathbf', arguments=name)


class Matrix(LatexObject):

    """A class representing a matrix.

    :param matrix:
    :param name:
    :param mtype:
    :param alignment:

    :type matrix: :class:`numpy.ndarray` instance
    :type name: str
    :type mtype: str
    :type alignment: str
    """

    def __init__(self, matrix, name='', mtype='p', alignment=None):
        import numpy as np
        self._np = np

        self.mtype = mtype
        self.matrix = matrix
        self.alignment = alignment
        self.name = name

        super().__init__(packages=[Package('amsmath')])

    def dumps(self):
        """Return a string representin the matrix in LaTeX syntax.

        :rtype: str
        """

        string = r'\begin{'
        mtype = self.mtype + 'matrix'

        if self.alignment is not None:
            mtype += '*'
            alignment = '{' + self.alignment + '}'
        else:
            alignment = ''

        string += mtype + '}' + alignment
        string += '\n'

        shape = self.matrix.shape

        for (y, x), value in self._np.ndenumerate(self.matrix):
            if x:
                string += '&'
            string += str(value)

            if x == shape[1] - 1 and y != shape[0] - 1:
                string += r'\\' + '\n'

        string += '\n'

        string += r'\end{' + mtype + '}'

        super().dumps()

        return string
