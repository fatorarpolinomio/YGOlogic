import unittest
from unittest.mock import Mock, MagicMock

from Components.YGOplayer import Player
from Components.YGOengine import YGOengine
from Communication.network import Network
from Components.cards.Monsters import Monster # <-- Alteração: Importa o Monstro real
from Components.cards.YGOcards import CardType # <-- Alteração: Necessário para criar Monstros

class TestEngineBattle(unittest.TestCase):

    def setUp(self):
        # Agora Player() funciona perfeitamente
        self.player1 = Player("P1", 4000)
        self.player2 = Player("P2", 4000)
        self.mock_network = Mock(spec=Network)
        
        self.engine = YGOengine(self.player1, self.player2, self.mock_network, is_host=True)
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        
        # Alteração: Usando a classe Monster real
        self.p1_monster = Monster("Attacker", 2000, CardType.MONSTER, "")
        self.p2_monster = Monster("Defender", 1500, CardType.MONSTER, "")
        
        self.player1.monstersInField = [self.p1_monster]
        self.player2.monstersInField = [self.p2_monster]
        
        self.player1.graveyard = []
        self.player2.graveyard = []

    def test_apply_battle_attacker_wins(self):
        # Cenário: Atacante (P1) vence, Defensor (P2) é destruído e sofre 500 de dano.
        
        # Usando a nomenclatura do snippet de YGOengine.py:
        # 'dano_ao_oponente' -> Dano ao self.turnPlayer (Atacante)
        # 'dano_ao_local' -> Dano ao self.nonTurnPlayer (Defensor)
        # 'oponente_destruido' -> Monstro do Atacante (turnPlayer) destruído
        # 'local_destruido' -> Monstro do Defensor (nonTurnPlayer) destruído
        
        # (O teste anterior tinha 'dano_ao_local=1000', mas 2000 vs 1500 = 500 de dano)
        
        self.engine._apply_battle_results(
            dano_ao_oponente=0,      # Dano ao Atacante (P1)
            dano_ao_local=500,       # Dano ao Defensor (P2)
            local_destruido=True,   # Monstro Defensor (P2) destruído
            oponente_destruido=False, # Monstro Atacante (P1) não destruído
            monster_atacante=self.p1_monster,
            monster_defensor=self.p2_monster
        )
        
        # Verificações
        self.assertEqual(self.player1.life, 4000) # P1 não sofreu dano
        self.assertEqual(self.player2.life, 3500) # P2 sofreu 500 de dano
        self.assertIn(self.p2_monster, self.player2.graveyard)
        self.assertNotIn(self.p1_monster, self.player1.graveyard)

    def test_apply_battle_defender_wins(self):
        # Cenário: Defensor (P2) vence (ex: ATK 2500), Atacante (P1) é destruído e sofre 500 de dano.
        self.p2_monster.ATK = 2500 # Ajusta o ATK do defensor para este cenário
        
        self.engine._apply_battle_results(
            dano_ao_oponente=500,    # Dano ao Atacante (P1)
            dano_ao_local=0,        # Dano ao Defensor (P2)
            local_destruido=False,  # Monstro Defensor (P2) não destruído
            oponente_destruido=True,  # Monstro Atacante (P1) destruído
            monster_atacante=self.p1_monster,
            monster_defensor=self.p2_monster
        )
        
        # Verificações
        self.assertEqual(self.player1.life, 3500) # P1 sofreu 500 de dano
        self.assertEqual(self.player2.life, 4000) # P2 não sofreu dano
        self.assertNotIn(self.p2_monster, self.player2.graveyard)
        self.assertIn(self.p1_monster, self.player1.graveyard)

    def test_apply_battle_both_destroyed(self):
        # Cenário: Empate (ambos com 2000 ATK), ambos destruídos, sem dano.
        self.p2_monster.ATK = 2000 # Ajusta o ATK do defensor
        
        self.engine._apply_battle_results(
            dano_ao_oponente=0,
            dano_ao_local=0,
            local_destruido=True,
            oponente_destruido=True,
            monster_atacante=self.p1_monster,
            monster_defensor=self.p2_monster
        )
        
        # Verificações
        self.assertEqual(self.player1.life, 4000)
        self.assertEqual(self.player2.life, 4000)
        self.assertIn(self.p1_monster, self.player1.graveyard)
        self.assertIn(self.p2_monster, self.player2.graveyard)

if __name__ == '__main__':
    unittest.main()