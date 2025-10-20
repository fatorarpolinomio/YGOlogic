from __future__ import annotations
import typing
from enum import Enum
import random

import Components.cards.StandardDeck as deck
import Components.cards.Monsters as monsters
import Components.cards.Spells as spells
import Components.cards.Traps as traps

if typing.TYPE_CHECKING:
    import Components.cards.YGOcards as card


class Player:
    # O jogador possui nome, vida, as cartas atuais na mão, o deck, o cemitério
    # Além disso, temos uma lista de monstros no campo e uma lista de magias e armadilhas no campo
    def __init__(self, name, life):
        self.name = name
        self.life = life
        self.hand = []
        self.deck = deck.standardDeck
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

    def monsterIntoGraveyard(self, monster: monsters.Monster):
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
