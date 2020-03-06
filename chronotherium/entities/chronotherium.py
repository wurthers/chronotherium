from random import randrange

from clubsandwich.geom import Point

from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color
from chronotherium.entities.items import Hourglass


class Chronotherium(Enemy):

    NAME = "Chronotherium"
    DESCRIPTION = "A hulking mass of intricate shimmering filigree"
    GLYPH = ActorType.BEAST
    BASE_HP = 20
    BASE_TP = 7
    XP = 5
    COLOR = Color.MAGENTA
    DROP = Hourglass

    def ai_behavior(self):
        x = randrange(-1, 1)
        y = randrange(-1, 1)
        delta = Point(x, y)
        self.actor_move(delta)
        self.turn()
