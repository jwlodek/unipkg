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

    def __init__(self, num_rows, num_cols, title):
        self.root = py_cui.PyCUI(num_rows, num_cols)
        self.root.set_title(title)
        self.marked_for_installation = []
        self.marked_for_removal = []
        self.supported_package_managers = find_supported_package_managers()
        self.current_status = 'Install'

        self.stdout_ret = None
        self.err_ret = 0

        self.log = self.root.add_text_block('Log', 0, 0, row_span=5, column_span=3)
        
        self.package_selection = self.root.add_checkbox_menu(f'Packages to {self.current_status}', 0, 3, row_span=5, column_span=3)

        self.package_manager_selecter = self.root.add_scroll_menu('Select Package Manager', 6, 0)

        operations = ['Install', 'Uninstall', 'Autoremove', 'Upgrade']
        self.select_operation = self.root.add_scroll_menu('Select Operation', 6, 1)
        self.select_operation.add_item_list(operations)


        self.apply_button = self.root.add_button('Apply', 6, 2, command=exit())

        self.exit_button = self.root.add_button('Exit', 6, 3, command=exit())



def find_supported_package_managers():
    ret = []
    for name in supported_package_managers.keys():
        pass
    return ret



def parse_args():
    pass


def main():
    manager = UniPkgManager(7, 7, f'UniPkg {__version__}')
    print('test')
    manager.root.start()
