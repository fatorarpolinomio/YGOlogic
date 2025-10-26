import unittest
from unittest.mock import Mock, MagicMock

# Importando as classes necessárias
from Components.YGOplayer import Player
from Components.cards.Spells import Raigeki, PoteDaGanancia, TempestadePesada
from Components.cards.Monsters import Monster # <-- Alteração: Importa o Monstro real
from Components.cards.YGOcards import CardType # <-- Alteração: Necessário para criar Monstros

class TestSpellCards(unittest.TestCase):

    def setUp(self):
        # Configuração inicial para cada teste
        self.player = Player("Yugi", 4000)
        self.opponent = Player("Kaiba", 4000)

        # Alteração: Usando a classe Monster real
        self.monster1 = Monster("Blue-Eyes White Dragon", 3000, CardType.MONSTER, "")
        self.monster2 = Monster("Battle Ox", 1700, CardType.MONSTER, "")
        
        # Mocks para magias/armadilhas (para teste de Tempestade Pesada)
        self.spell1 = Mock(name="Spell Card 1")
        self.trap1 = Mock(name="Trap Card 1")

    def test_raigeki_effect(self):
        # Configura o campo do oponente
        self.opponent.monstersInField = [self.monster1, self.monster2]
        self.opponent.graveyard = []
        
        # Cria e ativa o Raigeki
        raigeki = Raigeki()
        raigeki.effect(self.player, self.opponent)
        
        # Verifica se o campo do oponente está vazio
        self.assertEqual(len(self.opponent.monstersInField), 0)
        # Verifica se os monstros foram para o cemitério
        self.assertIn(self.monster1, self.opponent.graveyard)
        self.assertIn(self.monster2, self.opponent.graveyard)
        self.assertEqual(len(self.opponent.graveyard), 2)

    def test_pote_da_ganancia_effect(self):
        # O Player agora inicializa com o standardDeck.
        # Para um teste unitário controlado, ainda é uma boa prática
        # substituir o deck por um mock.
        self.player.deck = [Mock(name="Card 1"), Mock(name="Card 2"), Mock(name="Card 3")]
        self.player.hand = []
        
        initial_deck_size = len(self.player.deck)
        
        # Cria e ativa o Pote da Ganância
        pote = PoteDaGanancia()
        pote.effect(self.player, self.opponent)
        
        # Verifica se o jogador comprou 2 cartas
        self.assertEqual(len(self.player.hand), 2)
        # Verifica se o deck diminuiu em 2 cartas
        self.assertEqual(len(self.player.deck), initial_deck_size - 2)

    def test_tempestade_pesada_effect(self):
        # Configura o campo de S/T de ambos os jogadores
        self.player.spellsAndTrapsInField = [self.spell1]
        self.opponent.spellsAndTrapsInField = [self.trap1]
        self.player.graveyard = []
        self.opponent.graveyard = []
        
        # Cria e ativa a Tempestade Pesada
        tempestade = TempestadePesada()
        tempestade.effect(self.player, self.opponent)
        
        # Verifica se os campos de S/T estão vazios
        self.assertEqual(len(self.player.spellsAndTrapsInField), 0)
        self.assertEqual(len(self.opponent.spellsAndTrapsInField), 0)
        
        # Verifica se as cartas foram para os cemitérios
        self.assertIn(self.spell1, self.player.graveyard)
        self.assertIn(self.trap1, self.opponent.graveyard)

if __name__ == '__main__':
    unittest.main()