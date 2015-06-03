"""
Provide simplified entry points for common task
"""

from __future__ import absolute_import, print_function

from .converter import convert
from .reader import read


def python_to_notebook(input_filename, output_filename):
    """
    Convert the given python source file into a properly fomratted notebook.
    """
    cvt = read(input_filename)
    convert(cvt, output_filename)
