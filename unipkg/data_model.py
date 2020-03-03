"""Data Model

File containing all data representation classes for different package managers supported by 
unipkg
"""

import unipkg.command_handler as EXE
from typing import List


class Package:

    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description




class PackageManager:

    def __init__(self, name: str):
        self.name = name


    def search_for_packages(self, search_key: str):
        pass

    def install_package(self, package_names, password) -> None:
        command_str = f'{self.name} install '
        for package in package_names:
            command_str = command_str + package
        return EXE.execute_command(command_str, True, passwd=password, expect='Password:')

    def remove_package(self, package_names, credentials) -> None:
        pass

    def check_exists(self) -> bool:
        command = f'{self.name} --version'
        out, err = EXE.execute_command(command, False)
        if err == 0:
            return True
        



class Aptitude(PackageManager):

    def __init__(self, name: str):
        super().__init__(name)

    def search_for_packages(self, search_key: str):
        command_str = f'{self.name} cache-search {search_key}'
        out, err = EXE.execute_command(command_str, False)
        



class Pip(PackageManager):

    def __init__(self, name: str):
        super().__init__(name)


    def search_for_packages(self, search_key : str) -> List[str]:
        command_str = f'{self.name} search {search_key}'
        out, err = EXE.execute_command(command_str, False)
        if err != 0:
            return None, None, err
        else:
            lines = out.splitlines()
            ret = []
            installed = []
            for line in lines:
                if '-' in line:
                    ret.append(line.strip())
                else:
                    installed.append(ret[len(ret) - 1])
            return ret, installed, 0



class Npm(PackageManager):

    def __init__(self, name):
        super().__init__(name)