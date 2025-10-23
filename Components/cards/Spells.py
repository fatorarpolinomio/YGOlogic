from __future__ import annotations
from Components.cards.YGOcards import Card, CardType
import typing
from typing import override


if typing.TYPE_CHECKING:
    from Components.YGOplayer import Player


# Classes para cada magia
class Raigeki(Card):
    def __init__(self):
        super().__init__(
            "Raigeki",
            None,
            CardType.MAGIC,
            "Destrói todos os monstros no campo do oponente.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        # Mandando todos para o cemitério
        for monster in opponent.monstersInField:
            opponent.monsterIntoGraveyard(monster)

        # Limpando campo do oponente
        opponent.monstersInField.clear()
        print("Morreu de choque!! Todos os monstros do seu oponente foram destruídos!")
        return


class DianKeto(Card):
    def __init__(self):
        super().__init__(
            "Dian Keto, Mestre da Cura",
            None,
            CardType.MAGIC,
            "Ganhe 1000 pontos de vida.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        player.life += 1000
        return


class PoteDaGanancia(Card):
    def __init__(self):
        super().__init__(
            "Pote da Ganância", None, CardType.MAGIC, "Compre duas cartas."
        )

    @override
    def effect(self, player: Player, opponent: Player):
        player.drawCard()
        player.drawCard()
        print("O que essa carta faz? Me permite comprar duas cartas do meu baralho!")
        return


class TempestadePesada(Card):
    def __init__(self):
        super().__init__(
            "Tempestade Pesada",
            None,
            CardType.MAGIC,
            "Destrua todos os Cards de Magia e Armadilha no campo..",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        # Limpando magias e armadilhas do controlador da carta
        for spellOrTrap in player.spellsAndTrapsInField:
            player.spellTrapIntoGraveyard(spellOrTrap)
        player.spellsAndTrapsInField.clear()
        # Limpando magias e armadilhas do oponente
        for spellOrTrap in opponent.spellsAndTrapsInField:
            opponent.spellTrapIntoGraveyard(spellOrTrap)
        opponent.spellsAndTrapsInField.clear()
        print("Alerta vermelho para tempestade forte (sem aula na each)")
        return
