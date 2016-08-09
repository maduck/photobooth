
class BaseCameraBackend(object):
    
    def __init__(self):
        raise NotImplementedError("Please implement a camera backend.")

    def start_preview(self):
        pass

    def stop_preview(self):
        pass

    def take_photo(self, filename):
        pass

    def cleanup(self):
        pass

