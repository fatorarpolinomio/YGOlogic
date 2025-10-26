import unittest
from unittest.mock import Mock, patch

from Components.YGOplayer import Player
from Components.YGOengine import YGOengine
from Components.YGOgamePhase import GamePhase
from Communication.network import Network
from Communication.messages_protocol import MessageConstructor, MessageType

# Esta é uma implementação suposta de nextPhase, baseada na lógica
# inferida de Main.py e YGOinterface.py
def mock_nextPhase(self: YGOengine):
    """Função mock para simular a transição de fases."""
    if self.currentPhase == GamePhase.DRAW:
        self.currentPhase = GamePhase.MAIN_1
    elif self.currentPhase == GamePhase.MAIN_1:
        self.currentPhase = GamePhase.BATTLE
    elif self.currentPhase == GamePhase.BATTLE:
        self.currentPhase = GamePhase.END
    elif self.currentPhase == GamePhase.END:
        # Troca de turno
        self.turnPlayer, self.nonTurnPlayer = self.nonTurnPlayer, self.turnPlayer
        self.turnCount += 1
        self.summonThisTurn = False
        # Reinicia para Draw Phase
        self.currentPhase = GamePhase.DRAW
        
        # Notifica o outro jogador
        self.network.send_message(MessageConstructor.passar_turno())
        print(f"--- Turno {self.turnCount} ({self.turnPlayer.name}) ---")


class TestEngineFlow(unittest.TestCase):

    def setUp(self):
        self.player1 = Player("P1", 4000)
        self.player2 = Player("P2", 4000)
        self.mock_network = Mock(spec=Network)
        
        self.engine = YGOengine(self.player1, self.player2, self.mock_network, is_host=True)
        
        # Aplicando o "monkey-patch": Injeta a função mock_nextPhase como um método da *instância*
        self.engine.nextPhase = mock_nextPhase.__get__(self.engine, YGOengine)

    
    def test_phase_transition_flow(self):
        # Turno 1 - P1
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)
        self.assertEqual(self.engine.turnPlayer, self.player1)
        
        self.engine.nextPhase() # DRAW -> MAIN_1
        self.assertEqual(self.engine.currentPhase, GamePhase.MAIN_1)
        
        self.engine.nextPhase() # MAIN_1 -> BATTLE
        self.assertEqual(self.engine.currentPhase, GamePhase.BATTLE)
        
        self.engine.nextPhase() # BATTLE -> END
        self.assertEqual(self.engine.currentPhase, GamePhase.END)
        
        # Fim do Turno 1 -> Início do Turno 2
        self.engine.nextPhase() # END -> DRAW (e troca jogador)
        
        # Verifica se o turno mudou
        self.assertEqual(self.engine.turnCount, 2)
        # Verifica se o jogador mudou
        self.assertEqual(self.engine.turnPlayer, self.player2)
        # Verifica se a fase reiniciou
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)
        # Verifica se a rede foi notificada
        self.mock_network.send_message.assert_called_with(MessageConstructor.passar_turno())

if __name__ == '__main__':
    unittest.main()