from __future__ import annotations
from Components.cards.YGOcards import Card, CardType
import typing
from typing import override
from enum import Enum
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from Components.YGOplayer import Player


class Monster(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(name, ATK, type, effect)
        self.canAttack = True

    @override
    def effect(self, player: Player, opponent: Player):
        return None
