from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import HealthPotion


class Knight(Enemy):

    NAME = "Clockwork Knight"
    DESCRIPTION = "A windup automaton bent on giant-slaying."
    GLYPH = ActorType.KNIGHT
    BASE_HP = 2
    BASE_TP = 0
    RANGE = 9
    XP = 1
    COLOR = Color.GREEN
    DROP = HealthPotion
