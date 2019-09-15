# -*- coding: utf-8 -*-
"""
Installs ALS.

We added a custom command to override develop and install
in order to have Qt resources (UI and images) compiled and
put in place
"""
import os
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)


def compile_qt_resources():
    """Executes Qt resources compilation script"""

    if os.system(f'{os.path.dirname(os.path.abspath(__file__))}/utils/compile_ui_and_rc.sh') != 0:
        raise RuntimeError("Qt resource compilation failed")


if __name__ == "__main__":

    if any([command in ['develop', 'install'] for command in sys.argv[1::]]):
        compile_qt_resources()

    setup(use_pyscaffold=True)
