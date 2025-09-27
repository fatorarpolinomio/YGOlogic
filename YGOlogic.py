from enum import Enum
import random

# Enum básico para representar os tipos de cartas
class CardType(Enum):
    MONSTER = 1;
    MAGIC = 2;
    TRAP = 3;


class Card():

    # Cada carta pode ter nome, ataque, defesa, tipo e efeito
    def __init__(self, name, ATK, DEF, type, effect):
        self.name = name;
        self.ATK = ATK;
        self.DEF = DEF;
        self.type = type;
        self.effect = effect;

    # Getters e Setters básicos:

    def getName(self):
        return self.name;

    def getATK(self):
        return self.ATK;

    def getDEF(self):
        return self.DEF;

    def getType(self):
        return self.type;

    def getEffect(self):
        return self.effect;

class Player():

    # O jogador possui nome, vida, as cartas atuais na mão, o deck e o cemitério
    def __init__(self, name, life, cards):
        self.name = name;
        self.life = life;
        self.hand = [];
        self.deck = cards;
        self.graveyard = [];

    # Getters e Setters básicos:

    def getName(self):
        return self.name;

    def setLife(self, newLife):
        self.life = newLife;

    def getLife(self):
        return self.life;

    # Embaralhar deck
    def shuffleDeck(self):
        random.shuffle(self.deck);

    # Adicionar cartas ao cemitério do jogador
    def intoGraveyard(self, Card):
        self.graveyard.append(Card); # Coloca carta no topo do cemitério

    # Comprar cartas
    def drawCard(self):
        card = self.deck.pop(); # Retira carta do topo do deck
        self.hand.append(card); # Coloca na mão

    # Comprando cinco cartas para a mão inicial
    def initialHand(self):
        for i in range(5):
            self.drawCard();
