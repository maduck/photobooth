import logging
import subprocess
import time
import picamera
import pygame
from pygame_helpers import rounded_rect
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


class App(object):
    TEMP_DIR = '/dev/shm'
    TARGET_DIR = '/home/photobooth/photos'
    SWITCH_PIN = 4
    LED_PIN = 26
    stages = ('GREETING', 'PHOTO 1', 'PHOTO 2', 'PHOTO 3', 'PHOTO 4', 'FAREWELL')
    MAX_FPS = 60
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (1, 1, 1)
    RED = (255, 0, 0)
    ORANGE = (200, 50, 20)

    def __init__(self):
        self._running = True
        self._canvas = None
        self._background = None
        self._photo_space = None
        self.stage = 0
        self.size = self.width, self.height = 1024, 768
        self.font = None
        self._init_camera()
        self.photos = []
        self.clock = pygame.time.Clock()
        self._init_gpio()


    def _init_gpio(self):
        GPIO.setup(self.SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        self.enable_led(False)


    def enable_led(self, mode):
        GPIO.output(self.LED_PIN, int(not mode))


    def wait_for_button(self):
        while True:
            button_pressed = GPIO.input(self.SWITCH_PIN)
            if button_pressed:
                return
            pygame.display.flip()
            time.sleep(0.1)
    

    def _init_camera(self):
        self.camera = picamera.PiCamera()
        self.camera.annotate_text_size = 128
        self.camera.led = False
        self.camera.vflip = True
        self.camera.resolution = (1280, 853)
        #self.camera.hflip = True


    def on_init(self):
        pygame.init()
        display_mode = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN

        self._canvas = pygame.display.set_mode((0, 0), display_mode)
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.size = (self.width, self.height)
        self._background = self.fill_background()
        self._photo_space = self.fill_photo_space()
        self._running = True
        self.font = pygame.font.Font('concourse.ttf', 115)
        pygame.mouse.set_visible(False)
        #logging.debug('Cameras: %r' % pygame.camera.list_cameras())

        return self._running


    def fill_background(self):
        background = pygame.Surface((self.width, self.height))
        background_image = pygame.image.load("bg_linen.png").convert()
        for y in range(0, self.height, background_image.get_height()):
            for x in range(0, self.width, background_image.get_width()):
                background.blit(background_image, (x, y))
        return background


    def fill_photo_space(self, photo_files=None):
        if not photo_files:
            photo_files = (None, None, None, None)

        all_photos = pygame.Surface(self.size)

        for i, photo in enumerate(photo_files):
            if not photo:
                photo = "sample%d.jpg" % (i + 1)
            self.insert_single_photo(all_photos, photo, i)

        all_photos.set_colorkey(self.BLACK)
        return all_photos
    

    def insert_single_photo(self, surface, filename, number):
        width_gap = int(self.width / 100 * 5)
        height_gap = int(self.height / 100 * 5)

        frame_width = int((self.width - 3*width_gap)/2)
        frame_height = int((self.height - 3*height_gap)/2)

        frame_x = width_gap if number % 2 == 0 else (2*width_gap + frame_width)
        frame_y = height_gap if number < 2 else (2*height_gap + frame_height)

        photo = self.prepare_photo_for_display(filename)
        surface.blit(photo, (frame_x, frame_y))
        return surface


    def prepare_photo_for_display(self, photo_filename):
        width_gap = int(self.width / 100 * 5)
        height_gap = int(self.height / 100 * 5)
        frame_width = int((self.width - 3 * width_gap)/2)
        frame_height = int((self.height - 3 * height_gap)/2)
        frame_surface = pygame.Surface((frame_width, frame_height))
        frame_surface.fill(self.WHITE)

        photo_surface = pygame.image.load(photo_filename)
        self.photos.append(photo_surface)
        photo_width_gap = 0
        photo_height_gap = (frame_height / 100 * 8)
        photo_width = frame_width - 2*photo_width_gap
        photo_height = frame_height - 2*photo_height_gap

        scaled_surface = pygame.transform.scale(photo_surface, (photo_width, photo_height))
        frame_surface.blit(scaled_surface, (photo_width_gap, photo_height_gap))

        return frame_surface


    def take_photo(self, number):
        self.render_text("Bild %d von %d" % (number, 4), self.BLACK)
        pygame.display.flip()
        time.sleep(2)
        self.camera.start_preview()
        self.reset_background()
        countdown_seconds = 5
        for count in range(countdown_seconds, 0, -1):
           self.camera.annotate_text = str(count)
           time.sleep(1)
        self.camera.annotate_text = ""

        photo_filename = '%s/photo_%d.jpg' % (self.TEMP_DIR, number)
        self.camera.capture(photo_filename)
        self.camera.stop_preview()
        self.insert_single_photo(self._photo_space, photo_filename, number-1)


    def on_event(self, event):
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            self._running = False
        """if event.type in (pygame.QUIT, ):
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if self.stages[self.stage] == "FAREWELL":
                self._running = False
            else:
                self.stage += 1"""


    def on_loop(self):
        self.clock.tick(self.MAX_FPS)


    def render_text(self, text, bg_color):
        font_label = self.font.render(text, True, self.WHITE)
        font_width = font_label.get_width()
        font_height = font_label.get_height()
        background_width = font_width + 10 * font_width / 100
        background_height = font_height + 10 * font_height / 100
        x = (self.width - background_width) / 2
        y = (self.height - background_height) / 2
        rounded_rect(self._canvas, (x, y, background_width, background_height), bg_color, radius=0.2)
        x = (self.width - font_width) / 2
        y = (self.height - font_height) / 2
        self._canvas.blit(font_label, (x, y))


    def reset_background(self):
        self._canvas.blit(self._background, (0, 0))
        self._canvas.blit(self._photo_space, (0, 0))
        pygame.display.flip()


    def print_photos(self):
        PRINTER_DPI = 300
        PRINTER_SIZE = [6, 4]
        image_size = width, height = [size * PRINTER_DPI for size in PRINTER_SIZE]
        print_surface = pygame.Surface(image_size)
        print_surface.fill(self.WHITE)
        for number, photo in enumerate(self.photos):
            width_gap = int(width / 100 * 2)
            height_gap = int(height / 100 * 2)

            frame_width = int((width - width_gap)/2)
            frame_height = int((height - height_gap)/2)

            frame_x = 0 if number % 2 == 0 else (width_gap + frame_width)
            frame_y = 0 if number < 2 else (height_gap + frame_height)
            #print 50 * "=", "inserting photo number %d into coords (%d | %d)" % (number, frame_x, frame_y)

            scaled_photo = pygame.transform.scale(photo, (frame_width, frame_height))
            print_surface.blit(scaled_photo, (frame_x, frame_y))

        photo_filename = "%s/%d.jpg" % (self.TARGET_DIR, time.time())
        pygame.image.save(print_surface, photo_filename)
        subprocess.call(['/usr/bin/lp', photo_filename])

    def on_render(self):
        self.reset_background()

        def greeting():
            self.photos = []
            self.render_text("Bereit?", bg_color=self.ORANGE)
            pygame.display.flip()
            #TODO wait for button press...
            self.enable_led(True)
            self.wait_for_button()
            self.enable_led(False)

        def farewell():
            self.render_text("Vielen Dank! Drucke... ", bg_color=self.ORANGE)
            pygame.display.flip()
            self.print_photos()
            self.photos = []

            time.sleep(10)
            self.stage = -1

        if self.stage == 0:
            greeting()
        elif self.stage == 5:
            farewell()
        else:
            self.take_photo(number=self.stage)

        self.stage += 1


    def on_cleanup(self):
        GPIO.cleanup()
        pygame.quit()


    def on_execute(self):
        if not self.on_init():
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
