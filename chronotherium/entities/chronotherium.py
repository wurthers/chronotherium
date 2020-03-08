from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color
from chronotherium.entities.items import Hourglass


class Chronotherium(Enemy):

    NAME = "Chronotherium"
    DESCRIPTION = "A hulking mass of intricate, shimmering filigree."
    GLYPH = ActorType.BEAST
    BASE_HP = 20
    BASE_TP = 7
    RANGE = 25
    XP = 5
    COLOR = Color.MAGENTA
    DROP = Hourglass
    DROP_CHANCE = 1
