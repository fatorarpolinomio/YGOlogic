from __future__ import annotations
import typing
from enum import Enum
import random
import Components.YGOcards as card

if typing.TYPE_CHECKING:
    import Components.YGOcards as card

# Criando deck padrão para cada jogador (sim, ambos terão o mesmo deck, isso aqui é um ep de redes meu deus)
standardDeck = [
    # Monsters ---> Percebi que precisamos colocar o nível das cartas de monstros
    card.Monster("Mago Negro", 2500, card.CardType.MONSTER, ""),
    card.Monster("Dragão Negro de Olhos Vermelhos", 2400, card.CardType.MONSTER, ""),
    card.Monster("Dragão Branco de Olhos Azuis", 3000, card.CardType.MONSTER, ""),
    card.Monster(
        "Dragão Filhote", 1200, card.CardType.MONSTER, ""
    ),  # nível 3 (arrumar dps)
    card.Monster("Guardião Celta", 1400, card.CardType.MONSTER, ""),  # nível 4
    card.Monster("Dragão do Brilho", 1900, card.CardType.MONSTER, ""),  # nível 4
    card.Monster("Elfa Mística", 800, card.CardType.MONSTER, ""),  # nível 4
    card.Monster("Kaiser Violento", 1800, card.CardType.MONSTER, ""),  # nível 5
    card.Monster("Caveira Invocada", 2500, card.CardType.MONSTER, ""),  # nível 6
    # Magic
    card.Raigeki,
    card.ReviverMonstro,
    card.PoteDaGanancia,
    card.TempestadePesada,
    # Traps
    card.MirrorForce,
    card.Cilindro,
    card.BuracoArmadilha,
    card.Aparelho,
    card.NegateAttack,
]


class Player:
    # O jogador possui nome, vida, as cartas atuais na mão, o deck, o cemitério
    # Além disso, temos uma lista de monstros no campo e uma lista de magias e armadilhas no campo
    def __init__(self, name, life):
        self.name = name
        self.life = life
        self.hand = []
        self.deck = standardDeck
        self.graveyard = []
        self.monstersInField = []
        self.monstersCount = (
            0  # Contador para a quantidade de monstros que o jogador controla
        )
        self.spellsAndTrapsInField = []
        self.spellsAndTrapsCount = (
            0  # Contador para a quantidade de Spells e Traps no campo
        )

    # Embaralhar deck
    def shuffleDeck(self):
        random.shuffle(self.deck)

    # Adicionar cartas ao cemitério do jogador
    def intoGraveyard(self, Card):
        self.graveyard.append(Card)  # Coloca carta no topo do cemitério

    def monsterIntoGraveyard(self, monster: card.Monster):
        if monster in self.monstersInField:
            self.monstersInField.remove(monster)
            self.graveyard.append(monster)

    def spellTrapIntoGraveyard(self, spellTrap):
        if spellTrap in self.spellsAndTrapsInField:
            self.spellsAndTrapsInField.remove(spellTrap)
            self.graveyard.append(spellTrap)

    # Comprar cartas
    def drawCard(self):
        card = self.deck.pop()  # Retira carta do topo do deck
        self.hand.append(card)  # Coloca na mão

    # Comprando três cartas para a mão inicial
    def initialHand(self):
        for i in range(3):
            self.drawCard()

    # Função para invocar monstros
    def summonMonster(self, monster: card.Card):
        if self.monstersCount == 3:
            print("Você atingiu o limite de monstros em campo (max: 3)")
            return
        self.monstersInField.append(monster)
        print(f"Você invocou {monster.name}!")
        self.monstersCount += 1
        return

    # Função para colocar carta virada para baixo
    def setCard(self, card: card.Card):
        if self.spellsAndTrapsCount == 3:
            print("Você atingiu o limite de magias e armadilhas em campo (max 3)")
            return False

        self.spellsAndTrapsInField.append(card)
        print(f"Você colocou a carta {card.name} virada para baixo")
        self.spellsAndTrapsCount += 1
        return True

    # Função para ativar magia
    def activateSpell(self, spell: card.Card):
        if self.spellsAndTrapsCount == 3:
            print("Você atingiu o limite de magias e armadilhas em campo (max 3)")
            return False

        print(f"Ativando a magia {spell.name}: ")
