import unittest
import copy  # Necessário para testar o shuffle
from unittest.mock import Mock

from Components.YGOplayer import Player
import Components.cards.StandardDeck as deck  # Importa o deck real
from Components.cards.Monsters import Monster
from Components.cards.Spells import Raigeki  # Usado para teste de cemitério
from Components.cards.YGOcards import CardType


class TestPlayerInitialization(unittest.TestCase):
    """
    Testa a CRIAÇÃO e PREPARAÇÃO de um novo jogador,
    usando o deck real (StandardDeck).
    """

    def setUp(self):
        # Cria um jogador novo. __init__ automaticamente carrega o StandardDeck
        self.player = Player("Test Player", 4000)

    def test_initialization(self):
        """Testa se o __init__ do Player define os valores padrão corretamente."""
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.life, 4000)
        
        # Testa se os campos/mão/cemitério começam vazios
        self.assertEqual(len(self.player.hand), 0)
        self.assertEqual(len(self.player.monstersInField), 0)
        self.assertEqual(len(self.player.spellsAndTrapsInField), 0)
        self.assertEqual(len(self.player.graveyard), 0)
        
        # Testa se o deck foi carregado corretamente
        self.assertGreater(len(self.player.deck), 0)
        # Compara a lista de cartas do jogador com a lista original do StandardDeck
        self.assertListEqual(self.player.deck, deck.standardDeck)

    def test_initial_hand(self):
        """Testa se o método initialHand() compra 3 cartas."""
        initial_deck_size = len(self.player.deck)
        
        self.player.initialHand()
        
        self.assertEqual(len(self.player.hand), 3)
        self.assertEqual(len(self.player.deck), initial_deck_size - 3)

    def test_shuffle_deck(self):
        """Testa se o shuffleDeck() de fato reordena o deck."""
        
        # Faz uma cópia exata da ordem atual do deck
        original_deck_order = copy.deepcopy(self.player.deck)
        # Cria um "set" (conjunto) para verificar se as cartas são as mesmas
        original_deck_contents = set(self.player.deck)
        
        self.player.shuffleDeck()
        
        shuffled_deck_order = self.player.deck
        shuffled_deck_contents = set(self.player.deck)
        
        # 1. Verifica se as cartas são as mesmas (nenhuma perdida ou adicionada)
        self.assertEqual(original_deck_contents, shuffled_deck_contents)
        
        # 2. Verifica se a ordem é (muito provavelmente) diferente
        # Nota: Este teste pode falhar 1 em N! (fatorial) vezes,
        # mas N é tão grande que é seguro usar.
        self.assertNotEqual(original_deck_order, shuffled_deck_order)


class TestPlayerActions(unittest.TestCase):
    """
    Testa as AÇÕES isoladas de um jogador (comprar, mover para cemitério),
    usando um deck "mockado" (falso) para controle total.
    """

    def setUp(self):
        # Cria um jogador
        self.player = Player("Test Player", 4000)
        
        # Cria cartas mockadas para testes de draw
        self.card1 = Mock(name="Card 1")
        self.card2 = Mock(name="Card 2")
        self.card3 = Mock(name="Card 3")
        
        # Define manualmente o deck para testes controlados
        self.player.deck = [self.card1, self.card2, self.card3]
        self.player.hand = []
        self.player.graveyard = []

    def test_draw_card_success(self):
        """Testa se drawCard() move 1 carta do deck para a mão."""
        initial_deck_size = len(self.player.deck)
        self.assertEqual(len(self.player.hand), 0)
        
        # Chama a função de comprar carta
        card_drawn = self.player.drawCard()
        
        # Verifica se a carta retornada é a correta
        self.assertEqual(card_drawn, self.card1)
        # Verifica se a mão aumentou
        self.assertEqual(len(self.player.hand), 1)
        # Verifica se a carta correta foi para a mão
        self.assertIn(self.card1, self.player.hand)
        # Verifica se o deck diminuiu
        self.assertEqual(len(self.player.deck), initial_deck_size - 1)

    def test_draw_card_empty_deck(self):
        """Testa se comprar de um deck vazio levanta um IndexError."""
        self.player.deck = []
        
        with self.assertRaises(IndexError):
            self.player.drawCard()

    def test_monster_into_graveyard_from_field(self):
        """Testa mover um monstro do CAMPO para o cemitério."""
        monster_to_bury = Monster("Test Monster", 1000, CardType.MONSTER, "")
        self.player.monstersInField = [monster_to_bury]
        self.player.graveyard = []
        
        self.player.monsterIntoGraveyard(monster_to_bury)
        
        # Verifica
        self.assertEqual(len(self.player.monstersInField), 0)
        self.assertEqual(len(self.player.graveyard), 1)
        self.assertIn(monster_to_bury, self.player.graveyard)

    def test_spell_trap_into_graveyard_from_field(self):
        """Testa mover uma Magia/Armadilha do CAMPO para o cemitério."""
        st_to_bury = Raigeki()
        self.player.spellsAndTrapsInField = [st_to_bury]
        self.player.graveyard = []
        
        self.player.spellTrapIntoGraveyard(st_to_bury)
        
        # Verifica
        self.assertEqual(len(self.player.spellsAndTrapsInField), 0)
        self.assertEqual(len(self.player.graveyard), 1)
        self.assertIn(st_to_bury, self.player.graveyard)

    def test_spell_trap_into_graveyard_from_hand(self):
        """
        Testa mover uma Magia/Armadilha (ativada da MÃO) para o cemitério.
        (O método spellTrapIntoGraveyard também lida com isso)
        """
        st_to_bury = Raigeki()
        # A carta não está no campo:
        self.player.spellsAndTrapsInField = []
        self.player.graveyard = []
        
        self.player.spellTrapIntoGraveyard(st_to_bury)
        
        # Verifica
        self.assertEqual(len(self.player.spellsAndTrapsInField), 0) # Campo continua vazio
        self.assertEqual(len(self.player.graveyard), 1)
        self.assertIn(st_to_bury, self.player.graveyard)

if __name__ == '__main__':
    unittest.main()