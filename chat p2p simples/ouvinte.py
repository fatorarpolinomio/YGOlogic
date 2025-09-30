import socket

# Cria o objeto do socket
# AF_INET -> diz que estamos usando endereços IP (o "prédio")
# SOCK_STREAM -> diz que estamos usando o protocolo TCP, que é confiável
ouvinte_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Socket 'ouvinte' criado.")

# Define o endereço e a porta
HOST = '127.0.0.1'  # Endereço IP para escutar
PORTA = 65432      # Porta para escutar

# vincula o socket ao endereço e porta
ouvinte_socket.bind((HOST, PORTA))
print(f"Socket vinculado ao endereço {HOST} na porta {PORTA}.")

# coloca o socket em modo de escuta
ouvinte_socket.listen()
print(f"Ouvinte pronto e escutando na porta {PORTA}...")

# Aceita a conexão quando ela chegar
# O programa vai pausar aqui até alguém se conectar
conn, addr = ouvinte_socket.accept()

print(f"Conectado por {addr}")

while True:
    # recebe a mensagem do cliente
    dados_cliente = conn.recv(1024).decode('utf-8')
    if not dados_cliente or dados_cliente == 'sair':
        break
    print(f"Cliente: {dados_cliente}")

    # envia uma resposta para o cliente
    resposta = input("Sua vez: ")
    conn.sendall(resposta.encode('utf-8'))
    if resposta == 'sair':
        break

# fecha a conexão após a conversa
conn.close()
print("Conexão com o cliente fechada.")
