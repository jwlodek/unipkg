"""unipkg

File containing main CUI implementation for unipkg.

Author: Jakub Wlodek  
Created: 2/18/2020
"""

__version__ = 'v0.0.1'

import py_cui

import unipkg.data_model as MODEL

import os
import argparse
from subprocess import Popen, PIPE

supported_package_managers = {
    'apt'   : MODEL.Aptitude('apt'),
    'apt-get': MODEL.Aptitude('apt-get'),
    'pip'   : MODEL.Pip('pip'),
    'pip3'  : MODEL.Pip('pip3'),
    'npm'   : MODEL.Npm('npm')
}



class UniPkgManager:

    def __init__(self, root):
        self.root = root
        self.marked_for_installation = []
        self.marked_for_removal = []
        self.supported_package_managers = find_supported_package_managers()

        self.stdout_ret = None
        self.err_ret = 0

        self.search_bar = 0


def find_supported_package_managers():
    ret = []
    for name in supported_package_managers.keys():
        pass
    return ret



def parse_args():
    pass


def main():
    root = py_cui.PyCUI(6, 7)
    manager = UniPkgManager(root)
    root.start()