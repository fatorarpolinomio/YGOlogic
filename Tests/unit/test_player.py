import unittest
from unittest.mock import Mock

from Components.YGOplayer import Player
# Alterações: Importando cartas reais para testes de cemitério
from Components.cards.Monsters import Monster
from Components.cards.Spells import Raigeki
from Components.cards.YGOcards import CardType

class TestPlayer(unittest.TestCase):

    def setUp(self):
        # O Player() agora funciona pois StandardDeck.py existe
        self.player = Player("Test Player", 4000)
        
        # Criamos cartas mockadas para testes de draw
        self.card1 = Mock(name="Card 1")
        self.card2 = Mock(name="Card 2")
        self.card3 = Mock(name="Card 3")
        
        # Definimos manualmente o deck para o teste de draw
        self.player.deck = [self.card1, self.card2, self.card3]
        self.player.hand = []
        self.player.graveyard = []

    def test_draw_card_success(self):
        # Este teste permanece o mesmo, pois testar com um deck mockado
        # isola a lógica de "comprar" (pop) da lógica de "ter um deck".
        initial_deck_size = len(self.player.deck)
        self.assertEqual(len(self.player.hand), 0)
        
        # Chama a função de comprar carta
        self.player.drawCard()
        
        # Verifica se a mão aumentou
        self.assertEqual(len(self.player.hand), 1)
        # Verifica se a carta correta foi para a mão
        self.assertIn(self.card1, self.player.hand)
        # Verifica se o deck diminuiu
        self.assertEqual(len(self.player.deck), initial_deck_size - 1)
        # Verifica se a carta correta foi removida do deck
        self.assertNotIn(self.card1, self.player.deck)

    def test_draw_card_empty_deck(self):
        # Esvazia o deck
        self.player.deck = []
        
        # Tenta comprar
        with self.assertRaises(IndexError):
            self.player.drawCard()

    def test_monster_into_graveyard(self):
        # Alteração: Usa um Monstro real
        monster_to_bury = Monster("Test Monster", 1000, CardType.MONSTER, "")
        self.player.monstersInField = [monster_to_bury]
        self.player.graveyard = [] # Reseta o cemitério
        
        self.assertEqual(len(self.player.graveyard), 0)
        
        # Move o monstro para o cemitério
        self.player.monsterIntoGraveyard(monster_to_bury)
        
        # Verifica
        self.assertEqual(len(self.player.monstersInField), 0)
        self.assertEqual(len(self.player.graveyard), 1)
        self.assertIn(monster_to_bury, self.player.graveyard)

    def test_spell_trap_into_graveyard(self):
        # Alteração: Usa uma Spell real
        st_to_bury = Raigeki()
        self.player.spellsAndTrapsInField = [st_to_bury]
        self.player.graveyard = [] # Reseta o cemitério
        
        self.assertEqual(len(self.player.graveyard), 0)
        
        # Move a carta para o cemitério
        self.player.spellTrapIntoGraveyard(st_to_bury)
        
        # Verifica
        self.assertEqual(len(self.player.spellsAndTrapsInField), 0)
        self.assertEqual(len(self.player.graveyard), 1)
        self.assertIn(st_to_bury, self.player.graveyard)

if __name__ == '__main__':
    unittest.main()