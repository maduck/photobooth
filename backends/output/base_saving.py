class BaseOutputBackend(object):
    def __init__(self):
        raise NotImplementedError("Please implement a output backend.")

    def export(self):
        raise NotImplementedError("Please implement a output backend.")