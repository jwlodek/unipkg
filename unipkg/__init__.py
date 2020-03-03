"""unipkg

File containing main CUI implementation for unipkg.

Author: Jakub Wlodek  
Created: 2/18/2020
"""

__version__ = 'v0.0.1'

import py_cui

import unipkg
import unipkg.data_model as MODEL

import ctypes, os
import argparse
from subprocess import Popen, PIPE
from typing import List
import threading

supported_package_managers = {
    'apt'       : MODEL.Aptitude('apt'),
    'apt-get'   : MODEL.Aptitude('apt-get'),
    'pip'       : MODEL.Pip('pip'),
    'pip3'      : MODEL.Pip('pip3'),
    'npm'       : MODEL.Npm('npm')
}


class UniPkgManager:

    def __init__(self, root : py_cui.PyCUI):
        self.root = root
        self.marked_for_installation = []
        self.marked_for_removal = []
        self.current_status = 'Install'

        self.stdout_ret = None
        self.err_ret = 0

        self.package_manager_selecter = self.root.add_scroll_menu('Select Package Manager', 0, 0, row_span=2, column_span=2)
        self.package_manager_selecter.add_item_list(find_supported_package_managers())

        self.select_operation = self.root.add_scroll_menu('Select Operation', 2, 0, row_span=2, column_span=2)
        self.log = self.root.add_text_block('Log', 4, 0, row_span=3, column_span=2)

        self.package_selection = self.root.add_checkbox_menu(f'Packages to {self.current_status}', 0, 2, row_span=6, column_span=5)
        self.package_selection.add_key_command(py_cui.keys.KEY_S_LOWER, self.ask_search_key)

        operations = ['Install', 'Uninstall', 'Autoremove', 'Upgrade']
        self.select_operation.add_item_list(operations)


        self.apply_button = self.root.add_button('Apply', 6, 2, command=exit)

        self.exit_button = self.root.add_button('Exit', 6, 3, command=exit)

        self.root.add_key_command(py_cui.keys.KEY_S_LOWER, self.ask_search_key)
        #self.root.add_key_command(py_cui.keys.KEY_L_LOWER, self.list_installed)



    def check_admin_status(self) -> bool:
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        return is_admin

    def ask_search_key(self) -> None:
        self.root.show_text_box_popup('Enter a Search Key', self.search_to_install)

    def search_to_install(self, search_key):

        op_thread = threading.Thread(target=lambda : self.search_to_install_op(search_key))
        op_thread.start()
        self.root.show_loading_icon_popup('Searching', f'Fetching {self.package_manager_selecter.get()} package info')


    def search_to_install_op(self, search_key):
        current_package_manager = supported_package_managers[self.package_manager_selecter.get()]
        results, installed, err = current_package_manager.search_for_packages(search_key)
        self.root.stop_loading_popup()
        if results is None:
            self.root.show_error_popup('Failed to Search', 'Unable to search for packages, check network settings.')
        elif len(results) == 0:
            self.root.show_warning_popup('No Results', f'No packages were found for search key {search_key}')
        else:
            self.package_selection.clear()
            self.package_selection.add_item_list(results)
            for pkg in results:
                if pkg in installed:
                    self.package_selection.mark_item_as_checked(pkg)
            self.root.move_focus(self.package_selection)

def find_supported_package_managers() -> List[unipkg.data_model.PackageManager]:
    ret = []
    for name in supported_package_managers.keys():
        if supported_package_managers[name].check_exists():
            ret.append(name)
    return ret



def parse_args():
    pass


def main():
    root = py_cui.PyCUI(7, 7)
    root.set_title(f'UniPkg {__version__}')
    root.toggle_unicode_borders()
    manager = UniPkgManager(root)
    root.start()
