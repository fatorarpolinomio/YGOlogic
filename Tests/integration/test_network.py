import unittest
import threading
import time
import socket

from Communication.network import Network

# Define uma porta de teste não padrão para evitar conflitos
TEST_PORT = 5556
TEST_HOST = "127.0.0.1"

class TestNetworkLoopback(unittest.TestCase):

    def setUp(self):
        self.host_net = Network()
        self.client_net = Network()
        
        self.host_event = threading.Event()
        self.server_started = False
        self.client_connected = False
        
        self.msg_from_host = {"tipo": "TEST_HOST", "data": "Olá Cliente"}
        self.msg_from_client = {"tipo": "TEST_CLIENT", "data": "Olá Host"}

    def tearDown(self):
        # Garante que todos os sockets sejam fechados
        self.client_net.close()
        self.host_net.close()
        # Aguarda as threads finalizarem
        time.sleep(0.1)

    def host_thread_task(self):
        try:
            # Tenta hospedar o jogo
            self.server_started = self.host_net.host_game(TEST_HOST, TEST_PORT)
            self.host_event.set() # Sinaliza que o host_game() terminou (sucesso ou falha)
        except Exception as e:
            print(f"[Host Thread] Erro: {e}")
            self.host_event.set() # Sinaliza mesmo em caso de erro

    def wait_for_message(self, net_obj: Network, timeout=2.0):
        """Helper para esperar por uma mensagem na fila da rede."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            msg = net_obj.get_message()
            if msg:
                return msg
            time.sleep(0.01) # Evita busy-waiting
        return None

    def test_host_client_message_exchange(self):
        # 1. Inicia a thread do Host
        host_thread = threading.Thread(target=self.host_thread_task, daemon=True)
        host_thread.start()
        
        # 2. Espera o host sinalizar que está pronto (ou falhou)
        self.assertTrue(self.host_event.wait(timeout=15), "Host thread demorou muito para iniciar")
        self.assertTrue(self.server_started, "Servidor (Host) falhou ao iniciar")
        
        # 3. Conecta o Cliente
        try:
            self.client_connected = self.client_net.connect_to_game(TEST_HOST, TEST_PORT)
        except Exception as e:
            self.fail(f"Cliente falhou ao conectar: {e}")
            
        self.assertTrue(self.client_connected, "Cliente falhou ao conectar")
        
        # 4. Envia mensagens
        self.host_net.send_message(self.msg_from_host)
        self.client_net.send_message(self.msg_from_client)
        
        # 5. Espera e verifica as mensagens recebidas
        received_by_client = self.wait_for_message(self.client_net)
        received_by_host = self.wait_for_message(self.host_net)
        
        # 6. Verifica
        self.assertIsNotNone(received_by_client, "Cliente não recebeu mensagem do host")
        self.assertIsNotNone(received_by_host, "Host não recebeu mensagem do cliente")
        
        self.assertDictEqual(received_by_client, self.msg_from_host)
        self.assertDictEqual(received_by_host, self.msg_from_client)

if __name__ == '__main__':
    unittest.main()