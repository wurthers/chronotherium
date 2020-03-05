from chronotherium.entities.entity import Actor, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import HealthPotion


class Knight(Actor):

    NAME = "Clockwork Knight"
    DESCRIPTION = "A windup automata bent on giant-slaying"
    GLYPH = ActorType.KNIGHT
    BASE_HP = 2
    BASE_TP = 0
    COLOR = Color.BASE02
    DROP = HealthPotion

    def on_death(self):
        pass

    def ai_behavior(self):
        pass
