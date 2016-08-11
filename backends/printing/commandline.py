import subprocess
from base_printing import BasePrintingBackend


class PrintingBackend(BasePrintingBackend):
    def __init__(self, config):
        self.config = config

    def printout(self, filename):
        subprocess.call([self.config.get("command"), filename])
