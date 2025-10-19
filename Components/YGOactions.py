from enum import Enum
from msilib import PID_LASTPRINTED
import Components.YGOcards as cards
import Components.YGOplayer as player
from abc import ABC, abstractmethod

# Ações que não envolvem troca de mensagens:


# Função para olhar o próprio campo ou o do oponente
def viewField(player: player.Player, opponent: player.Player):
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
        print("Opção inválida!")


# Função para olhar o próprio cemitério
def viewGraveyard(player: player.Player):
    count = 0
    print("Você tem as seguintes cartas no cemitério: ")
    for card in player.graveyard:
        print(f"{count}) {card.name}")
        count += 1


# Ações possíveis a partir da seleção de uma carta
def selectCard(player: player.Player, card: cards.Card, playerCanSummon: bool):
    print(f"{card.name}")
    if card.type == cards.CardType.MONSTER:
        print(f"ATK - {card.ATK}")
        if playerCanSummon:
            willSummon = int(
                input(f"Digite 0 para retornar, ou 1 para invocar {card.name}: ")
            )
            while willSummon != 0 and willSummon != 1:
                willSummon = int(input(f"Opção inválida! Tente novamente: "))
            if willSummon == 0:
                return
            else:
                player.summonMonster(card)
                playerCanSummon = False
    elif card.type == cards.CardType.SPELL:
        print(f"Efeito: {card.effectDescription}")
        if player.spellsAndTrapsCount < 3:
            nextAction = int(
                input(
                    f"Digite 0 para retornar, 1 para ativar a carta e 2 para colocá-la virada para baixo: "
                )
            )
            while nextAction < 0 and nextAction > 2:
                nextAction = int(input(f"Opção inválida! Tente novamente: "))
            if nextAction == 0:
                return
            elif nextAction == 1:
                player.activateSpell(card)
            else:
                player.setCard(card)
    else:
        print(f"Efeito: {card.effectDescription}")
        if player.spellsAndTrapsCount < 3:
            nextAction = int(
                input(f"Digite 0 para retornar ou 1 para colocá-la virada para baixo: ")
            )
            while nextAction < 0 and nextAction > 1:
                nextAction = int(input(f"Opção inválida! Tente novamente: "))
            if nextAction == 0:
                return
            else:
                player.setCard(card)


# Função para olhar a própria mão
def viewHand(player: player.Player, playerCanSummon: bool):
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
