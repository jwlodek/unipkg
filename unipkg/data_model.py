"""Data Model

File containing all data representation classes for different package managers supported by 
unipkg
"""

import unipkg.command_handler as EXE


class Package:

    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description


class PackageManager:

    def __init__(self, name: str):
        self.name = name


    def search_for_packages(self, search_key: str) -> List[Package]:
        pass

    def install_package(self, package_names: List[str], credentials: List[str]) -> None:
        pass

    def remove_package(self, package_names: List[str], credentials: List[str]) -> None:
        pass



class Aptitude:

    def __init__(self, name: str):
        super().__init__(name)

    def search_for_packages(self, search_key: str) -> List[Package]:
        command_str = f'{self.name} cache-search {search_key}'
        return EXE.execute_command(command_str, False)
        

    def install_package(self,  package_names: List[str], credentials: List[str]) -> None:
        command_str = f'sudo {self.name} install '
        for package in package_names:
            command_str = command_str + package
        return EXE.execute_command(command_str, True, creds = credentials, expect='Password:')