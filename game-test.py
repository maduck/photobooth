import logging
import time
import picamera
import pygame
from pygame_helpers import rounded_rect


class App(object):
    temp_dir = '/dev/shm/'
    stages = ('GREETING', 'PHOTO 1', 'PHOTO 2', 'PHOTO 3', 'PHOTO 4', 'FAREWELL')
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (1, 1, 1)
    RED = (255, 0, 0)

    def __init__(self):
        self._running = True
        self._canvas = None
        self._background = None
        self._photo_space = None
        self.stage = 0
        self.size = self.width, self.height = 1024, 768
        self.font = None
        self.camera = picamera.PiCamera()
        self.photos = []
        self.clock = pygame.time.Clock()

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
        width_gap = int(self.width / 100 * 5)
        height_gap = int(self.height / 100 * 5)

        all_photos = pygame.Surface(self.size)

        frame_width = int((self.width - 3*width_gap)/2)
        frame_height = int((self.height - 3*height_gap)/2)
        for i, photo in enumerate(photo_files):
            if not photo:
                photo = "sample%d.jpg" % (i + 1)
            frame_surface = pygame.Surface((frame_width, frame_height))
            frame_surface.fill(self.WHITE)
            frame_x = width_gap if i % 2 == 0 else (2*width_gap + frame_width)
            frame_y = height_gap if i < 2 else (2*height_gap + frame_height)
            photo_surface = pygame.image.load(photo)
            photo_width_gap = (frame_width / 100 * 8)
            photo_height_gap = (frame_height / 100 * 8)
            photo_width = frame_width - 2*photo_width_gap
            photo_height = frame_height - 2*photo_height_gap

            scaled_surface = pygame.transform.scale(photo_surface, (photo_width, photo_height))
            frame_surface.blit(scaled_surface, (photo_width_gap, photo_height_gap))

            all_photos.blit(frame_surface, (frame_x, frame_y))

        all_photos.set_colorkey(self.BLACK)
        return all_photos

    def take_photo(self):
        self.camera.start_preview(alpha=200)
        time.sleep(5)
        self.camera.stop_preview()             
        time.sleep(2)

    def on_event(self, event):
        if event.type in (pygame.QUIT, ):
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if self.stages[self.stage] == "FAREWELL":
                self._running = False
            else:
                self.stage += 1

    def on_loop(self):
        self.clock.tick(60)

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

    def on_render(self):
        self._canvas.blit(self._background, (0, 0))
        self._canvas.blit(self._photo_space, (0, 0))

        def greeting():
            self.render_text("Bereit?", bg_color=(200, 50, 20))

        def farewell():
            self.render_text("Vielen Dank!", bg_color=self.BLACK)

        def picture(number):
            self.render_text("Bild %d von %d" % (number, 4), self.BLACK)
            self.take_photo()
            self.stage += 1

        logging.warn(self.stages[self.stage])

        if self.stage == 0:
            greeting()
        elif self.stage == 5:
            farewell()
        else:
            picture(self.stage)

        pygame.display.flip()

    def on_cleanup(self):
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
