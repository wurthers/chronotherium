from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import TimePotion


class Golem(Enemy):

    NAME = "Hourglass Golem"
    DESCRIPTION = "Shifting sands spill from cracked fluted glass to form massive limbs."
    GLYPH = ActorType.GOLEM
    BASE_HP = 5
    BASE_TP = 3
    XP = 3
    COLOR = Color.VIOLET
    DROP = TimePotion

    def drain_tp(self):
        # Wander around generally towards the player, firing a drain tp spell every turn
        pass
