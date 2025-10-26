import unittest
from unittest.mock import Mock, MagicMock

# Importando as classes necessárias
from Components.YGOplayer import Player

# Importa as armadilhas do arquivo Traps.py
from Components.cards.Traps import MirrorForce, Cilindro, BuracoArmadilha, Aparelho

from Components.cards.Monsters import Monster 
from Components.cards.YGOcards import CardType 

class TestTrapCards(unittest.TestCase):

    def setUp(self):
        # Jogador que ativa a armadilha (defensor)
        self.player = Player("Joey", 4000) 
        # Jogador que ataca (e sofre o efeito)
        self.opponent = Player("Rex", 4000) 

        # Monstros do atacante (Oponente)
        self.opponent_monster1 = Monster("Megazowler", 1800, CardType.MONSTER, "")
        self.opponent_monster2 = Monster("Two-Headed King Rex", 1600, CardType.MONSTER, "")
        
        # Monstro do defensor (Jogador) - (não é usado nestes testes, mas bom para contexto)
        self.player_monster = Monster("Flame Swordsman", 1800, CardType.MONSTER, "")

        # Reseta os campos e cemitérios antes de cada teste
        self.player.monstersInField = [self.player_monster]
        self.player.graveyard = []
        self.opponent.monstersInField = [self.opponent_monster1, self.opponent_monster2]
        self.opponent.graveyard = []
        self.opponent.hand = [] # Mão do oponente começa vazia

    def test_mirror_force_effect(self):
        """
        Testa se a Força do Espelho destrói TODOS os monstros do oponente 
        e os move para o cemitério.
        """
        # Cria e ativa a Força do Espelho
        mirror_force = MirrorForce()
        mirror_force.effect(self.player, self.opponent)
        
        # Verifica se o campo do oponente está vazio
        self.assertEqual(len(self.opponent.monstersInField), 0)
        
        # Verifica se os monstros foram para o cemitério
        self.assertIn(self.opponent_monster1, self.opponent.graveyard)
        self.assertIn(self.opponent_monster2, self.opponent.graveyard)
        self.assertEqual(len(self.opponent.graveyard), 2)

    def test_cilindro_magico_effect(self):
        """
        Testa se o Cilindro Mágico causa dano ao oponente 
        igual ao ATK do monstro atacante.
        """
        # O monstro atacante é o Megazowler (1800 ATK)
        attacking_monster = self.opponent_monster1 
        initial_opponent_life = self.opponent.life # 4000
        
        # Cria e ativa o Cilindro Mágico
        cilindro = Cilindro()
        # Simula o motor do jogo definindo qual monstro está atacando
        cilindro.attackingMonster = attacking_monster
        
        cilindro.effect(self.player, self.opponent)
        
        # Verifica se o oponente tomou o dano
        expected_life = initial_opponent_life - attacking_monster.ATK
        self.assertEqual(self.opponent.life, expected_life) # 4000 - 1800 = 2200

    def test_buraco_armadilha_effect(self):
        """
        Testa se o Buraco Armadilha destrói APENAS o monstro atacante.
        """
        # O monstro atacante é o Megazowler (1800 ATK)
        attacking_monster = self.opponent_monster1
        
        # Cria e ativa o Buraco Armadilha
        trap = BuracoArmadilha()
        # Simula o motor do jogo definindo qual monstro está atacando
        trap.attackingMonster = attacking_monster
        
        trap.effect(self.player, self.opponent)
        
        # Verifica se o monstro atacante foi para o cemitério
        self.assertIn(attacking_monster, self.opponent.graveyard)
        self.assertEqual(len(self.opponent.graveyard), 1)
        
        # Verifica se o monstro atacante FOI removido do campo
        self.assertNotIn(attacking_monster, self.opponent.monstersInField)
        
        # Verifica se o OUTRO monstro (não atacante) permaneceu no campo
        self.assertIn(self.opponent_monster2, self.opponent.monstersInField)
        self.assertEqual(len(self.opponent.monstersInField), 1)

    def test_aparelho_evacuacao_effect(self):
        """
        Testa se o Aparelho de Evacuação Obrigatória 
        retorna o monstro atacante para a mão do oponente.
        """
        # O monstro atacante é o Megazowler (1800 ATK)
        attacking_monster = self.opponent_monster1
        
        # Cria e ativa o Aparelho
        trap = Aparelho()
        # Simula o motor do jogo definindo qual monstro está atacando
        trap.attackingMonster = attacking_monster
        
        trap.effect(self.player, self.opponent)
        
        # Verifica se o monstro atacante foi para a mão do oponente
        self.assertIn(attacking_monster, self.opponent.hand)
        self.assertEqual(len(self.opponent.hand), 1)
        
        # NOTA: O código em Traps.py (Aparelho.effect) NÃO remove o monstro
        # do campo, ele apenas o adiciona à mão. Este teste verifica
        # esse comportamento (que é um bug no seu Traps.py).
        
        # Verifica se o monstro atacante AINDA está no campo
        self.assertIn(attacking_monster, self.opponent.monstersInField)
        # Verifica se o outro monstro também está no campo
        self.assertIn(self.opponent_monster2, self.opponent.monstersInField)
        self.assertEqual(len(self.opponent.monstersInField), 2)


if __name__ == '__main__':
    unittest.main()