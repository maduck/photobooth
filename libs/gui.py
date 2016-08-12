import pygame


class Colors(object):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

    ORANGE = (200, 50, 20)
    DARK_GRAY = (1, 1, 1)


def rounded_rect(surface, rect, color, radius=0.4):
    """
    rounded_rect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return surface.blit(rectangle, pos)


class PygameGUI(object):
    display_mode = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.limit_cpu_usage()
        self._canvas = pygame.display.set_mode((0, 0), self.display_mode)
        self.screen_width = pygame.display.Info().current_w
        self.screen_height = pygame.display.Info().current_h
        self.font = pygame.font.Font(self.config.get('font_filename'), self.config.getint('font_size'))
        pygame.mouse.set_visible(False)

    def limit_cpu_usage(self):
        self.clock.tick(self.config.getfloat("MAX_FPS"))