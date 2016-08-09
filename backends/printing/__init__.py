import importlib


def get_printing_backend(config):
    backend_name = config.get("printing backend")
    backend = importlib.import_module(backend_name)
    return backend.PrintingBackend(config)
