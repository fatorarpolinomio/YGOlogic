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

    def to_dict(self):
        """converte o objeto Card para um dicionário para serialização em JSON"""
        return {
            "name": self.name,
            "ATK": self.ATK,
            "DEF": self.DEF,
            "type": self.type.name, # .name para pegar o nome do Enum como texto
            "effect": self.effect
        }
    
    def __repr__(self):
        """retorna uma representação em string do objeto"""
        return f"Card({self.name}, ATK:{self.ATK}, DEF:{self.DEF})"

class Player():

    # O jogador possui nome, vida, as cartas atuais na mão, o deck e o cemitério
    def __init__(self, name, life, cards):
        self.name = name;
        self.life = life;
        self.hand = [];
        self.deck = cards;
        self.graveyard = [];

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
            
    def create_standard_deck():
    """cria e retorna uma lista de cartas padrão para um novo jogador"""
    deck = [
        Card("Mago Negro", 2500, 2100, CardType.MONSTER),
        Card("Dragão Negro de Olhos Vermelhos", 2400, 2000, CardType.MONSTER),
        Card("Dragão Branco de Olhos Azuis", 3000, 2500, CardType.MONSTER),
        Card("Raigeki", None, None, CardType.MAGIC, "Destrói todos os monstros no campo do oponente."),
        Card("Monster Reborn", None, None, CardType.MAGIC, "Ressuscita um monstro de qualquer cemitério.")
       
        # temos que decidir quais cartas por no deck inteiro e será o mesmo para ambos jogadores?
    ]
    return deck
