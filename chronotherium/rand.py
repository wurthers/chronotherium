from random import randrange


def d6(limit=2, over=True):
    roll = randrange(1, 6)
    if over:
        return roll > limit
    else:
        return roll < limit
