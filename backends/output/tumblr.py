from base_saving import BaseOutputBackend


class OutputBackend(BaseOutputBackend):
    def __init__(self, config):
        self.config = config

    def export(self):
        pass
