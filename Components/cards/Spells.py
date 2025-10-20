from __future__ import annotations
from Components.cards.YGOcards import Card, CardType
import typing
from typing import override


if typing.TYPE_CHECKING:
    from Components.YGOplayer import Player


# Classes para cada magia
class Raigeki(Card):
    def __init__(self, name, ATK, type, effect):
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
            opponent.intoGraveyard(monster)

        # Limpando campo do oponente
        opponent.monstersInField.clear()
        print("Morreu de choque!! Todos os monstros do seu oponente foram destruídos!")
        return


class ReviverMonstro(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Reviver Monstro",
            None,
            CardType.MAGIC,
            "Ressuscita um monstro do seu cemitério.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        count = 0
        print("Seu cemitério:")
        for monster in player.graveyard:
            print(f"{count}) {monster}")
            count += 1

        escolhido = int(input("Terror do INSS! Escolha um monstro para ser revivido: "))
        while escolhido < 0 or escolhido > count:
            escolhido = int(input("ID da cova inválido, tente novamente: "))

        player.summonMonster(player.graveyard[escolhido])
        return


class PoteDaGanancia(Card):
    def __init__(self, name, ATK, type, effect):
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
    def __init__(self, name, ATK, type, effect):
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
            player.intoGraveyard(spellOrTrap)
        player.spellsAndTrapsInField.clear()
        # Limpando magias e armadilhas do oponente
        for spellOrTrap in opponent.spellsAndTrapsInField:
            opponent.intoGraveyard(spellOrTrap)
        opponent.spellsAndTrapsInField.clear()
        print("Alerta vermelho para tempestade forte (sem aula na each)")
        return
