# -*- coding: utf8 -*-

import os
import sys
import time

import RPi.GPIO as GPIO
import picamera
import pygame

import backends
from libs.config import Config
from libs.gui import rounded_rect, Colors


class PhotoboothApp(object):
    config = Config()

    def __init__(self):
        self.runtime_id = 0
        self._canvas = None
        self._background = None
        self._photo_space = None
        self.target_dir = None
        self.font = None
        self._init_camera()
        self.photos = []
        self.printer = backends.acquire_backend("output", "line_printer", self.config)
        self._init_gpio()
        self._get_last_runtime_id()
        self.get_current_photo_directory()

        pygame.init()
        self.clock = pygame.time.Clock()
        self.limit_cpu_usage()
        display_mode = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN
        self._canvas = pygame.display.set_mode((0, 0), display_mode)
        self.screen_width = pygame.display.Info().current_w
        self.screen_height = pygame.display.Info().current_h
        self._background = self.fill_background()
        self._photo_space = self.fill_photo_space()
        self._running = True
        self.font = pygame.font.Font(self.config.get('font_filename'), self.config.getint('font_size'))
        pygame.mouse.set_visible(False)

    def _get_last_runtime_id(self):
        self.runtime_id = 0
        try:
            f = open(self.config.get("RUNTIME_ID_FILE"), "r")
            self.runtime_id = int(f.read())
            f.close()
        except (IOError, OSError, ValueError):
            pass

    def _acquire_new_runtime_id(self):
        self.runtime_id += 1
        f = open(self.config.get("RUNTIME_ID_FILE"), "w")
        f.write(str(self.runtime_id))
        f.close()

    def create_valid_photo_directory(self):
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)
            return True
        if os.path.isdir(self.target_dir):
            return not os.listdir(self.target_dir)
        return False

    def get_current_photo_directory(self):
        self.generate_runtime_dirname()
        while not self.create_valid_photo_directory():
            self._acquire_new_runtime_id()
            self.generate_runtime_dirname()

    def generate_runtime_dirname(self):
        base_dir = os.path.expanduser(self.config.get("TARGET_DIR"))
        runtime_dir = "photos-%04d" % self.runtime_id
        self.target_dir = os.path.join(base_dir, runtime_dir)

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config.getint("SWITCH_PIN"), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.config.getint("LED_PIN"), GPIO.OUT)
        self.enable_led(False)

    def _init_camera(self):
        self.camera = picamera.PiCamera()
        self.camera.annotate_text_size = 128
        self.camera.led = False
        self.camera.vflip = True
        self.camera.resolution = (self.config.getint("picture_width"), self.config.getint("picture_height"))

    def enable_led(self, mode):
        GPIO.output(self.config.getint("LED_PIN"), int(not mode))

    def wait_for_button(self):
        while True:
            button_pressed = GPIO.input(self.config.getint("SWITCH_PIN"))
            if button_pressed:
                return
            pygame.display.flip()
            time.sleep(0.1)
            self.parse_events()

    def fill_background(self):
        background = pygame.Surface((self.screen_width, self.screen_height))
        background_image = pygame.image.load(self.config.get("background_tile_image")).convert()
        for y in range(0, self.screen_height, background_image.get_height()):
            for x in range(0, self.screen_width, background_image.get_width()):
                background.blit(background_image, (x, y))
        return background

    def fill_photo_space(self):
        all_photos = pygame.Surface((self.screen_width, self.screen_height))

        for photo_number in range(1, 5):
            photo_filename = "images/sample%d.png" % photo_number
            self.put_photo_on_surface(all_photos, photo_filename, photo_number)

        all_photos.set_colorkey(Colors.BLACK)
        return all_photos

    def put_photo_on_surface(self, surface, filename, number):
        gap_percentage = 5
        width_gap = int(self.screen_width / 100 * gap_percentage)
        height_gap = int(self.screen_height / 100 * gap_percentage)

        frame_width = int((self.screen_width - 3 * width_gap) / 2)
        frame_height = int((self.screen_height - 3 * height_gap) / 2)

        frame_x = width_gap if number % 2 != 0 else (2 * width_gap + frame_width)
        frame_y = height_gap if number <= 2 else (2 * height_gap + frame_height)

        photo = self.load_and_scale_photo_for_display(filename)

        surface.blit(photo, (frame_x, frame_y))

    def load_and_scale_photo_for_display(self, photo_filename):
        gap_percentage = 5
        width_gap = int(self.screen_width / 100 * gap_percentage)
        height_gap = int(self.screen_height / 100 * gap_percentage)
        frame_width = int((self.screen_width - 3 * width_gap) / 2)
        frame_height = int((self.screen_height - 3 * height_gap) / 2)
        frame_surface = pygame.Surface((frame_width, frame_height))
        frame_surface.fill(Colors.WHITE)

        photo_surface = pygame.image.load(photo_filename)
        self.photos.append(photo_surface)
        photo_width_gap = 0
        photo_height_gap = (frame_height / 100 * 8)
        photo_width = frame_width - 2 * photo_width_gap
        photo_height = frame_height - 2 * photo_height_gap

        scaled_surface = pygame.transform.scale(photo_surface, (photo_width, photo_height))
        frame_surface.blit(scaled_surface, (photo_width_gap, photo_height_gap))

        return frame_surface

    def take_photo(self, number):
        self.redraw_background()
        self.render_text("Bild %d von %d" % (number, 4), Colors.BLACK)
        pygame.display.flip()
        time.sleep(2)
        self.camera.start_preview()
        self.redraw_background(white_borders=True)
        for count in range(self.config.getint("countdown_seconds"), 0, -1):
            self.camera.annotate_text = str(count)
            time.sleep(1)
        self.camera.annotate_text = ""

        photo_filename = '%s/photo_%d.jpg' % (self.config.get("TEMP_DIR"), number)
        self.camera.capture(photo_filename)
        self.camera.stop_preview()
        self.put_photo_on_surface(self._photo_space, photo_filename, number)

    def parse_events(self):
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                self._running = False
                self.cleanup()
                sys.exit(0)

    def limit_cpu_usage(self):
        self.clock.tick(self.config.getfloat("MAX_FPS"))

    def render_text(self, text, bg_color):
        overall_width = 0
        overall_height = 0
        text_lines = []
        for line in text.split('\n'):
            overall_width = max(overall_width, self.font.size(line)[0])
            overall_height += self.font.size(line)[1]
            text_lines.append(self.font.render(line, True, Colors.WHITE))

        top_and_bottom_margin_percentage = 10
        background_width = overall_width * (100 + top_and_bottom_margin_percentage) / 100
        background_height = overall_height * (100 + top_and_bottom_margin_percentage) / 100
        x = (self.screen_width - background_width) / 2
        y = (self.screen_height - background_height) / 2
        rounded_rect(self._canvas, (x, y, background_width, background_height), bg_color, radius=0.2)
        text_margin_percentage = top_and_bottom_margin_percentage / 2
        start_height = y + text_margin_percentage * overall_height / 100
        for i, line in enumerate(text_lines):
            label_x = (self.screen_width - line.get_width()) / 2
            label_y = start_height + i * line.get_height()
            self._canvas.blit(line, (label_x, label_y))

    def redraw_background(self, white_borders=False):
        self._canvas.blit(self._background, (0, 0))
        self._canvas.blit(self._photo_space, (0, 0))
        if white_borders:
            photo_height = self.config.getint("picture_height")
            rect_height = int((self.screen_height - photo_height) / 2)
            rect_size = (self.screen_width, rect_height)
            border_rect = pygame.Surface(rect_size)
            border_rect.fill(Colors.WHITE)
            self._canvas.blit(border_rect, (0, 0))
            self._canvas.blit(border_rect, (0, rect_height + photo_height))
        pygame.display.flip()

    def render_and_save_printer_photo(self, photo_filename):
        dpi = self.config.getfloat("printer_dpi")
        width = dpi * self.config.getfloat("printer_width_inch")
        height = dpi * self.config.getfloat("printer_height_inch")
        print_surface = pygame.Surface((width, height))
        print_surface.fill(Colors.WHITE)
        for number, photo in enumerate(self.photos):
            gap_percentage = 2
            width_gap = int(width / 100 * gap_percentage)
            height_gap = int(height / 100 * gap_percentage)

            frame_width = int((width - width_gap) / 2)
            frame_height = int((height - height_gap) / 2)

            frame_x = 0 if number % 2 == 0 else (width_gap + frame_width)
            frame_y = 0 if number < 2 else (height_gap + frame_height)

            scaled_photo = pygame.transform.scale(photo, (frame_width, frame_height))
            scaled_photo = pygame.transform.flip(scaled_photo, True, False)
            print_surface.blit(scaled_photo, (frame_x, frame_y))
        pygame.image.save(print_surface, photo_filename)

    def generate_photo_filename(self):
        picture = "%d.jpg" % time.time()
        filename = os.path.join(self.target_dir, picture)
        return os.path.normpath(filename)

    def stage_greeting(self):
        self.photos = []
        self.redraw_background()
        self.render_text(u"Bereit?\nKnopf drücken!", bg_color=Colors.ORANGE)
        pygame.display.flip()
        self.enable_led(True)
        self.wait_for_button()
        self.enable_led(False)

    def stage_farewell(self):
        time.sleep(2)
        self.render_text(u"Vielen Dank!\nDrucke... ", bg_color=Colors.ORANGE)
        pygame.display.flip()
        photo_filename = self.generate_photo_filename()
        self.render_and_save_printer_photo(photo_filename)
        self.printer.export(photo_filename)
        self.photos = []

        time.sleep(10)
        self._photo_space = self.fill_photo_space()

    def stage_photos(self):
        for number in range(1, 5):
            self.take_photo(number)
            self.redraw_background()

    def cleanup(self):
        GPIO.cleanup()
        pygame.quit()

    def launch_app(self):
        while self._running:
            self.stage_greeting()
            self.stage_photos()
            self.stage_farewell()
        self.cleanup()


if __name__ == "__main__":
    photo_app = PhotoboothApp()
    photo_app.launch_app()
