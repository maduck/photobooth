import picamera
from base_camera import BaseCameraBackend


class CameraBackend(BaseCameraBackend):

    def __init__(self, config):
        self.config = config
        self.camera = picamera.PiCamera()
        self.camera.annotate_text_size = 128
        self.camera.led = False
        self.camera.vflip = True
        self.camera.resolution = (
            self.config.getint("picture_width"),
            self.config.getint("picture_height")
        )

    def start_preview(self):
        self.camera.start_preview()

    def stop_preview(self):
        self.camera.stop_preview()

    def take_photo(self, filename):
        self.camera.capture(filename)

    def cleanup(self):
        pass

