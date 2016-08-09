class BaseSavingBackend(object):
    def __init__(self):
        raise NotImplementedError("Please implement a saving backend.")

    def save(self):
        raise NotImplementedError("Please implement a saving backend.")