import importlib


class CameraFactory(object):
    def __init__(self, config):
        backend_name = config.get("camera backend")
        backend = importlib.import_module(backend_name)
        return backend.CameraBackend(config)