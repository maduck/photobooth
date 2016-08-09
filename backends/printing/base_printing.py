class BasePrintingBackend(object):
    def __init__(self):
        raise NotImplementedError("Please implement a printing backend.")

    def printout(self, filename):
        raise NotImplementedError("Please implement a printing backend.")