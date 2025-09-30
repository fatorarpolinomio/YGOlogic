import socket
import json

class Network:
    def __init__(self):
        # criando o objeto socket principal: AF_INET para usar endereços IPv4 e SOCK_STREAM para usar o protocolo TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # variável que guardará a conexão específica com o outro jogador
        self.conn = None

    def host_game(self, host, port):
        """Configura o jogador como anfitrião (servidor) e espera por uma conexão"""
        try:
            # Associa o socket a um endereço IP e uma porta específicos
            self.socket.bind((host, port))
            # coloca o socket em modo de escuta, aguardando por 1 conexão na fila
            self.socket.listen(1)
            print("Esperando por um oponente...")
            # ´pausa o programa e espera uma conexão. Retorna um novo socket (conn) para a comunicação
            self.conn, addr = self.socket.accept()
            print(f"Oponente {addr} se conectou.")
            return True # Retorna True se a conexão foi bem-sucedida
        except socket.error as e:
            print(f"Erro ao hospedar o jogo: {e}")
            return False #False se ocorreu um erro

    def connect_to_game(self, host, port):
        """Configura o jogador como convidado (cliente) e tenta se conectar ao anfitrião"""
        try:
            # Tenta estabelecer uma conexão com o endereço e porta do servidor
            self.socket.connect((host, port))
            # Para o cliente, o socket principal é o mesmo da comunicação.
            self.conn = self.socket
            print("Conectado ao anfitrião.")
            return True 
        except socket.error as e:
            print(f"Erro ao conectar: {e}")
            return False 

    def send_message(self, data):
        """Envia um dicionário de dados pela rede e retorna False se a conexão falhar"""
        try:
            # Converte o dicionário Python para uma string no formato JSON
            # Codifica a string JSON para o formato de bytes (utf-8), que é o que a rede transporta
            message = json.dumps(data).encode('utf-8')
            # envia todos os bytes da mensagem pela conexão estabelecida.
            self.conn.sendall(message)
            return True 
        except (socket.error, BrokenPipeError) as e:
            print(f"Erro de conexão ao enviar: {e}")
            return False # Retorna False se ocorreu um erro.

    def receive_message(self):
        """Recebe dados e retorna None se a conexão for perdida"""
        try:
            # Recebe os bytes
            message_bytes = self.conn.recv(2048)

            # verificação de desconexão
            if not message_bytes:
                return None
            
            # decodifica para string e depois para dicionário Python
            message_str = message_bytes.decode('utf-8')
            return json.loads(message_str)

        except (socket.error, ConnectionResetError) as e:
            # ConnectionResetError é comum quando a conexão é forçada
            print(f"Erro de conexão ao receber: {e}")
            return None
        except json.JSONDecodeError:
            print("Erro ao decodificar a mensagem JSON. Pode ter sido corrompida ou incompleta.")
            return None
        
    def close(self):
        """fecha todas as conexões ativas de forma segura"""
        print("Fechando conexões...")
        # O anfitrião tem um 'conn' separado do 'socket' principal
        # convidado usa o 'socket' principal como 'conn', então a verificação é importante
        if self.conn and self.conn is not self.socket:
            try:
                self.conn.close()
            except socket.error as e:
                print(f"Erro ao fechar a conexão do cliente (conn): {e}")
        
        # fecha o socket principal (de escuta para o host, de conexão para o cliente)
        try:
            self.socket.close()
        except socket.error as e:
            print(f"Erro ao fechar o socket principal: {e}")