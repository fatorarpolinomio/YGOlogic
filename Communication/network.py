import socket
import json
import threading
from queue import Queue, Empty
from typing import Dict, Any, Optional
from Communication.messages_protocol import MessageType   

class Network:
    def __init__(self):
        # criando o objeto socket principal: AF_INET para usar endereços IPv4 e SOCK_STREAM para usar o protocolo TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # variável que guardará a conexão específica com o outro jogador
        self.conn = None
        # flag para rastrear estado da conexão
        self.is_connected = False

        
        # fila thread-safe para armazenar mensagens recebidas
        # a thread de recebimento 'coloca' (put) mensagens aqui
        # a thread principal (jogo) 'obtém' (get) mensagens daqui
        self.message_queue: Queue[Dict[str, Any]] = Queue()
        
        # variável para armazenar a thread de recebimento
        self.receiver_thread: Optional[threading.Thread] = None

    def _start_receiver_thread(self):
        "Inicia a thread de recebimento em background."
        if self.receiver_thread is None:
            # daemon=True garante que a thread feche se o programa principal fechar
            self.receiver_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
            self.receiver_thread.start()

    def host_game(self, host, port):
        "Configura o jogador como anfitrião (servidor) e espera por uma conexão"
        try:
            # Associa o socket a um endereço IP e uma porta específicos
            self.socket.bind((host, port))
            # coloca o socket em modo de escuta, aguardando por 1 conexão na fila
            self.socket.listen(1)
            print("Esperando por um oponente...")
            # ´pausa o programa e espera uma conexão. Retorna um novo socket (conn) para a comunicação
            self.conn, addr = self.socket.accept()
            self.is_connected = True 
            print(f"Oponente {addr} se conectou.")
            # inicia a thread de recebimento
            self._start_receiver_thread()
            return True # true se a conexão foi bem sucedida
        except socket.error as e:
            print(f"Erro ao hospedar o jogo: {e}")
            return False #False se ocorreu um erro
    
    def connect_to_game(self, host, port):
        "Configura o jogador como convidado (cliente) e tenta se conectar ao anfitrião"
        try:
            # Tenta estabelecer uma conexão com o endereço e porta do servidor
            self.socket.connect((host, port))
            # Para o cliente, o socket principal é o mesmo da comunicação.
            self.conn = self.socket
            self.is_connected = True
            print("Conectado ao anfitrião!")
            self._start_receiver_thread()
            return True 
        except socket.error as e:
            print(f"Erro ao conectar: {e}")
            return False
        
    def listen_for_messages(self):
        """
        Função alvo da thread. Fica em loop recebendo mensagens.
        Este é o ÚNICO lugar que chama self.receive_message()
        """
        print("[Network Thread] Thread de recebimento iniciada.")
        while self.is_connected:
            try:
                # receive_message() é bloqueante, mas está em sua própria thread,
                # então não trava o loop principal do jogo.
                message = self.receive_message()
                
                if message:
                    # Adiciona a mensagem na fila para a thread principal processar
                    self.message_queue.put(message)
                else:
                    # receive_message() retorna None se a conexão for perdida
                    if self.is_connected:
                        print("[Network Thread] Conexão perdida. Encerrando.")
                        self.is_connected = False
                        # Envia uma mensagem de SAIR para o loop do jogo saber
                        self.message_queue.put({"tipo": MessageType.SAIR, "reason": "Connection lost"})
                    break # Sai do loop
            except Exception as e:
                if self.is_connected:
                    print(f"[Network Thread] Erro inesperado: {e}")
                    self.is_connected = False
                    self.message_queue.put({"tipo": MessageType.SAIR, "reason": "Network error"})
                break
        print("[Network Thread] Thread de recebimento finalizada.")

    # --- NOVO MÉTODO ---
    def get_message(self) -> Optional[Dict[str, Any]]:
        """
        Obtém uma mensagem da fila de forma NÃO-BLOQUEANTE.
        Este método deve ser chamado pelo loop principal do jogo.
        """
        try:
            # get_nowait() levanta uma exceção 'Empty' se a fila estiver vazia
            return self.message_queue.get_nowait()
        except Empty:
            # Isso é normal, significa que não há novas mensagens
            return None
             

    def send_message(self, message: Dict[str, Any]):
        "Envia uma mensagem estruturada pela rede e retorna False se a conexão falhar"
        # Verificação de estado
        if not self.is_connected or self.conn is None:
            print("Erro: Não há conexão ativa")
            return False
        
        if "tipo" not in message:
            print("Aviso: Mensagem sem campo 'tipo'")
            
        try:
            # Converte o dicionário Python para uma string no formato JSON
            # Codifica a string JSON para o formato de bytes (utf-8) )que é o que a rede transporta)
            message_json = json.dumps(message).encode('utf-8')
            message_length = len(message_json)
            # envia o tamanho da mensagem primeiro (4 bytes)
            self.conn.sendall(message_length.to_bytes(4, byteorder='big'))
            # Dps envia a mensagem
            self.conn.sendall(message_json)
            return True 
        except(socket.error, BrokenPipeError) as e:
            print(f"Erro de conexão ao enviar mensagem: {e}")
            return False 
        except (TypeError, ValueError) as e:
            print(f"Erro ao serializar mensagem: {e}")
            return False

    def receive_message(self, timeout: Optional[float] = None):
        "Recebe dados e retorna None se a conexão for perdida"
        # mesmo de send -> verificação de estado
        if not self.is_connected or self.conn is None:
            print("Erro: Não há conexão ativa")
            return None
        
        try:
            if timeout is not None:
                self.conn.settimeout(timeout)

            # recebe os bytes
            length_bytes = self.recv_exact(4)

            # verificação de desconexão
            if not length_bytes:
                return None
            # recebendo a mensagem completa
            message_length = int.from_bytes(length_bytes, byteorder='big')
            # verificação de tamanho inválido
            if message_length <= 0:
                print(f"Tamanho de mensagem inválido: {message_length}")
                return None
            # recebendo a msg completa
            message_bytes = self.recv_exact(message_length)
            if not message_bytes:
                return None
            
            # decodifica para string e depois para dicionário Python
            message_str = message_bytes.decode('utf-8')
            message = json.loads(message_str)

            return message
        
        except socket.timeout:
            print("Timeout ao aguardar mensagem.")
            return None
        except (socket.error, ConnectionResetError) as e:
            print(f"Erro de conexão ao receber: {e}")
            return None
        except json.JSONDecodeError:
            print("Erro ao decodificar a mensagem JSON. Pode ter sido corrompida ou incompleta.")
            return None
        except UnicodeDecodeError as e:
            print(f"Erro de codificação UTF-8: {e}")
            return None
        finally:
            if timeout is not None:
                self.conn.settimeout(None)

    def recv_exact(self, num_bytes: int):
        "recebe exatamente num_bytes bytes ou None se desconectou"
        data = b''
        while len(data) < num_bytes:
            try:
                chunk = self.conn.recv(num_bytes - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.error as e:
                # acontecerá se self.close() for chamado por outra thread
                return None
        return data
            
    def close(self):
        "fecha todas as conexões ativas de forma segura e a thread de recebimento"
        print("Fechando conexões...")
        if not self.is_connected:
            return
        self.is_connected = False
        # O anfitrião tem um 'conn' separado do 'socket' principal
        # convidado usa o 'socket' principal como 'conn', então a verificação é importante
        if self.conn and self.conn is not self.socket:
            try:
                # shutdown para nao permitir mais send/receive
                self.conn.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass # ignora erros se já estiver fechado
                self.conn.close()
                print("Conexão fechada")
            except socket.error as e:
                print(f"Erro ao fechar a conexão: {e}")
        
        # fecha o socket principal
        try:
            if self.socket.fileno() != -1:
                self.socket.shutdown(socket.SHUT_RDWR)
        except (socket.error, OSError):
            pass  # Ignora erro se não estiver conectado
        try:
            self.socket.close()
            print("Socket principal fechado.")
        except socket.error as e:
            print(f"Erro ao fechar o socket principal: {e}")
        
        # aguarda a thread de recebimento finalizar
        if self.receiver_thread and self.receiver_thread.is_alive():
            print("Aguardando thread de recebimento finalizar...")
            self.receiver_thread.join(timeout=3.0) # espera no máximo 3s
            if self.receiver_thread.is_alive():
                print("Aviso: Thread de recebimento não finalizou a tempo.")
            else:
                print("Thread de recebimento finalizada com sucesso.")
        
        self.receiver_thread = None
        self.conn = None