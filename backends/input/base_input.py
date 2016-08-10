

class BaseInputBackend(object):

    def __init__(self):
        raise NotImplementedError("Please implement an input backend.")

    def check_for_button(self):
        pass