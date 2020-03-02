from enum import Enum

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


TITLE = "Chronotherium - 2020 7DRL"
WINDOW_WIDTH = 50
WINDOW_HEIGHT = 50
ENCODING = 'utf-8'
SPACING = '1x1'
FONT = resource_path('../resources/VeraMono.ttf')
TITLE_FONT = resource_path('../resources/CinzelDecorative-Regular.ttf')
FONT_SIZE = '18x18'
CELL_SIZE = '20x20'
FG_COLOR = 0xFF000000
BG_COLOR = 0xFFFFFFFF
# Option to draw UI rectangles
RECTANGLES = False
MAP_SIZE = Size(30, 30)
VIEW_SIZE = Size(30, 30)
MAP_ORIGIN = Point(10, 10)
MAP_CENTER = Point(14, 14)


class Color(Enum):
    GREEN = 0xFF557e3e
    PURPLE = 0xFF847788
    ORANGE = 0xFFcf8b26
    BLUE = 0xFF525d84
    TAN = 0xFF99886c
    TEAL = 0xFF528480
    MAGENTA = 0xFF845264
    SILVER = 0xFFa1a1a1
    BROWN = 0xFF68451d
    RED = 0xFF52282b
    GREY = 0xFF42525c


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
