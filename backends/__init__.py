import importlib


def get_class_name_for_backend(backend_type):
    class_name = "{}{}{}".format(
        backend_type[0].upper(),
        backend_type[1:],
        'Backend',
    )
    return class_name


def acquire_backend(backend_type, backend_name, config):
    import_class = "{}.{}.{}".format(
        "backends",
        backend_type,
        backend_name,
    )
    backend = importlib.import_module(import_class)
    class_name = get_class_name_for_backend(backend_type)
    return backend.getattr(class_name)(config)
