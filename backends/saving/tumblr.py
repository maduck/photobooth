from base_saving import BaseSavingBackend


class SavingBackend(BaseSavingBackend):
    def __init__(self, config):
        self.config = config

    def save(self):
        pass
