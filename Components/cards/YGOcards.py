from __future__ import annotations
import typing
from typing import override
from enum import Enum
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from Components.YGOplayer import Player


# Enum básico para representar os tipos de cartas
class CardType(Enum):
    MONSTER = 1
    SPELL = 2
    TRAP = 3


class Card(ABC):
    # Cada carta pode ter nome, ataque tipo e efeito
    def __init__(self, name, ATK, type, effect):
        self.name = name
        self.ATK = ATK
        self.type = type
        self.effectDescription = effect
        self.canAttack = False

    def to_dict(self):
        """converte o objeto Card para um dicionário para serialização em JSON"""
        return {
            "name": self.name,
            "ATK": self.ATK,
            "type": self.type.name,  # .name para pegar o nome do Enum como texto
            "effect": self.effect,
        }

    def __repr__(self):
        """retorna uma representação em string do objeto"""
        return f"Card({self.name}, ATK:{self.ATK})"

    @abstractmethod
    def effect(self, player: Player, opponent: Player):
        pass

    # Aplica o efeito da carta no jogador e no adversário
    def apply_effect(self, player: Player, opponent: Player):
        self.effect(player, opponent)
