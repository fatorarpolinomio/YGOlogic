from __future__ import annotations
from contextlib import AsyncExitStack
from Components.cards.YGOcards import Card, CardType
from Components.cards.Monsters import Monster
import typing
from typing import override
from enum import Enum
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from Components.YGOplayer import Player


# Classes para cada armadilha
class MirrorForce(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Força do Espelho",
            None,
            CardType.TRAP,
            "Quando um monstro do oponente declarar um ataque: destrua todos os monstros em Posição de Ataque que seu oponente controla.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        # Mandando todos para o cemitério
        for monster in opponent.monstersInField:
            opponent.monsterIntoGraveyard(monster)
        return


class Cilindro(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Cilindro Mágico",
            None,
            CardType.TRAP,
            "Quando um monstro do oponente declarar um ataque: escolha o monstro atacante; negue o ataque e cause dano ao seu oponente igual ao ATK dele.",
        )
        self.attackingMonster = ""

    def setAttackingMonster(self, monster: Monster):
        self.attackingMonster = monster

    @override
    def effect(self, player: Player, opponent: Player):
        return super().effect()


class BuracoArmadilha(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Buraco Armadilha",
            None,
            CardType.TRAP,
            "Quando seu oponente Invocar por Invocação-Normal ou Virar um monstro com 1000 ou mais de ATK: escolha o monstro; destrua o alvo.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        return super().effect()


class Aparelho(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Aparelho de Evacuação Obrigatória",
            None,
            CardType.TRAP,
            "Escolha 1 monstro no campo; devolva o alvo para a mão.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        return super().effect()


class NegateAttack(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Negativação de Ataque",
            None,
            CardType.TRAP,
            "Quando um monstro do oponente declarar um ataque: escolha o monstro atacante; negue o ataque.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        return super().effect()
