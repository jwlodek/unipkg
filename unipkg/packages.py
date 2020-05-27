"""Module containing python class representations for different package types
"""

import unipkg.command_handler as EXE

class Package:

    def __init__(self, name : str, version : str, description : str, installed : bool):
        self.name = name
        self.version = version
        self.description = description
        self.installed = installed
        self.marked_op = None

    def get_info(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f'{self.name:<32} | {self.version:<8} | {self.description}'


class PipPackage(Package):

    def __init__(self, name : str, version : str, description : str, installed : bool):
        super().__init__(name, version, description, installed)


class AptitudePackage(Package):
    def __init__(self, name : str, version : str, description : str, installed : bool):
        super().__init__(name, version, description, installed)


    def get_info(self) -> str:
        pkg_info, _ = EXE.execute_command(
            f'apt-cache show {self.name}', False)
        pkg_info_lines = pkg_info.splitlines()
        for pkg_info_line in pkg_info_lines:
            if pkg_info_line.startswith('Version:'):
                self.version = pkg_info_line.split(
                    'Version:', 1)[1].strip()
                break
        
        return f'{self.name:<32} | {self.version:<8} | {self.description}'


    def __str__(self) -> str:
        return f'{self.name:<28} | {self.description}'