"""Data Model

File containing all data representation classes for different package managers supported by
unipkg
"""

import unipkg.command_handler as EXE
import unipkg.packages as PKG
from typing import List
from difflib import SequenceMatcher
import operator
import re


class PackageManager:

    def __init__(self, name: str):
        self.name = name
        self.installer_name = name
        self.is_selected = False

    def search_for_packages(self, search_key: str):
        pass

    def list_packages(self) -> (List[PKG.Package], int):
        pass

    def update_package(self, package, password, as_admin=False) -> None:
        pass

    def install_package(self, package, password, as_admin=False) -> None:
        command_str = f'{self.installer_name} install {package.name}'
        return EXE.execute_command(command_str, as_admin, passwd=password, expect='Password:')

    def remove_package(self, package, password, as_admin=False) -> None:
        command_str = f'{self.installer_name} uninstall -y {package.name}'
        return EXE.execute_command(command_str, as_admin, passwd=password, expect='Password:')

    def check_exists(self) -> bool:
        command = f'{self.installer_name} --version'
        _, err = EXE.execute_command(command, False)
        if err == 0:
            return True
        return False

    def __str__(self):
        if self.is_selected:
            return f'-> {self.name}'
        else:
            return f'   {self.name}'


    def get_best_match_packages(self, pkg_names: List[str], search_key : str) -> List[str]:

        sim_dict = {}
        for pkg_name in pkg_names:
            sim_dict[pkg_name] = SequenceMatcher(None, pkg_name, search_key).quick_ratio()
        sim_dict_sorted = sorted(sim_dict.items(), key=operator.itemgetter(1))
        sim_dict_sorted.reverse()
        return [x[0] for x in sim_dict_sorted]


class Aptitude(PackageManager):

    def __init__(self):
        super().__init__('apt')

        self.installer_name = 'apt-get'
        self.cache_name = 'apt-cache'


    def list_packages(self):
        command_str = f'dpkg -l --no-pager'
        out, err = EXE.execute_command(command_str, False)
        lines = out.splitlines()
        output = []
        pkg_list = False
        for line in lines:
            if line.startswith('+++'):
                pkg_list = True
            elif pkg_list:
                temp = re.sub('\s+', ' ', line)
                temp.split(' ', 4)
                output.append(PKG.AptitudePackage(temp[1], temp[2], temp[4], True))
        return output


    def search_for_packages(self, search_key: str):
        command_str = f'{self.cache_name} search {search_key}'
        out, err = EXE.execute_command(command_str, False)

        installed_packages = self.list_packages()
        installed_package_names = []
        for pkg in installed_packages:
            installed_package_names.append(pkg.name)

        if err != 0:
            return None, out, err
        else:
            lines = out.splitlines()
            pkg_names = []
            pkg_descs = {}
            for line in lines:
                if len(line.strip()) == 0:
                    pass
                else:
                    pkg = line.strip().split(' - ', 1)
                    pkg_name = pkg[0]
                    pkg_desc = pkg[1]
                    pkg_names.append(pkg_name)
                    pkg_descs[pkg_name] = pkg_desc
            actual_pkgs = self.get_best_match_packages(pkg_names, search_key)
            packages = []
            for pkg_name in actual_pkgs:

                pkg_desc = pkg_descs[pkg_name]
                #_, ret_installed = EXE.execute_command(
                #    f'dpkg -l {pkg[0]}', False)
                is_installed = False
                if pkg_name in installed_package_names:
                    is_installed = True

                fp = open('temp.txt', 'w')

                if is_installed:
                    packages.insert(0, PKG.AptitudePackage(pkg_name, '', pkg_desc, is_installed))
                    fp.write(f'{pkg_name} is installed')
                else:
                    packages.append(PKG.AptitudePackage(
                        pkg_name, '', pkg_desc, is_installed))

                fp.close()

            return packages, '', 0


class Pip(PackageManager):

    def __init__(self, name: str):
        super().__init__(name)

    def update_package(self, package, password, as_admin=False) -> (str, str):
        command_str = f'{self.name} install --upgrade {package.name}'
        return EXE.execute_command(command_str, False)

    def list_packages(self) -> (List[PKG.PipPackage], int):
        command_str = f'{self.name} list --format=freeze'
        out, err = EXE.execute_command(command_str, False)
        if err != 0:
            return None, out, err
        else:
            lines = out.splitlines()
            packages = []
            for line in lines:
                if len(line) > 0:
                    name_ver = line.strip().split('==')
                    packages.append(PKG.PipPackage(
                        name_ver[0], name_ver[1], '', True))
            return packages, err
    
    def search_for_packages(self, search_key: str) -> (List[PKG.PipPackage], int):
        command_str = f'{self.name} search {search_key}'
        out, err = EXE.execute_command(command_str, False)

        if err != 0:
            return None, err
        else:
            lines = out.splitlines()
            packages = []
            for line in lines:
                if len(line.strip()) == 0:
                    pass
                elif 'INSTALLED' in line:
                    packages[len(packages) - 1].installed = True
                elif ' - ' in line:
                    name = line.split(' ')[0].strip()
                    version = line.split(' ')[1].strip()[1:-1]
                    description = line.split(' - ', 1)[-1].strip()
                    packages.append(PKG.PipPackage(
                        name, version, description, False))
            return packages, '', 0


class Npm(PackageManager):

    def __init__(self, name):
        super().__init__(name)
