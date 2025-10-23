from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from Components.YGOengine import YGOengine, GamePhase
    from Components.YGOinterface import YGOinterface
    from Components.YGOplayer import Player
    from Components.cards.YGOcards import Card
    from Components.cards.YGOcards import CardType

from Communication.network import Network


def main():
    """gerencia o menu inicial e a conexão"""
    print("Bem-vindo ao Yu-Gi-Oh! P2P")

    net = Network()  # cria o objeto de rede

    try:
        connection_established = False

        while True:
            choice = input(
                "Você quer (1) Hospedar um jogo ou (2) Conectar-se a um jogo? "
            )
            if choice in ["1", "2"]:
                break
            else:
                print("Escolha inválida. Por favor, digite 1 ou 2.")

        if choice == "1":
            connection_established = net.host_game("0.0.0.0", 5555)
            is_host = True
        else:  # choice == '2'
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


def setup_game(net, is_host):
    """
    Prepara o jogo, cria os jogadores e troca as informações iniciais.
    Retorna os objetos (player, opponent) prontos para o jogo
    """
    if is_host:
        player_name = input("Digite seu nome: ")

        player = Player(player_name, 4000)
        player.shuffleDeck()
        player.initialHand()

        # espera o nome do oponente para poder criar o objeto dele
        opponent_name_data = net.receive_message()
        opponent_name = opponent_name_data["name"]
        net.send_message({"name": player.name})

        opponent = Player(opponent_name, 4000)
        opponent.shuffleDeck()
        opponent.initialHand()

        print(f"Você ({player.name}) vs {opponent.name}")
        print(f"Sua mão inicial (Anfitrião): {player.hand}")

        # enviando a mão inicial para o oponente
        print("Enviando mão inicial para o oponente...")
        mao_oponente_em_dict = [card.to_dict() for card in opponent.hand]

        setup_message = {"tipo": "SETUP_JOGO", "sua_mao": mao_oponente_em_dict}
        net.send_message(setup_message)

    else:  # Se for o convidado
        player_name = input("Digite seu nome: ")
        net.send_message({"name": player_name})
        opponent_name_data = net.receive_message()
        opponent_name = opponent_name_data["name"]

        # cria os objetos de jogador com mãos e decks vazios por enquanto
        player = Player(player_name, 4000)
        opponent = Player(opponent_name, 4000)

        print(f"Você ({player.name}) vs {opponent.name}")

        # recebe e processa a mão inicial do anfitrião
        print("Aguardando o anfitrião enviar sua mão inicial...")
        setup_data = net.receive_message()

        if setup_data and setup_data.get("tipo") == "SETUP_JOGO":
            mao_recebida_em_dict = setup_data["sua_mao"]

            # Limpa a mão (caso já tenha algo) e a preenche com as cartas recebidas
            player.hand = []
            for carta_dict in mao_recebida_em_dict:
                # recria o objeto Card a partir do dicionário recebido via JSON
                nova_carta = Card(
                    name=carta_dict["name"],
                    ATK=carta_dict["ATK"],
                    DEF=carta_dict["DEF"],
                    # converte a string de volta para o tipo Enum correto
                    type=CardType[carta_dict["type"]],
                    effect=carta_dict["effect"],
                )
                player.hand.append(nova_carta)

            print(f"Mão recebida! Sua mão (Convidado): {player.hand}")
        else:
            print("Erro ao receber dados de setup do anfitrião.")
            return None, None  # retorna None para indicar que o setup falhou

    return player, opponent


def run_game_loop(net, is_host, player, opponent):
    """Executa o loop de turnos do jogo."""
    my_turn = is_host
    game_over = False

    # Inicializando as duas classes principais:
    engine = YGOengine(player, opponent, net, is_host)
    interface = YGOinterface()

    # loop continua enquanto o jogo não acabar
    while not game_over:
        currentPlayer = engine.turnPlayer
        currentPhase = engine.currentPhase

        interface.displayPhase(currentPhase.name, currentPlayer.name, engine.turnCount)
        print(
            f"Sua Vida: {engine.turnPlayer.life} | Vida do Oponente: {engine.nonTurnPlayer.life}"
        )

        if currentPhase == GamePhase.DRAW:
            # print da fase de compra na interface
            # drawCard na engine
            engine.advanceToNextPhase()
            continue

        actionString = None
        if currentPhase == GamePhase.MAIN_1:
            actionString = interface.promptMainPhaseActions(currentPlayer.name)
        elif currentPhase == GamePhase.BATTLE:
            actionString = interface.promptBattlePhaseActions(currentPlayer.name)
        elif currentPhase == GamePhase.END:
            engine.endTurn()
            continue

        if actionString in ["GO_TO_BATTLE_FASE", "END_TURN"]:
            result = engine.processPlayerAction(actionString)
        elif actionString == "VIEW_FIELD":
            interface.viewField(engine.turnPlayer, engine.nonTurnPlayer)
        elif actionString == "VIEW_GRAVEYARD":
            interface.viewGraveyard(engine.turnPlayer)
        elif actionString == "VIEW_HAND":
            commandDict = interface.viewHand(engine.turnPlayer, engine.summonThisTurn)
            if commandDict:
                # O usuário selecionou uma carta e uma ação (ex: SUMMON)
                # Agora, passamos esse comando para o engine processar
                result = engine.processPlayerAction(commandDict["action"], commandDict)

                # O engine retorna se foi sucesso ou não
                if not result["success"]:
                    # interface.displayError(result["reason"])
                    print(f"Ação falhou: {result['reason']}")
                else:
                    # interface.displaySuccess(f"{command_dict['action']} bem-sucedido!")
                    print(f"Ação bem-sucedida: {result['card_name']}")
        elif actionString == "DECLARE_ATTACK":
            attackers = engine.getAttackableMonsters(engine.turnPlayer)
            if not attackers:
                print(
                    "Nenhum monstro seu pode atacar."
                )  # interface.displayMessage(...)
                continue
            attacker = interface.selectAttacker(attackers)

            targetMonsters = engine.getAttackTargets(engine.nonTurnPlayer)
            if not targetMonsters:
                engine.resolveAttack(
                    engine.turnPlayer, engine.nonTurnPlayer, attacker, None
                )
                continue
            target = interface.targetMonsterForAttack(targetMonsters)
            battleResult = engine.resolveAttack(
                engine.turnPlayer, engine.nonTurnPlayer, attacker, target
            )

        # condição de vitória/derrota por pontos de vida
        if engine.turnPlayer.life <= 0 or engine.nonTurnPlayer.life <= 0:
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
