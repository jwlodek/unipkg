"""Data Model

File containing all data representation classes for different package managers supported by 
unipkg
"""

import unipkg.command_handler as EXE
import unipkg.packages as PKG
from typing import List


class PackageManager:

    def __init__(self, name: str):
        self.name           = name
        self.is_selected    = False

    def search_for_packages(self, search_key: str):
        pass


    def list_packages(self) -> (List[PKG.Package], int):
        pass

    def update_package(self, package, password, as_admin=False)-> None:
        pass

    def install_package(self, package, password, as_admin=False) -> None:
        command_str = f'{self.name} install {package.name}'
        return EXE.execute_command(command_str, as_admin, passwd=password, expect='Password:')

    def remove_package(self, package, password, as_admin=False) -> None:
        command_str = f'{self.name} uninstall -y {package.name}'
        return EXE.execute_command(command_str, as_admin, passwd=password, expect='Password:')

    def check_exists(self) -> bool:
        command = f'{self.name} --version'
        _, err = EXE.execute_command(command, False)
        if err == 0:
            return True
        return False

    def __str__(self):
        if self.is_selected:
            return f'-> {self.name}'
        else:
            return f'   {self.name}'


class Aptitude(PackageManager):

    def __init__(self, name: str):
        super().__init__(name)

    def search_for_packages(self, search_key: str):
        command_str = f'{self.name} cache-search {search_key}'
        out, err = EXE.execute_command(command_str, False)
        



class Pip(PackageManager):

    def __init__(self, name: str):
        super().__init__(name)


    def update_package(self, package, password, as_admin=False) -> (str, str):
        command_str = f'{self.name} install --upgrade {package.name}'
        return EXE.execute_command(command_str, False)


    def list_packages(self) -> (List[PKG.PipPackage], int):
        command_str = f'{self.name} list --format=freeze'
        out, err = EXE.execute_command(command_str, False)
        if err !=0:
            return None, err
        else:
            lines = out.splitlines()
            packages = []
            for line in lines:
                if len(line) > 0:
                    name_ver = line.strip().split('==')
                    packages.append(PKG.PipPackage(name_ver[0], name_ver[1], '', True))
            return packages, err


    def search_for_packages(self, search_key : str) -> (List[PKG.PipPackage], int):
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
                    packages.append(PKG.PipPackage(name, version, description, False))
            return packages, 0



class Npm(PackageManager):

    def __init__(self, name):
        super().__init__(name)