import Components.YGOplayer as player
import Components.cards.YGOcards as cards
from Components.cards.YGOcards import CardType

class YGOinterface:

    def cardAction(self, card : cards.Card, playerCanSummon: bool) -> dict | None:
        """
        Mostra as ações para uma carta e retorna um "comando" representando a escolha do jogador.
        NÃO executa a ação, apenas pergunta.
        """
        print(f"\n Carta Selecionada: {card.name}")

        options = {}
        option_index = 1

        if card.type == CardType.MONSTER and playerCanSummon:
            print(f"{option_index}) Invocar Monstro")
            options[option_index] = {"action": "SUMMON", "card": card}
            option_index += 1

        elif card.type == CardType.SPELL:
            print(f"{option_index}) Ativar Magia")
            options[option_index] = {"action": "ACTIVATE_SPELL", "card": card}
            option_index += 1
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
        if visualiza == 1:
            print("Você tem os seguintes monstros em campo: ")
            for monster in player.monstersInField:
                print(f"{count}) {monster.name} - ATK {monster.ATK}")
                count += 1
            count = 0
            print("Você tem as seguintes magias/armadilhas viradas para baixo em campo: ")
            for spellTrap in player.spellsAndTrapsInField:
                print(f"{count}) {spellTrap.name}")
                count += 1
        elif visualiza == 2:
            print(
                f"Seu oponente tem {opponent.spellsAndTrapsCount} cartas viradas para baixo e os seguintes monstros em campo: "
            )
            for monster in opponent.monstersInField:
                print(f"{count}) {monster.name} - ATK {monster.ATK}")
                count += 1
        else:
            print("Opção inválida!"))

    # Função para olhar o próprio cemitério
    def viewGraveyard(self, player: player.Player):
        count = 0
        print("Você tem as seguintes cartas no cemitério: ")
        for card in player.graveyard:
            print(f"{count}) {card.name}")
            count += 1


    # Função para olhar a própria mão
    def viewHand(self, player: player.Player, playerCanSummon: bool):
        count = 0
        for card in player.hand:
            count += 1
            print(f"{count}) {card.name}")

        next = int(
            input(
                "Digite o índice da carta para selecioná-la ou 0 para voltar ao estado anterior: "
            )
        )
        while next < 0 or next > len(player.hand):
            next = int(input("Opção inválida! Tente novamente: "))

        if next == 0:
            return
        else:
            selectCard(player, player.hand[next], playerCanSummon)
