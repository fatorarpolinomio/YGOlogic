from Communication.network import Network
from Components.YGOinterface import YGOinterface
from Components.YGOengine import YGOengine, GamePhase
from Components.YGOplayer import Player


def setup_game(net: Network, is_host: bool) -> tuple[Player, Player]:
    """
    Prepara o jogo, cria os jogadores e troca as informações iniciais.
    Retorna os objetos (player, opponent) prontos para o jogo
    """

    playerName = input("Digite seu nome: ")
    player = Player(playerName, 4000)
    player.shuffleDeck()
    player.initialHand()
    opponentName = ""

    if is_host:
        # espera o nome do oponente para poder criar o objeto dele
        opponent_name_data = net.receive_message()
        opponent_name = opponent_name_data["name"]
        net.send_message({"name": player.name})

    else:  # Se for o convidado
        # Convidado envia seu nome primeiro
        net.send_message({"name": playerName})
        opponent_name_data = net.receive_message()
        opponent_name = opponent_name_data["name"]

    print(f"Seu oponente é: {opponent_name}")

    opponent = Player(opponentName, 4000)

    if not opponent_name:
        print("Erro ao trocar informações com o oponente.")
        return None, None

    print(f"\n--- Jogo Iniciado: {player.name} vs {opponent.name} ---")

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
        if my_turn:
            currentPlayer = engine.turnPlayer
            currentPhase = engine.currentPhase

            interface.displayPhase(
                currentPhase.name, currentPlayer.name, engine.turnCount
            )
            print(
                f"Sua Vida: {engine.turnPlayer.life} | Vida do Oponente: {engine.nonTurnPlayer.life}"
            )

            actionString = None

            if currentPhase == GamePhase.DRAW:
                actionString = "DRAW_CARD"
                # print da fase de compra na interface
                result = engine.processPlayerAction(actionString)

                # Aqui, o cara tomou deckout, perdendo o jogo
                if result == {"success": False, "reason": "DECK_EMPTY"}:
                    game_over = True
                    break

                engine.advanceToNextPhase()
                continue

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
                commandDict = interface.viewHand(
                    engine.turnPlayer, engine.summonThisTurn
                )
                if commandDict:
                    # O usuário selecionou uma carta e uma ação (ex: SUMMON)
                    # Agora, passamos esse comando para o engine processar
                    result = engine.processPlayerAction(
                        commandDict["action"], commandDict
                    )

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
        else:
            print("\nAguardando jogada do oponente...")

            received_message = net.receive_message()
            if not received_message:
                print("Oponente desconectado.")
                game_over = True
                continue

            # engine.processNetworkAction(received_message)
            engine.receive_network_message(received_message)

            if received_message.get("tipo") == "END_TURN":
                print("Oponente encerrou o turno.")
                # O engine do oponente já trocou os jogadores.
                # Agora o *seu* engine local precisa fazer o mesmo.
                engine.endTurn()
                my_turn = True  # AGORA É O SEU TURNO
                continue
        # condição de vitória/derrota por pontos de vida
        if engine.turnPlayer.life <= 0 or engine.nonTurnPlayer.life <= 0:
            game_over = True

    # Lógica de Fim de Jogo
    print("\n--- FIM DE JOGO ---")
    if engine.turnPlayer.life <= 0:
        print("Você perdeu!")
    elif engine.nonTurnPlayer.life <= 0:
        print("Você venceu!")
    elif len(engine.turnPlayer.deck) == 0:
        print("Você perdeu! (deckout)")
    elif len(engine.nonTurnPlayer.deck) == 0:
        print("Você venceu! (deckout do oponente)")
    else:
        # se ninguém perdeu por pontos de vida, o jogo terminou por desconexão ou desistência
        print("A partida foi encerrada.")


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
