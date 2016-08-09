import importlib


def get_saving_backend(config):
    backend_name = config.get("saving backend")
    backend = importlib.import_module(backend_name)
    return backend.SavingBackend(config)
