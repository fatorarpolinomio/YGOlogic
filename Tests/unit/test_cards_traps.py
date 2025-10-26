import unittest
from unittest.mock import Mock, MagicMock

# Importando as classes necessárias
from Components.YGOplayer import Player
from Components.cards.Traps import MirrorForce, Cilindro
from Components.cards.Monsters import Monster # <-- Alteração: Importa o Monstro real
from Components.cards.YGOcards import CardType # <-- Alteração: Necessário para criar Monstros

class TestTrapCards(unittest.TestCase):

    def setUp(self):
        self.player = Player("Joey", 4000) # Jogador que ativa a armadilha (defensor)
        self.opponent = Player("Rex", 4000) # Jogador que ataca

        # Alteração: Usando a classe Monster real
        self.opponent_monster1 = Monster("Megazowler", 1800, CardType.MONSTER, "")
        self.opponent_monster2 = Monster("Two-Headed King Rex", 1600, CardType.MONSTER, "")
        self.player_monster = Monster("Flame Swordsman", 1800, CardType.MONSTER, "")

    def test_mirror_force_effect(self):
        # Configura o campo do oponente
        self.opponent.monstersInField = [self.opponent_monster1, self.opponent_monster2]
        self.opponent.graveyard = []
        
        # Cria e ativa a Força do Espelho
        mirror_force = MirrorForce()
        mirror_force.effect(self.player, self.opponent)
        
        # Verifica se o campo do oponente está vazio
        self.assertEqual(len(self.opponent.monstersInField), 0)
        # Verifica se os monstros foram para o cemitério
        self.assertIn(self.opponent_monster1, self.opponent.graveyard)
        self.assertIn(self.opponent_monster2, self.opponent.graveyard)

    def test_cilindro_magico_effect(self):
        # Configura o monstro atacante
        attacking_monster = self.opponent_monster1 # Atacando com 1800 ATK
        
        initial_opponent_life = self.opponent.life # 4000
        
        # Cria e ativa o Cilindro Mágico
        cilindro = Cilindro()
        # Definimos manualmente o monstro atacante, como o motor do jogo faria
        cilindro.attackingMonster = attacking_monster
        
        cilindro.effect(self.player, self.opponent)
        
        # Verifica se o oponente tomou o dano
        expected_life = initial_opponent_life - attacking_monster.ATK
        self.assertEqual(self.opponent.life, expected_life) # 4000 - 1800 = 2200

if __name__ == '__main__':
    unittest.main()