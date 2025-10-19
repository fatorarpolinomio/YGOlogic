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
    MAGIC = 2
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
    def apply_effect(self, player, opponent):
        self.effect(player, opponent)


class Monster(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(name, ATK, type, effect)
        self.canAttack = True

    @override
    def effect(self, player: Player, opponent: Player):
        return None


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
        return super().effect()


class Cilindro(Card):
    def __init__(self, name, ATK, type, effect):
        super().__init__(
            "Cilindro Mágico",
            None,
            CardType.TRAP,
            "Quando um monstro do oponente declarar um ataque: escolha o monstro atacante; negue o ataque e cause dano ao seu oponente igual ao ATK dele.",
        )

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
