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

        self.marked_packages = []
        self.opened_packages = {}

        self.passwd = None
        self.stdout_ret = None
        self.err_ret = 0

        self.package_manager_selecter = self.root.add_scroll_menu('Managers', 0, 0, row_span=2, column_span=1)
        self.package_manager_selecter.add_item_list(find_supported_package_managers())
        self.active_package_manager = self.package_manager_selecter.view_items[self.package_manager_selecter.selected_item][3:]
        self.package_manager_selecter.view_items[self.package_manager_selecter.selected_item] = f'-> {self.active_package_manager}'
        self.package_manager_selecter.add_key_command(py_cui.keys.KEY_ENTER, self.select_package_manager)


        self.package_selection = self.root.add_checkbox_menu(f'{self.active_package_manager} Packages', 0, 1, row_span=4, column_span=6)
        self.log = self.root.add_text_block('Log/Status', 4, 1, row_span=3, column_span=6)
        self.package_selection.add_key_command(py_cui.keys.KEY_S_LOWER, self.ask_search_key)
        self.package_selection.add_key_command(py_cui.keys.KEY_L_LOWER, self.list_packages)
        self.package_selection.add_key_command(py_cui.keys.KEY_ENTER, self.mark_package)
        self.package_selection.add_key_command(py_cui.keys.KEY_A_LOWER, self.apply)
        self.package_selection.add_key_command(py_cui.keys.KEY_SPACE, self.show_package_info)

        self.marked_package_list = self.root.add_scroll_menu('Marked', 2, 0, row_span=2)
        #self.marked_packages.add_key_command(py_cui.keys.KEY_ENTER, self.unmark_package)

        self.apply_button = self.root.add_button('Apply', 4, 0, command=self.apply)
        self.update_all = self.root.add_button('Update', 5, 0, command=self.update_all)

        self.exit_button = self.root.add_button('Exit', 6, 0, command=exit)

        self.root.add_key_command(py_cui.keys.KEY_A_LOWER, self.apply)
        self.root.add_key_command(py_cui.keys.KEY_S_LOWER, self.ask_search_key)
        self.root.add_key_command(py_cui.keys.KEY_L_LOWER, self.list_packages)


    def update_all(self):
        pass

    def show_package_info(self):
        package = None
        for pkg in self.opened_packages.values():
            if f'{pkg}' == self.package_selection.view_items[self.package_selection.selected_item][6:]:
                package = pkg
                break

        info = supported_package_managers[self.active_package_manager].get_package_info(package)
        self.log.set_text(info)

    def mark_package(self):
        
        mark_toggle_pkg = None
        for pkg in self.opened_packages.values():
            if f'{pkg}' == self.package_selection.view_items[self.package_selection.selected_item][6:]:
                mark_toggle_pkg = pkg
                break

        rmpkg = None
        for pkg in self.marked_packages:
            if pkg.name == mark_toggle_pkg.name:
                rmpkg = pkg
                break
        if rmpkg is not None:
            self.marked_packages.remove(rmpkg)

        if f'{mark_toggle_pkg}' not in self.package_selection.get() and mark_toggle_pkg.installed is False:
            self.opened_packages[mark_toggle_pkg.name].marked_op = 'Install'
            self.marked_packages.append(self.opened_packages[mark_toggle_pkg.name])
        elif f'{mark_toggle_pkg}' in self.package_selection.get() and mark_toggle_pkg.installed:
            self.opened_packages[mark_toggle_pkg.name].marked_op = 'Uninstall'
            self.marked_packages.append(self.opened_packages[mark_toggle_pkg.name])

        self.refresh_marked_list()


    def refresh_marked_list(self):

        self.marked_package_list.clear()
        for pkg in self.marked_packages:
            self.marked_package_list.add_item(f'{pkg.name} - {pkg.marked_op}')



    def select_package_manager(self) -> None:
        self.marked_packages.clear()
        self.opened_packages.clear()
        self.refresh_marked_list()
        self.active_package_manager = self.package_manager_selecter.view_items[self.package_manager_selecter.selected_item][3:]
        for i in range(0, len(self.package_manager_selecter.view_items)):
            if self.package_manager_selecter.view_items[i].startswith('-> '):
                self.package_manager_selecter.view_items[i] = f'   {self.package_manager_selecter.view_items[i][3:]}'
        self.package_manager_selecter.view_items[self.package_manager_selecter.selected_item] = f'-> {self.active_package_manager}'
        self.package_selection.title = f'{self.active_package_manager} Packages'


    def ask_search_key(self) -> None:
        self.root.show_text_box_popup('Enter a Search Key', self.search_to_install)


    def search_to_install(self, search_key : str) -> None:

        self.root.show_loading_icon_popup('Searching', f'Fetching {self.active_package_manager} package info')
        op_thread = threading.Thread(target=lambda : self.search_to_install_op(search_key))
        op_thread.start()



    def search_to_install_op(self, search_key: str) -> None:
        current_package_manager = supported_package_managers[self.active_package_manager]
        try:
            packages, err = current_package_manager.search_for_packages(search_key)
            self.root.stop_loading_popup()
            if packages is None:
                self.root.show_error_popup('Failed to Search', 'Unable to search for packages, check network settings.')
            elif len(packages) == 0:
                self.root.show_warning_popup('No Results', f'No packages were found for search key {search_key}')
            else:
                self.update_package_selection_list(packages)
        except Exception as e:
            self.root.stop_loading_popup()
            self.root.show_error_popup('Search Failed', f'Searching for {current_package_manager.name} packages failed due to: {str(e)}')


    def update_package_selection_list(self, packages):
        self.opened_packages.clear()
        self.package_selection.clear()
        for pkg in packages:
            self.opened_packages[pkg.name] = pkg
            self.package_selection.add_item(f'{pkg}')
            if pkg.installed:
                self.package_selection.mark_item_as_checked(f'{pkg}')
        self.root.move_focus(self.package_selection)


    def list_packages(self):
        self.root.show_loading_icon_popup('Searching', f'Locating {self.active_package_manager} installed packages')
        op_thread = threading.Thread(target=self.list_packages_op)
        op_thread.start()


    def list_packages_op(self):
        current_package_manager = supported_package_managers[self.active_package_manager]
        try:
            packages, err = current_package_manager.list_packages()
            self.root.stop_loading_popup()
            if packages is None:
                self.root.show_error_popup('Failed to Search', 'Unable to locate for packages!')
            elif len(packages) == 0:
                self.root.show_warning_popup('No Results', 'No packages were found on local system.')
            else:
                self.update_package_selection_list(packages)
        except Exception as e:
            self.root.stop_loading_popup()
            self.root.show_error_popup('Search Failed', f'Searching for local {current_package_manager.name} packages failed due to: {str(e)}')


    def apply(self):

        if len(self.marked_packages) == 0:
            self.root.show_warning_popup('No Packages Selected', 'No packages were selected for install/uninstall!')
            return

        self.root.show_loading_bar_popup('Applying...', len(self.marked_packages))
        op_thread = threading.Thread(target=self.apply_op)
        op_thread.start()


    def apply_op(self):
        try:
            current_manager = supported_package_managers[self.active_package_manager]

            for pkg in self.marked_packages:
                self.root.popup.title = f'{pkg.marked_op}ing {pkg.name}...'
                if pkg.marked_op == 'Install':
                    current_manager.install_package(pkg, self.passwd)
                elif pkg.marked_op == 'Update':
                    current_manager.update_package(pkg, self.passwd)
                else:
                    current_manager.remove_package(pkg, self.passwd)
                self.root.increment_loading_bar()

            count = len(self.marked_packages)
            self.opened_packages.clear()
            self.marked_packages.clear()
            self.refresh_marked_list()

            self.root.stop_loading_popup()
            self.root.show_message_popup('Finished Applying', f'Performed {count} package operations succesffully.')
        except Exception as e:
            self.root.stop_loading_popup()
            self.root.show_error_popup('Apply Failed', f'Applying specified packages failed due to: {str(e)}')



def find_supported_package_managers() -> List[unipkg.data_model.PackageManager]:
    ret = []
    for name in supported_package_managers.keys():
        if supported_package_managers[name].check_exists():
            ret.append(f'   {name}')
    return ret



def check_admin_status() -> bool:
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin



def parse_args():
    pass


def main():
    root = py_cui.PyCUI(7, 7)
    is_admin = check_admin_status()
    if is_admin:
        root.set_title(f'UniPkg {__version__} - Administrator')
    else:
        root.set_title(f'UniPkg {__version__}')
    root.toggle_unicode_borders()
    manager = UniPkgManager(root)
    root.start()
