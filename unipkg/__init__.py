"""unipkg

File containing main CUI implementation for unipkg.

Author: Jakub Wlodek  
Created: 2/18/2020
"""

__version__ = 'v0.0.1'

import py_cui

import unipkg
import unipkg.package_managers as PKG_MANAGERS
import unipkg.packages as PKG
import unipkg.operations as OPS

import ctypes, os
import logging
import argparse
from subprocess import Popen, PIPE
from typing import List
import threading

supported_package_managers = {
    'apt'       : PKG_MANAGERS.Aptitude('apt'),
    'apt-get'   : PKG_MANAGERS.Aptitude('apt-get'),
    'pip'       : PKG_MANAGERS.Pip('pip'),
    'pip3'      : PKG_MANAGERS.Pip('pip3'),
    'npm'       : PKG_MANAGERS.Npm('npm')
}


class UniPkgManager:

    def __init__(self, root : py_cui.PyCUI):
        self.root = root

        self.passwd         = None
        self.stdout_ret     = None
        self.err_ret        = 0

        self.package_manager_selecter = self.root.add_scroll_menu('Managers', 0, 0, row_span=2, column_span=1)
        self.package_manager_selecter.add_item_list(find_supported_package_managers())

        self.active_package_manager = self.package_manager_selecter.get()
        self.active_package_manager.is_selected = True

        self.package_manager_selecter.add_key_command(py_cui.keys.KEY_ENTER, self.select_package_manager)



        self.package_selection = self.root.add_checkbox_menu(f'{self.active_package_manager.name} Packages', 0, 1, row_span=4, column_span=6)
        self.package_selection.add_key_command(py_cui.keys.KEY_S_LOWER,     self.ask_search_key)
        self.package_selection.add_key_command(py_cui.keys.KEY_L_LOWER,     self.list_packages)
        self.package_selection.add_key_command(py_cui.keys.KEY_ENTER,       self.mark_package)
        self.package_selection.add_key_command(py_cui.keys.KEY_A_LOWER,     self.apply)
        self.package_selection.add_key_command(py_cui.keys.KEY_SPACE,       self.show_package_info)


        self.log = self.root.add_text_block('Log/Status', 4, 1, row_span=3, column_span=6)
        self.log.add_text_color_rule('Done', py_cui.GREEN_ON_BLACK, 'startswith')
        self.log.add_text_color_rule('Error', py_cui.RED_ON_BLACK, 'startswith')


        self.marked_package_list = self.root.add_scroll_menu('Marked', 2, 0, row_span=2)
        #self.marked_packages.add_key_command(py_cui.keys.KEY_ENTER, self.unmark_package)

        self.apply_button       = self.root.add_button('Apply',     4, 0, command=self.apply)
        self.update_all_button  = self.root.add_button('Update',    5, 0, command=self.update_all)
        self.exit_button        = self.root.add_button('Exit',      6, 0, command=exit)

        self.root.add_key_command(py_cui.keys.KEY_A_LOWER, self.apply)
        self.root.add_key_command(py_cui.keys.KEY_S_LOWER, self.ask_search_key)
        self.root.add_key_command(py_cui.keys.KEY_L_LOWER, self.list_packages)


    def update_all(self):
        pass

    def show_package_info(self):

        pkg = self.package_selection.get()
        info = f'{pkg.name} - {pkg.version}\nDescription: {pkg.description}'
        self.log.set_text('{}\n\n{}'.format(info, self.log.get()))


    def mark_package(self):
        
        pkg = self.package_selection.get()
        if pkg.marked_op is not None:
            self.marked_package_list.remove_item(pkg.marked_op)
            pkg.marked_op = None
        elif pkg.installed:
            pkg.marked_op = OPS.PackageOp(pkg, 'Uninstall')
            self.marked_package_list.add_item(pkg.marked_op)
        else:
            pkg.marked_op = OPS.PackageOp(pkg, 'Install')
            self.marked_package_list.add_item(pkg.marked_op)


    def select_package_manager(self) -> None:
        self.marked_package_list.clear()
        self.package_selection.clear()
        self.log.clear()
        self.active_package_manager.is_selected = False
        self.active_package_manager = self.package_manager_selecter.get()
        self.package_selection.set_title(f'{self.active_package_manager.name} Packages')


    def ask_search_key(self) -> None:
        self.root.show_text_box_popup('Enter a Search Key', self.search_to_install)


    def search_to_install(self, search_key : str) -> None:

        self.root.show_loading_icon_popup('Searching', f'Fetching {self.active_package_manager.name} package info')
        op_thread = threading.Thread(target=lambda : self.search_to_install_op(search_key))
        op_thread.start()



    def search_to_install_op(self, search_key: str) -> None:
        try:
            self.root._logger.error(self.active_package_manager)
            packages, err = self.active_package_manager.search_for_packages(search_key)
            self.root.stop_loading_popup()
            if packages is None or err != 0:
                self.root.show_error_popup('Failed to Search', 'Unable to search for packages, check network settings.')
            elif len(packages) == 0:
                self.root.show_warning_popup('No Results', f'No packages were found for search key {search_key}')
            else:
                self.update_package_selection_list(packages)
        except Exception as e:
            self.root.stop_loading_popup()
            self.root.show_error_popup('Search Failed', f'Searching for {self.active_package_manager.name} packages failed due to: {str(e)}')


    def update_package_selection_list(self, packages):
        self.package_selection.clear()

        clean_packages = []
        for pkg in packages:
            found = False
            for op in self.marked_package_list.get_item_list():
                if pkg.name == op.pkg.name:
                    clean_packages.append(op.pkg)
                    found = True
            if not found:
                clean_packages.append(pkg)

        self.package_selection.add_item_list(clean_packages)
        
        for pkg in clean_packages:
            if pkg.marked_op is not None:
                if (pkg.installed and not pkg.marked_op.op == 'Uninstall') or pkg.marked_op.op == 'Install':
                    self.package_selection.mark_item_as_checked(pkg)
            elif pkg.installed:
                self.package_selection.mark_item_as_checked(pkg)
        self.root.move_focus(self.package_selection)


    def list_packages(self):
        self.root.show_loading_icon_popup('Searching', f'Locating {self.active_package_manager.name} installed packages')
        op_thread = threading.Thread(target=self.list_packages_op)
        op_thread.start()


    def list_packages_op(self):
        try:
            packages, _ = self.active_package_manager.list_packages()
            self.root.stop_loading_popup()
            if packages is None:
                self.root.show_error_popup('Failed to Search', 'Unable to locate for packages!')
            elif len(packages) == 0:
                self.root.show_warning_popup('No Results', 'No packages were found on local system.')
            else:
                self.update_package_selection_list(packages)
        except Exception as e:
            self.root.stop_loading_popup()
            self.root.show_error_popup('Search Failed', f'Searching for local {self.active_package_manager.name} packages failed due to: {str(e)}')


    def apply(self):

        if len(self.marked_package_list.get_item_list()) == 0:
            self.root.show_warning_popup('No Packages Selected', 'No packages were selected for install/uninstall!')
            return

        self.root.show_loading_bar_popup('Applying...', len(self.marked_package_list.get_item_list()))
        op_thread = threading.Thread(target=self.apply_op)
        op_thread.start()


    def apply_op(self):
        try:

            for pkg_op in self.marked_package_list.get_item_list():
                self.root._popup.set_title(f'{pkg_op.op}ing {pkg_op.pkg.name}...')
                if pkg_op.op == 'Install':
                    self.active_package_manager.install_package(pkg_op.pkg, self.passwd)
                    pkg_op.pkg.installed = True
                elif pkg_op.op == 'Update':
                    self.root._popup.set_title(f'Updating {pkg_op.pkg.name}...')
                    self.active_package_manager.update_package(pkg_op.pkg, self.passwd)
                else:
                    self.active_package_manager.remove_package(pkg_op.pkg, self.passwd)
                    pkg_op.pkg.installed = False
                self.update_log(f'Performed {pkg_op.op} operation on package {pkg_op.pkg.name} successfully.')
                self.root.increment_loading_bar()
                pkg_op.pkg.marked_op = None

            count = len(self.marked_package_list.get_item_list())
            self.marked_package_list.clear()
            self.root.stop_loading_popup()
            self.root.show_message_popup('Finished Applying', f'Performed {count} package operations succesffully.')
            self.update_log(f'Done. {count} operation(s) finished without errors.')
        except Exception as e:
            self.root.stop_loading_popup()
            self.root.show_error_popup('Apply Failed', f'Applying specified packages failed due to: {str(e)}')


    def update_log(self, text):
        self.log.set_text(f'{text}\n{self.log.get()}')


def find_supported_package_managers() -> List[unipkg.package_managers.PackageManager]:
    ret = []
    for name in supported_package_managers.keys():
        if supported_package_managers[name].check_exists():
            ret.append(supported_package_managers[name])
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
    _ = UniPkgManager(root)
    root.enable_logging()
    root.start()
