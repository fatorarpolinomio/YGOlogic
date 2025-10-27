# Código deste teste foi realizado com auxílio do Gemini 2.5 Pro como dito no relatório

import unittest
import threading
import time
import socket

# (Assumindo que este arquivo está em 'tests/' e 'Communication/' está no mesmo nível do 'tests/' ou acima)
from Communication.network import Network

# Define uma porta de teste não padrão para evitar conflitos
TEST_PORT = 5556
TEST_HOST = "127.0.0.1"

class TestNetworkLoopback(unittest.TestCase):

    def setUp(self):
        self.host_net = Network()
        self.client_net = Network()
        
        # Evento para sinalizar que o host está pronto (ou falhou)
        self.host_event = threading.Event()
        self.host_exception = None 
        self.server_started = False
        
        self.msg_from_host = {"tipo": "TEST_HOST", "data": "Olá Cliente"}
        self.msg_from_client = {"tipo": "TEST_CLIENT", "data": "Olá Host"}

    def tearDown(self):
        # Garante que todos os sockets sejam fechados
        self.client_net.close()
        self.host_net.close()
        time.sleep(0.2) # Dá um tempo para o SO liberar a porta

    def host_thread_task(self):
        """ Thread para rodar a função bloqueante host_game() """
        try:
            # Tenta hospedar o jogo
            self.server_started = self.host_net.host_game(TEST_HOST, TEST_PORT)
        except Exception as e:
            print(f"[Host Thread] Erro: {e}")
            self.host_exception = e 
        finally:
            self.host_event.set() # Sinaliza que o host_game() terminou (sucesso ou falha)

    def wait_for_message(self, net_obj: Network, timeout=5) -> dict | None:
        """ Helper para aguardar uma mensagem na fila. """
        end_time = time.time() + timeout
        while time.time() < end_time:
            msg = net_obj.get_message()
            if msg:
                return msg
            time.sleep(0.1)  # Aguarda 100ms antes de tentar novamente
        return None

    def _establish_connection(self) -> bool:
        """
        Helper para conectar o host e o cliente.
        CORRIGIDO: Lógica alterada para evitar deadlock.
        """
        host_thread = threading.Thread(target=self.host_thread_task, daemon=True)
        host_thread.start()
        
        # Dá um tempo mínimo para a thread do host iniciar
        # e chegar na chamada bloqueante 'accept()'
        time.sleep(0.1)
        
        # 2. Conecta o Cliente
        # Esta ação irá *desbloquear* a thread do host que está em 'accept()'
        try:
            client_connected = self.client_net.connect_to_game(TEST_HOST, TEST_PORT)
            if not client_connected:
                self.fail("Cliente falhou ao conectar (método retornou False)")
        except Exception as e:
            self.fail(f"Cliente falhou ao conectar com exceção: {e}")
        
        # 3. AGORA esperamos pelo evento.
        # Ele deve ser disparado logo, já que o cliente conectou.
        if not self.host_event.wait(timeout=5):
            self.fail("Host thread não sinalizou 'set()' após a conexão do cliente")
            
        # 4. Verifica se o host teve algum problema
        if self.host_exception:
            self.fail(f"Host falhou ao iniciar: {self.host_exception}")
        if not self.server_started:
            self.fail("Servidor (Host) não iniciou e não reportou exceção.")
            
        return True # Sucesso

    # --- Testes ---

    def test_full_connection_and_messaging(self):
        """ Testa o 'caminho feliz': conectar, enviar e receber mensagens de ambos os lados. """
        if not self._establish_connection():
            return # Falha já foi reportada no helper

        # Envia mensagens
        self.host_net.send_message(self.msg_from_host)
        self.client_net.send_message(self.msg_from_client)
        
        # Espera e verifica as mensagens recebidas
        received_by_client = self.wait_for_message(self.client_net)
        received_by_host = self.wait_for_message(self.host_net)
        
        # Verifica
        self.assertEqual(received_by_client, self.msg_from_host, "Cliente recebeu mensagem errada")
        self.assertEqual(received_by_host, self.msg_from_client, "Host recebeu mensagem errada")

    def test_multiple_messages_framing(self):
        """ 
        NOVO: Testa se duas mensagens enviadas rapidamente são recebidas
        como duas mensagens distintas (testa o 'framing' com '\n').
        """
        if not self._establish_connection():
            return

        msg_host_1 = {"id": 1, "txt": "Primeira"}
        msg_host_2 = {"id": 2, "txt": "Segunda"}

        # Envia duas mensagens em rápida sucessão
        self.host_net.send_message(msg_host_1)
        self.host_net.send_message(msg_host_2)

        # Verifica se o cliente recebe duas mensagens distintas
        received_1 = self.wait_for_message(self.client_net, timeout=2)
        received_2 = self.wait_for_message(self.client_net, timeout=2)

        self.assertIsNotNone(received_1, "Não recebeu a primeira mensagem")
        self.assertIsNotNone(received_2, "Não recebeu a segunda mensagem")
        self.assertEqual(received_1, msg_host_1)
        self.assertEqual(received_2, msg_host_2)

    def test_disconnect_from_client(self):
        """
        NOVO: Testa se o Host detecta quando o Cliente se desconecta.
        """
        if not self._establish_connection():
            return
            
        # Cliente encerra a conexão
        self.client_net.close()
        
        # Verifica se o 'is_connected' do cliente é atualizado
        self.assertFalse(self.client_net.is_connected)

        # Aguarda o host detectar a desconexão
        # (A thread 'listen_for_messages' do host deve parar)
        end_time = time.time() + 5
        while self.host_net.is_connected and time.time() < end_time:
            time.sleep(0.1)
            
        self.assertFalse(self.host_net.is_connected, "Host não detectou a desconexão do cliente")
        
        # Verifica se a thread do host realmente parou
        self.host_net.receiver_thread.join(timeout=1.0)
        self.assertFalse(self.host_net.receiver_thread.is_alive(), "Thread de recebimento do Host não foi finalizada")

    def test_disconnect_from_host(self):
        """
        NOVO: Testa se o Cliente detecta quando o Host se desconecta.
        """
        if not self._establish_connection():
            return

        # Host encerra a conexão
        self.host_net.close()
        self.assertFalse(self.host_net.is_connected)

        # Aguarda o cliente detectar a desconexão
        end_time = time.time() + 5
        while self.client_net.is_connected and time.time() < end_time:
            time.sleep(0.1)
            
        self.assertFalse(self.client_net.is_connected, "Cliente não detectou a desconexão do host")

        # Verifica se a thread do cliente realmente parou
        self.client_net.receiver_thread.join(timeout=1.0)
        self.assertFalse(self.client_net.receiver_thread.is_alive(), "Thread de recebimento do Cliente não foi finalizada")

if __name__ == '__main__':
    unittest.main()