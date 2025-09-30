import socket

HOST = '127.0.0.1'  # endereço do servidor que queremos nos conectar
PORTA = 65432      # A mesma porta que o "ouvinte" está usando

# Cria o socket do "iniciador"
iniciador_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Tenta se conectar ao endereço e porta do "ouvinte"
iniciador_socket.connect((HOST, PORTA))

print(f"Conectado com sucesso ao ouvinte em {HOST}:{PORTA}")

print("Conectado ao servidor. Digite 'sair' para terminar.")

while True:
    # envia uma mensagem para o servidor
    mensagem = input("Sua vez: ")
    # transforma a string em uma sequência de bytes
    iniciador_socket.sendall(mensagem.encode('utf-8'))
    if mensagem == 'sair':
        break

    # recebe a resposta do servidor
    dados_servidor = iniciador_socket.recv(1024).decode('utf-8')  # traduz os bytes recebidos em uma string
    if not dados_servidor or dados_servidor == 'sair':
        break
    print(f"Servidor: {dados_servidor}")

# Fecha a conexão
iniciador_socket.close()
print("Conexão com o servidor fechada.")


