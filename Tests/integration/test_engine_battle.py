# Código deste teste foi realizado com auxílio do Gemini 2.5 Pro como dito no relatório

import unittest
from unittest.mock import Mock, MagicMock

# Importa as classes reais, já que YGOplayer e Monster são necessários
# para simular o estado real do jogo.
from Components.YGOplayer import Player
from Components.YGOengine import YGOengine
from Communication.network import Network
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import CardType

# (Assumindo que este arquivo está em uma pasta 'tests' no mesmo nível que 'Components')
# Se os imports falharem, você pode precisar ajustar o sys.path ou
# rodar com 'python -m unittest discover' da pasta raiz.


class TestEngineBattleResults(unittest.TestCase):
    """
    Testa o handler 'handle_opponent_battle_result'.
    
    Esta função é chamada no cliente que está DEFENDENDO,
    após o oponente (ATACANTE) ter calculado e enviado o resultado da batalha.
    """

    def setUp(self):
        """
        Configura o ambiente para testar a aplicação dos resultados da batalha.
        
        Perspectiva: Nós somos o P2 (Defensor / Local).
        - self.player1 é o 'turnPlayer' (Oponente / Atacante)
        - self.player2 é o 'nonTurnPlayer' (Local / Defensor)
        """
        
        # Usamos objetos Player reais para rastrear 'life', 'graveyard', etc.
        self.player1 = Player("P1-Atacante", 4000)
        self.player2 = Player("P2-Defensor", 4000)
        self.mock_network = Mock(spec=Network)
        
        self.engine = YGOengine(self.player1, self.player2, self.mock_network, is_host=True)
        
        # Garante que P1 é o atacante e P2 é o defensor
        # (Esta é a perspectiva do P2 ao receber o resultado)
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        
        # Instancia monstros reais (nome, ATK, tipo, efeito)
        self.p1_monster = Monster("Atacante", 2000, CardType.MONSTER, "")
        self.p2_monster = Monster("Defensor", 1500, CardType.MONSTER, "")
        
        # Reseta o estado 'canAttack' para o teste
        self.p1_monster.canAttack = True
        
        # Coloca os monstros em campo
        self.player1.monstersInField = [self.p1_monster]
        self.player2.monstersInField = [self.p2_monster]
        
        # CORREÇÃO: Define as contagens de monstros
        self.player1.monstersCount = 1
        self.player2.monstersCount = 1
        
        self.player1.graveyard = []
        self.player2.graveyard = []

        # "Espiona" (Mock) os métodos dos players reais para rastrear
        # se eles foram chamados corretamente.
        # Usamos side_effect para executar a função real E rastreá-la.
        self.player1.monsterIntoGraveyard = Mock(
            side_effect=self.player1.monsterIntoGraveyard
        )
        self.player2.monsterIntoGraveyard = Mock(
            side_effect=self.player2.monsterIntoGraveyard
        )


    def test_handle_battle_attacker_wins(self):
        """
        Testa o Cenário: Atacante (P1) vence.
        Defensor (P2) é destruído e sofre 500 de dano.
        """
        
        # O payload é o que a engine espera receber da rede
        payload = {
            "dano_atacante": 0,      # Dano ao Atacante (P1)
            "dano_defensor": 500,     # Dano ao Defensor (P2)
            "atacante_destruido": False,
            "defensor_destruido": True,
            "atacante_idx": 0, # Índice do monstro de P1
            "defensor_idx": 0  # Índice do monstro de P2
        }
        
        # Chama a função pública (handler)
        self.engine.handle_opponent_battle_result(payload)
        
        # Verificações
        self.assertEqual(self.player1.life, 4000) # P1 (Atacante) não sofreu dano
        self.assertEqual(self.player2.life, 3500) # P2 (Defensor) sofreu 500 de dano
        
        # Verifica se o monstro de P2 foi para o cemitério
        self.player2.monsterIntoGraveyard.assert_called_with(self.p2_monster)
        self.assertIn(self.p2_monster, self.player2.graveyard)
        self.assertNotIn(self.p2_monster, self.player2.monstersInField)
        self.assertEqual(self.player2.monstersCount, 0) # Verifica se o contador atualizou
        
        # Verifica se o monstro de P1 NÃO foi para o cemitério
        self.player1.monsterIntoGraveyard.assert_not_called()
        self.assertIn(self.p1_monster, self.player1.monstersInField)
        
        # Verifica se o monstro atacante (de P1) foi marcado como "não pode atacar mais"
        self.assertFalse(self.p1_monster.canAttack)

    def test_handle_battle_defender_wins(self):
        """
        Testa o Cenário: Defensor (P2) vence.
        Atacante (P1) é destruído e sofre 500 de dano.
        """
        # Ajusta o ATK do defensor para este cenário
        self.p2_monster.ATK = 2500 
        
        payload = {
            "dano_atacante": 500,    # Dano ao Atacante (P1)
            "dano_defensor": 0,      # Dano ao Defensor (P2)
            "atacante_destruido": True,
            "defensor_destruido": False,
            "atacante_idx": 0,
            "defensor_idx": 0
        }

        self.engine.handle_opponent_battle_result(payload)
        
        # Verificações
        self.assertEqual(self.player1.life, 3500) # P1 (Atacante) sofreu 500 de dano
        self.assertEqual(self.player2.life, 4000) # P2 (Defensor) não sofreu dano
        
        # Verifica se o monstro de P1 foi para o cemitério
        self.player1.monsterIntoGraveyard.assert_called_with(self.p1_monster)
        self.assertIn(self.p1_monster, self.player1.graveyard)
        self.assertNotIn(self.p1_monster, self.player1.monstersInField)
        self.assertEqual(self.player1.monstersCount, 0)
        
        # Verifica se o monstro de P2 NÃO foi para o cemitério
        self.player2.monsterIntoGraveyard.assert_not_called()
        self.assertIn(self.p2_monster, self.player2.monstersInField)

    def test_handle_battle_both_destroyed(self):
        """
        Testa o Cenário: Empate (ambos com 2000 ATK).
        Ambos destruídos, sem dano.
        """
        # Ajusta o ATK do defensor
        self.p2_monster.ATK = 2000 
        
        payload = {
            "dano_atacante": 0,
            "dano_defensor": 0,
            "atacante_destruido": True,
            "defensor_destruido": True,
            "atacante_idx": 0,
            "defensor_idx": 0
        }
        
        self.engine.handle_opponent_battle_result(payload)
        
        # Verificações
        self.assertEqual(self.player1.life, 4000)
        self.assertEqual(self.player2.life, 4000)
        
        # Verifica se ambos foram para o cemitério
        self.player1.monsterIntoGraveyard.assert_called_with(self.p1_monster)
        self.assertIn(self.p1_monster, self.player1.graveyard)
        self.assertEqual(self.player1.monstersCount, 0)
        
        self.player2.monsterIntoGraveyard.assert_called_with(self.p2_monster)
        self.assertIn(self.p2_monster, self.player2.graveyard)
        self.assertEqual(self.player2.monstersCount, 0)

if __name__ == '__main__':
    unittest.main()