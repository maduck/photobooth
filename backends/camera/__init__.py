import importlib


def get_camera_backend(config):
    backend_name = config.get("camera backend")
    backend = importlib.import_module(backend_name)
    return backend.CameraBackend(config)
