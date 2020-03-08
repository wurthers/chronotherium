from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import HealthPotion


class Sentry(Enemy):

    DESCRIPTION = "An ornate biped set to forever guard the halls of the Palace."
    NAME = "Eternal Sentry"
    GLYPH = ActorType.SENTRY
    BASE_HP = 2
    BASE_TP = 0
    RANGE = 3
    XP = 2
    COLOR = Color.BASE2
    DROP = HealthPotion
    DROP_CHANCE = .5
    DENSITY = .3
