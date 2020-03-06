from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import HealthPotion


class Knight(Enemy):

    NAME = "Clockwork Knight"
    DESCRIPTION = "A windup automata bent on giant-slaying"
    GLYPH = ActorType.KNIGHT
    BASE_HP = 2
    BASE_TP = 0
    XP = 1
    COLOR = Color.BASE02
    DROP = HealthPotion

    def ai_behavior(self):
        pass
