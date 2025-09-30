from pickle import NONE
import YGOlogic as ygo

def setup_game(net, is_host):
    """
    Prepara o jogo, cria os jogadores e troca as informações iniciais.
    Retorna os objetos (player, opponent) prontos para o jogo
    """
    if is_host:
        player_name = input("Digite seu nome: ")
        # é o anfitrião cria os dois decks e os dois jogadores
        deck1 = ygo.create_standard_deck()
        deck2 = ygo.create_standard_deck()
        
        player = ygo.Player(player_name, 4000, deck1)
        player.shuffleDeck()
        player.initialHand()
        
        # espera o nome do oponente para poder criar o objeto dele
        opponent_name_data = net.receive_message()
        opponent_name = opponent_name_data['name']
        net.send_message({'name': player.name})

        opponent = ygo.Player(opponent_name, 4000, deck2)
        opponent.shuffleDeck()
        opponent.initialHand()
        
        print(f"Você ({player.name}) vs {opponent.name}")
        print(f"Sua mão inicial (Anfitrião): {player.hand}")
        
        # enviando a mão inicial para o oponente
        print("Enviando mão inicial para o oponente...")
        mao_oponente_em_dict = [card.to_dict() for card in opponent.hand]
        
        setup_message = {
            "tipo": "SETUP_JOGO",
            "sua_mao": mao_oponente_em_dict
        }
        net.send_message(setup_message)
        
    else: # Se for o convidado
        player_name = input("Digite seu nome: ")
        net.send_message({'name': player_name})
        opponent_name_data = net.receive_message()
        opponent_name = opponent_name_data['name']

        # cria os objetos de jogador com mãos e decks vazios por enquanto
        player = ygo.Player(player_name, 4000, [])
        opponent = ygo.Player(opponent_name, 4000, [])
        
        print(f"Você ({player.name}) vs {opponent.name}")
        
        # recebe e processa a mão inicial do anfitrião
        print("Aguardando o anfitrião enviar sua mão inicial...")
        setup_data = net.receive_message()

        if setup_data and setup_data.get("tipo") == "SETUP_JOGO":
            mao_recebida_em_dict = setup_data['sua_mao']
            
            # Limpa a mão (caso já tenha algo) e a preenche com as cartas recebidas
            player.hand = [] 
            for carta_dict in mao_recebida_em_dict:
                # recria o objeto Card a partir do dicionário recebido via JSON
                nova_carta = ygo.Card(
                    name=carta_dict['name'],
                    ATK=carta_dict['ATK'],
                    DEF=carta_dict['DEF'],
                    # converte a string de volta para o tipo Enum correto
                    type=ygo.CardType[carta_dict['type']], 
                    effect=carta_dict['effect']
                )
                player.hand.append(nova_carta)
                
            print(f"Mão recebida! Sua mão (Convidado): {player.hand}")
        else:
            print("Erro ao receber dados de setup do anfitrião.")
            return None, None # retorna None para indicar que o setup falhou

    return player, opponent


def run_game_loop(net, is_host, player, opponent):
    """ Executa o loop de turnos do jogo. """
    my_turn = is_host
    game_over = False
    
    # loop continua enquanto o jogo não acabar
    while not game_over:
        if my_turn:
            print("\n" + "="*10 + " SEU TURNO " + "="*10)
            print(f"Sua Vida: {player.life} | Vida do Oponente: {opponent.life}")
            
            while True: 
                # opções de ação do jogador (simplificado, ainda precisa adicionar +) ***
                action = input("Escolha uma ação: (1) Ver Mão, (2) Passar o Turno, (3) Sair do Jogo\n> ")
                
                if action == '1':
                    print("Sua mão:", player.hand)
                
                elif action == '2':
                    print("Você passou o turno.")
                    # Envia a mensagem e verifica se o envio foi bem-sucedido
                    if not net.send_message({"tipo": "MUDAR_TURNO"}):
                        game_over = True # se falhou, encerra o jogo
                    my_turn = False
                    break 
                
                elif action == '3':
                    print("Você saiu do jogo.")
                    net.send_message({"tipo": "SAIR"}) # notifica o oponente
                    game_over = True # define a flag para encerrar o jogo localmente
                    break 

                else:
                    print("Ação inválida.")
        
        else: # Vez do oponente
            print("\n" + "="*10 + " TURNO DO OPONENTE " + "="*10)
            print("Aguardando jogada do oponente...")
            data = net.receive_message()
            
            if data is None:
                print("O oponente se desconectou. Fim de jogo.")
                game_over = True
                continue 

            # analisa a mensagem recebida do oponente
            message_type = data.get("tipo")

            if message_type == "MUDAR_TURNO":
                print("O oponente passou o turno. Agora é a sua vez!")
                my_turn = True
            
            elif message_type == "SAIR":
                print("O oponente saiu do jogo.")
                game_over = True 

        # condição de vitória/derrota por pontos de vida
        if player.life <= 0 or opponent.life <= 0:
            game_over = True

    # Lógica de Fim de Jogo 
    print("\n--- FIM DE JOGO ---")
    if player.life <= 0:
        print("Você perdeu!")
    elif opponent.life <= 0:
        print("Você venceu!")
    else:
        # se ninguém perdeu por pontos de vida, o jogo terminou por desconexão ou desistência
        print("A partida foi encerrada.")


def main():
    """ gerencia o menu inicial e a conexão"""
    print("Bem-vindo ao Yu-Gi-Oh! P2P")
    
    net = Network() # cria o objeto de rede 

    try:
        connection_established = False

        while True:
            choice = input("Você quer (1) Hospedar um jogo ou (2) Conectar-se a um jogo? ")
            if choice in ['1', '2']:
                break
            else:
                print("Escolha inválida. Por favor, digite 1 ou 2.")

        if choice == '1':
            connection_established = net.host_game('0.0.0.0', 5555)
            is_host = True
        else: # choice == '2'
            host_ip = input("Digite o endereço IP do anfitrião: ")
            connection_established = net.connect_to_game(host_ip, 5555)
            is_host = False

        if connection_established:
            player, opponent = setup_game(net, is_host)
            
            if player and opponent:
                run_game_loop(net, is_host, player, opponent)
        else:
            print("\nNão foi possível estabelecer a conexão.")

    finally:
        print("\nEncerrando a aplicação.")
        net.close()

# só pra main() ser executada quando o arq. é executado como programa principal
if __name__ == "__main__":
    main()
