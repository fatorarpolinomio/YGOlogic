from __future__ import annotations

from Components.cards.YGOcards import Card, CardType
from Components.cards.Monsters import Monster
import typing
from typing import override

if typing.TYPE_CHECKING:
    from Components.YGOplayer import Player


# Classes para cada armadilha
class MirrorForce(Card):
    def __init__(self):
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
    def __init__(self):
        super().__init__(
            "Cilindro Mágico",
            None,
            CardType.TRAP,
            "Quando um monstro do oponente declarar um ataque: escolha o monstro atacante; negue o ataque e cause dano ao seu oponente igual ao ATK dele.",
        )
        self.attackingMonster = None

    @override
    def effect(self, player: Player, opponent: Player):
        opponent.life = opponent.life - self.attackingMonster.ATK
        return


class BuracoArmadilha(Card):
    def __init__(self):
        super().__init__(
            "Buraco Armadilha",
            None,
            CardType.TRAP,
            "Quando seu oponente atacar com um monstro: escolha o monstro; destrua o alvo.",
        )
        self.attackingMonster = None

    @override
    def effect(self, player: Player, opponent: Player):
        opponent.monsterIntoGraveyard(self.attackingMonster)
        return


class Aparelho(Card):
    def __init__(self):
        super().__init__(
            "Aparelho de Evacuação Obrigatória",
            None,
            CardType.TRAP,
            "Quando seu oponente atacar com um monstro: escolha o monstro; devolva o alvo para a mão.",
        )
        self.attackingMonster = None

    @override
    def effect(self, player: Player, opponent: Player):
        opponent.hand.append(self.attackingMonster)
        return


class NegateAttack(Card):
    def __init__(self):
        super().__init__(
            "Negativação de Ataque",
            None,
            CardType.TRAP,
            "Quando um monstro do oponente declarar um ataque: escolha o monstro atacante; negue o ataque.",
        )
        self.attackingMonster = None

    @override
    def effect(self, player: Player, opponent: Player):
        return
