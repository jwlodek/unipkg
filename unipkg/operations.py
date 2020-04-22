

class PackageOp:

    def __init__(self, pkg, op):
        self.pkg = pkg
        self.op = op


    def __str__(self):
        return f'{self.pkg.name} - {self.op}'