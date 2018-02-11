import tempfile
import subprocess
from base_saving import BaseOutputBackend


class OutputBackend(BaseOutputBackend):
    def __init__(self, config):
        self.config = config

    def export(self):
        tmpfile = tempfile.NamedTemporaryFile()
        # save file in here
        subprocess.call([self.config.get("command"), tmpfile.name])
        tmpfile.close()
