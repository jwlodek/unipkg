"""Data Model

File containing all data representation classes for different package managers supported by 
unipkg
"""

import unipkg.command_handler as EXE
from typing import List


class Package:

    def __init__(self, name : str, version : str, description : str, installed : bool):
        self.name = name
        self.version = version
        self.description = description
        self.installed = installed
        self.marked_op = None

    def __format__(self, fmt : str) -> str:
        return f'{self.name:<16} - {self.version:<8} - {self.description}'



class PackageManager:

    def __init__(self, name: str):
        self.name = name


    def search_for_packages(self, search_key: str):
        pass


    def list_packages(self) -> (List[Package], int):
        pass


    def install_package(self, package, password, as_admin=False) -> None:
        command_str = f'{self.name} install {package.name}'
        return EXE.execute_command(command_str, as_admin, passwd=password, expect='Password:')



    def remove_package(self, package, password, as_admin=False) -> None:
        command_str = f'{self.name} uninstall {package.name}'
        return EXE.execute_command(command_str, as_admin, passwd=password, expect='Password:')

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


    def list_packages(self) -> (List[Package], int):
        command_str = f'{self.name} list'
        out, err = EXE.execute_command(command_str, False)
        if err !=0:
            return None, err
        else:
            lines = out.splitlines()
            packages = []
            for line in lines:
                if len(line) > 0:
                    try:
                        name_ver = line.strip().split('==')
                        packages.append(Package(name_ver[0], name_ver[1], '', True))
                    except:
                        pass
            return packages, err


    def search_for_packages(self, search_key : str) -> List[str]:
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
                elif '-' in line:
                    name = line.split(' ')[0].strip()
                    version = line.split(' ')[1].strip()[1:-1]
                    description = line.split(')', 1)[-1].strip()[2:]
                    packages.append(Package(name, version, description, False))
            return packages, 0



class Npm(PackageManager):

    def __init__(self, name):
        super().__init__(name)