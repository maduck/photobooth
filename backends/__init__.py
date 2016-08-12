import importlib


def get_class_name_for_backend(backend_type):
    class_name = "{}Backend".format(
        backend_type.capitalize(),
    )
    return class_name


def acquire_backend(backend_type, backend_name, config):
    import_class = "backends.{}.{}".format(
        backend_type,
        backend_name,
    )
    backend = importlib.import_module(import_class)
    class_name = get_class_name_for_backend(backend_type)
    return backend.getattr(class_name)(config)


def acquire_multiple_backends(backend_type, backend_names, config):
    names = backend_names.split(",")
    result = []
    for name in names:
        backend = acquire_backend(backend_type, name, config)
        result.append(backend)
    return result
