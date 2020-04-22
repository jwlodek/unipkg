"""Module containing python class representations for different package types
"""

class Package:

    def __init__(self, name : str, version : str, description : str, installed : bool):
        self.name = name
        self.version = version
        self.description = description
        self.installed = installed
        self.marked_op = None

    def __str__(self) -> str:
        return f'{self.name:<32} | {self.version:<8} | {self.description}'


class PipPackage(Package):

    def __init__(self, name : str, version : str, description : str, installed : bool):
        super().__init__(name, version, description, installed)