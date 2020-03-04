from bearlibterminal import terminal as bearlib
from clubsandwich.geom import Point, Size

from logging import getLogger

import sys
import os


# Source: https://stackoverflow.com/a/44352931
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Color:
    BASE03 = 0xFF002B36
    BASE02 = 0xFF073642
    BASE01 = 0xFF586E75
    BASE00 = 0xFF657B83
    BASE0 = 0xFF839496
    BASE1 = 0xFF93A1A1
    BASE2 = 0xFFEEE8D5
    BASE3 = 0xFFFDF6E3
    YELLOW = 0xFFB58900
    ORANGE = 0xFFCB4B16
    RED = 0xFFDC322F
    MAGENTA = 0xFFD33682
    VIOLET = 0xFF6C71C4
    BLUE = 0xFF268BD2
    CYAN = 0xFF2AA198
    GREEN = 0xFF859900


TITLE = "Chronotherium - 2020 7DRL"
WINDOW_WIDTH = 30
WINDOW_HEIGHT = 30
ENCODING = 'utf-8'
SPACING = '1x1'
FONT = resource_path('../resources/VeraMono.ttf')
TITLE_FONT = resource_path('../resources/CinzelDecorative-Regular.ttf')
FONT_SIZE = '18x18'
CELL_SIZE = '20x20'
FG_COLOR = Color.BASE1
BG_COLOR = Color.BASE03
# Option to draw UI rectangles
RECTANGLES = False
MAP_SIZE = Size(15, 15)
VIEW_SIZE = Size(16, 16)
MAP_ORIGIN = Point(7, 7)


class Window:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            new_window = super().__new__(cls)
            new_window.__init()
            cls.__instance = new_window
        return cls.__instance

    def __init(self):
        self.logger = getLogger()
        self.height = WINDOW_HEIGHT
        self.width = WINDOW_WIDTH
        self.rectangles = RECTANGLES
        self.dimensions = str(self.width) + 'x' + str(self.height)

        h, w = FONT_SIZE.split('x')
        self.font_height = int(h)
        self.font_width = int(w)

        self.encoding = ENCODING
        self.font = FONT
        self.title_font = TITLE_FONT
        self.font_size = FONT_SIZE
        self.title = TITLE
        self.cell_size = CELL_SIZE
        self.spacing = SPACING
        self.fg_color = FG_COLOR
        self.bg_color = BG_COLOR
        self.config_str = 'terminal: encoding={}; ' \
                          'font: {}, size={}, align=center, spacing={}; ' \
                          'window: size={} title={}, cellsize={}; ' \
                          'input: filter=[arrow, keypad, keyboard, system]'.format(self.encoding,
                                                                                   self.font,
                                                                                   self.font_size,
                                                                                   self.spacing,
                                                                                   self.dimensions,
                                                                                   self.title,
                                                                                   self.cell_size)
        self.start()
        self.bearlib = bearlib

    def start(self):
        bearlib.open()
        bearlib.color(self.fg_color)
        bearlib.bkcolor(self.bg_color)
        bearlib.set(self.config_str)
