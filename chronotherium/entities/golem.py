from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import TimePotion
from chronotherium.rand import d6


class Golem(Enemy):

    NAME = "Hourglass Golem"
    DESCRIPTION = "Shifting sands spill from fluted glass to form massive limbs."
    GLYPH = ActorType.GOLEM
    BASE_HP = 5
    BASE_TP = 2
    RANGE = 5
    XP = 6
    COLOR = Color.VIOLET
    DROP = TimePotion
    DROP_CHANCE = .8
    TP_DRAIN_RATE = 6
    TP_DRAIN_COST = 1
    DENSITY = .2

    def __init__(self, tile, map, scene):
        self._tp_drain_clock = 0
        super().__init__(tile, map, scene)

    def ai_behavior(self):
        if not self.drain_tp():
            super().ai_behavior()
        else:
            self.turn()
            return True

    def drain_tp(self):
        if self.tp < self.TP_DRAIN_COST:
            return False
        self._tp_drain_clock += 1
        if self.visible_to(self.scene.player) and self._tp_drain_clock % self.TP_DRAIN_RATE == 0:
            self.delta_tp -= self.TP_DRAIN_COST
            if d6(limit=3, over=True):
                self.scene.player.delta_tp -= 2
                self.scene.player.update_tp()
                self.scene.log(f'The {self.NAME} drained your mana.')
                return True
            else:
                self.scene.log(f'The {self.NAME} tries to drain your mana, but you resist the attack.')
        return False
