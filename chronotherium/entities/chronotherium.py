from chronotherium.entities.entity import Actor, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import Hourglass


class Chronotherium(Actor):

    NAME = "Chronotherium"
    DESCRIPTION = "A hulking mass of intricate shimmering filigree"
    GLYPH = ActorType.BEAST
    BASE_HP = 25
    BASE_TP = 10
    COLOR = Color.MAGENTA
    DROP = Hourglass

    def on_death(self):
        pass

    def ai_behavior(self):
        pass
