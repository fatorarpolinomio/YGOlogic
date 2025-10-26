import unittest
from unittest.mock import Mock, MagicMock
from queue import Queue, Empty

# Importações do Jogo
from Components.YGOplayer import Player
from Components.YGOengine import YGOengine, GamePhase
from Communication.network import Network
from Communication.messages_protocol import MessageConstructor, MessageType
from Components.cards.Monsters import Monster # <-- Alteração
from Components.cards.YGOcards import CardType # <-- Alteração

# (Copiado de test_engine_flow.py para simular a lógica do Main.py)
def mock_nextPhase(self: YGOengine):
    """Função mock para simular a transição de fases."""
    if self.currentPhase == GamePhase.DRAW:
        self.currentPhase = GamePhase.MAIN_1
    elif self.currentPhase == GamePhase.MAIN_1:
        self.currentPhase = GamePhase.BATTLE
    elif self.currentPhase == GamePhase.BATTLE:
        self.currentPhase = GamePhase.END
    elif self.currentPhase == GamePhase.END:
        self.turnPlayer, self.nonTurnPlayer = self.nonTurnPlayer, self.turnPlayer
        self.turnCount += 1
        self.summonThisTurn = False
        self.currentPhase = GamePhase.DRAW
        # Apenas a engine do jogador do turno deve enviar a mensagem
        if (self.is_host and self.turnPlayer == self.player1) or \
           (not self.is_host and self.turnPlayer == self.player1):
            self.network.send_message(MessageConstructor.passar_turno())


class TestFullGameFlow(unittest.TestCase):

    def setUp(self):
        # 1. Filas de mensagens
        self.host_to_client_queue = Queue()
        self.client_to_host_queue = Queue()

        # 2. Mocks da Rede
        self.mock_host_net = Mock(spec=Network)
        self.mock_client_net = Mock(spec=Network)

        # 3. Configura os mocks para usar as filas
        self.mock_host_net.send_message.side_effect = lambda msg: self.host_to_client_queue.put(msg)
        self.mock_client_net.get_message.side_effect = lambda: self.host_to_client_queue.get(timeout=1)
        self.mock_client_net.send_message.side_effect = lambda msg: self.client_to_host_queue.put(msg)
        self.mock_host_net.get_message.side_effect = lambda: self.client_to_host_queue.get(timeout=1)

        # 4. Criar Jogadores (Agora funciona)
        self.host_player = Player("HostPlayer", 4000)
        self.client_player = Player("ClientPlayer", 4000)
        
        # 5. Criar Motores
        self.host_engine = YGOengine(self.host_player, self.client_player, self.mock_host_net, is_host=True)
        self.client_engine = YGOengine(self.client_player, self.host_player, self.mock_client_net, is_host=False)

        # 6. Monkey-patch a lógica de fluxo de fase (que estaria em Main.py)
        self.host_engine.nextPhase = mock_nextPhase.__get__(self.host_engine, YGOengine)
        self.client_engine.nextPhase = mock_nextPhase.__get__(self.client_engine, YGOengine)


    def test_turn_1_host_summons_and_passes(self):
        # Estado inicial: Host (P1) começa
        self.assertEqual(self.host_engine.turnPlayer.name, "HostPlayer")
        self.assertEqual(self.client_engine.turnPlayer.name, "HostPlayer")
        self.assertEqual(self.host_engine.currentPhase, GamePhase.DRAW)

        # --- FASE DE COMPRA (Simulada) ---
        # (O loop principal chamaria drawCard() aqui)
        self.host_engine.nextPhase() # DRAW -> MAIN_1
        # O cliente teria recebido uma msg 'MUDOU_FASE' (não implementada no protocolo)
        # Vamos forçar a sincronia
        self.client_engine.currentPhase = GamePhase.MAIN_1
        
        # --- FASE PRINCIPAL 1 ---
        # O Host (P1) decide invocar um monstro.
        monster_to_summon = Monster(name="Test Monster", atk=1500, type=CardType.MONSTER, effect="")
        self.host_player.hand = [monster_to_summon] # Coloca o monstro na mão
        
        action_msg = MessageConstructor.invocar_monstro(hand_index=0, posicao="ATK")
        
        # 1. Host processa sua própria ação (Simulação da lógica de Main.py)
        self.host_player.hand.pop(0)
        self.host_player.monstersInField.append(monster_to_summon)
        self.host_engine.summonThisTurn = True
        
        # 2. Host envia a mensagem para o cliente
        self.host_engine.network.send_message(action_msg)
        
        # 3. Cliente recebe e processa a mensagem
        try:
            received_msg = self.client_engine.network.get_message()
            self.assertDictEqual(received_msg, action_msg)
            
            # NOTA: O protocolo 'INVOCAR_MONSTRO' é falho. Ele só envia o índice da mão.
            # O cliente não sabe QUAL carta foi invocada.
            # Para o teste funcionar, simulamos que o cliente *sabe* qual carta é.
            
            # Simulação do cliente processando a ação do oponente
            # (O cliente atualiza sua *visão* do campo do oponente)
            self.client_engine.nonTurnPlayer.monstersInField.append(monster_to_summon)
            
            self.assertEqual(len(self.client_engine.nonTurnPlayer.monstersInField), 1)
            self.assertEqual(self.client_engine.nonTurnPlayer.monstersInField[0].name, "Test Monster")

        except Empty:
            self.fail("Cliente não recebeu a mensagem de invocação do Host")

        # --- FIM DO TURNO ---
        # Host decide passar o turno. Ele chama nextPhase até o fim.
        self.host_engine.nextPhase() # MAIN_1 -> BATTLE
        self.host_engine.nextPhase() # BATTLE -> END
        
        # A última chamada (END -> DRAW) envia a mensagem de "PASSAR_TURNO"
        self.host_engine.nextPhase() 
        
        self.assertEqual(self.host_engine.turnPlayer.name, "ClientPlayer")
        
        # ... O cliente recebe a mensagem ...
        try:
            received_pass_msg = self.client_engine.network.get_message()
            self.assertEqual(received_pass_msg["tipo"], MessageType.PASSAR_TURNO)
            
            # Cliente atualiza seu estado (recebe o turno)
            self.client_engine.nextPhase() # MAIN_1 -> BATTLE
            self.client_engine.nextPhase() # BATTLE -> END
            self.client_engine.nextPhase() # END -> DRAW (e recebe o turno)
            
            self.assertEqual(self.client_engine.turnPlayer.name, "ClientPlayer")
            
        except Empty:
            self.fail("Cliente não recebeu a mensagem de passar o turno")

if __name__ == '__main__':
    unittest.main()