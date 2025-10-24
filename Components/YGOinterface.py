import Components.YGOplayer as player
from Components.cards.Monsters import Monster
import Components.cards.YGOcards as cards
from Components.cards.YGOcards import CardType
import time


class YGOinterface:
    def promptMainPhaseActions(self, playerName: str) -> str:
        print("\nAções possíveis da Main Phase:")
        print("[1] Ver Mão")
        print("[2] Olhar Campo")
        print("[3] Olhar Cemitério")
        print("[4] Ir para Battle Phase")
        print("[5] Encerrar Turno")

        while True:
            choice = input(f"{playerName}, escolha sua ação: ")
            if choice == "1":
                return "VIEW_HAND"
            if choice == "2":
                return "VIEW_FIELD"
            if choice == "3":
                return "VIEW_GRAVEYARD"
            if choice == "4":
                return "GO_TO_BATTLE_PHASE"
            if choice == "5":
                return "END_TURN"
            print("Opção inválida.")

    def promptBattlePhaseActions(self, playerName: str) -> str:
        print("\nAções possíveis da Batalha:")
        print("[1] Olhar Campo")
        print("[2] Olhar Cemitério")
        print("[3] Atacar")
        print("[4] Encerrar Turno")

        while True:
            choice = input(f"{playerName}, escolha sua ação: ")
            if choice == "1":
                return "VIEW_FIELD"
            if choice == "2":
                return "VIEW_GRAVEYARD"
            if choice == "3":
                return "DECLARE_ATTACK"
            if choice == "4":
                return "END_TURN"
            print("Opção inválida.")

    def displayPhase(self, phaseName: str, playerName: str, turnCount: int):
        print(f"\n--- Turno {turnCount} para {playerName} ---")
        print(f"Fase: {phaseName}")

    def cardAction(self, card: cards.Card, playerCanSummon: bool) -> dict | None:
        """
        Mostra as ações para uma carta e retorna um "comando" representando a escolha do jogador.
        NÃO executa a ação, apenas pergunta.
        """
        print(f"\n Carta Selecionada: {card.name}")

        options = {}
        option_index = 1

        if card.type == CardType.MONSTER:  # and playerCanSummon:
            print(f"{option_index}) Invocar Monstro")
            options[option_index] = {"action": "SUMMON_MONSTER", "card": card}
            option_index += 1

        elif card.type == CardType.SPELL:
            print(f"{option_index}) Ativar Magia")
            options[option_index] = {"action": "ACTIVATE_SPELL", "card": card}
            option_index += 1
            print(f"{option_index}) Baixar Carta")
            options[option_index] = {"action": "SET_CARD", "card": card}
            option_index += 1

        elif card.type == CardType.TRAP:
            print(f"{option_index}) Baixar Carta")
            options[option_index] = {"action": "SET_CARD", "card": card}
            option_index += 1

        print("0) Voltar")

        while True:
            choice = int(input("Escolha uma ação: "))
            try:
                if choice == 0:
                    return None
                if choice in options:
                    return options[choice]
                else:
                    print("Opção inválida")
            except ValueError:
                print("Por favor, digite um número válido.")

    # Função para olhar o próprio campo ou o do oponente
    def viewField(self, player: player.Player, opponent: player.Player):
        visualiza = int(
            input("Você deseja ver (1) O próprio campo ou (2) O campo do oponente? ")
        )
        count = 0
        print("")
        if visualiza == 1:
            if len(player.monstersInField) > 0:
                print("Você tem os seguintes monstros em campo: ")
                for monster in player.monstersInField:
                    print(f"{count}) {monster.name} - ATK {monster.ATK}")
                    count += 1
            else:
                print("Você não tem nenhum monstro em campo.")
            time.sleep(2)

            if len(player.spellsAndTrapsInField) > 0:
                count = 0
                print(
                    "Você tem as seguintes magias/armadilhas viradas para baixo em campo: "
                )
                for spellTrap in player.spellsAndTrapsInField:
                    count += 1
                    print(f"{count}) {spellTrap.name}")
            else:
                print("Você não tem nenhuma magia ou armadilha virada para baixo.")
            time.sleep(2)
        elif visualiza == 2:
            if len(opponent.monstersInField) > 0:
                print(
                    f"Seu oponente tem {opponent.spellsAndTrapsCount} cartas viradas para baixo e os seguintes monstros em campo: "
                )
                for monster in opponent.monstersInField:
                    print(f"{count}) {monster.name} - ATK {monster.ATK}")
                    count += 1
            else:
                print(
                    f"Seu oponente tem {opponent.spellsAndTrapsCount} cartas viradas para baixo e nenhum monstro em campo."
                )
            time.sleep(2)
        else:
            print("Opção inválida!")
            time.sleep(2)

    # Função para olhar o próprio cemitério
    def viewGraveyard(self, player: player.Player):
        count = 0
        print("")
        if len(player.graveyard) > 0:
            print("Você tem as seguintes cartas no cemitério: ")
            for card in player.graveyard:
                count += 1
                print(f"{count}) {card.name}")
        else:
            print("Você não tem cartas no cemitério.")
        time.sleep(2)

    # Função para olhar a própria mão
    def viewHand(self, player: player.Player, playerCanSummon: bool):
        count = 0
        print("")
        if len(player.hand) > 0:
            for card in player.hand:
                count += 1
                print(f"{count}) {card.name}")

            next = int(
                input(
                    "Digite o índice da carta para selecioná-la ou 0 para voltar ao estado anterior: "
                )
            )
            print("")
            while next < 0 or next > len(player.hand):
                next = int(input("Opção inválida! Tente novamente: "))

            if next == 0:
                return
            else:
                return self.cardAction(player.hand[next - 1], playerCanSummon)
        else:
            print("Você não tem cartas na mão.")
        time.sleep(2)

    def selectAttacker(self, attackers: list[Monster]):
        count = 0
        print("Você tem o(s) seguinte(s) monstro(s) em campo: ")
        for monster in attackers:
            count += 1
            print(f"{count}) {monster.name} - ATK {monster.ATK}")

        target = int(
            input(
                "Digite o índice do monstro alvo para selecioná-lo ou 0 para cancelar o ataque: "
            )
        )
        while target < 0 or target > len(attackers):
            target = int(input("Opção inválida! Tente novamente: "))

        if target == 0:
            return None
        else:
            return attackers[target - 1]

    def targetMonsterForAttack(self, targets: list[Monster]) -> Monster:
        count = 0
        print("Seu oponente tem o(s) seguinte(s) monstro(s) em campo: ")
        for monster in targets:
            count += 1
            print(f"{count}) {monster.name} - ATK {monster.ATK}")

        target = int(
            input(
                "Digite o índice do monstro alvo para selecioná-lo ou 0 para cancelar o ataque: "
            )
        )
        while target < 0 or target > len(targets):
            target = int(input("Opção inválida! Tente novamente: "))

        if target == 0:
            return None
        else:
            return targets[target - 1]

    def promptTrapActivation(
        self, valid_traps: list[cards.Card], attacker: Monster
    ) -> cards.Card:
        """
        Mostra ao jogador defensor as armadilhas que ele pode ativar.
        """
        print(
            f"\n!!! O oponente declarou um ataque com {attacker.name} (ATK {attacker.ATK}) !!!"
        )
        print("Você pode ativar uma das seguintes armadilhas:")

        count = 1
        for trap in valid_traps:
            print(f"[{count}] {trap.name}")
            count += 1
        print("[0] Não ativar nada")

        while True:
            try:
                choice = int(input("Escolha sua ação: "))
                if choice == 0:
                    return None  # Jogador escolheu não ativar
                elif 0 < choice <= len(valid_traps):
                    return valid_traps[
                        choice - 1
                    ]  # Retorna a CARTA ARMADILHA escolhida
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Por favor, digite um número.")
