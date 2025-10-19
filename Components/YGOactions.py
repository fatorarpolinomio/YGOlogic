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


def selectMonsterToBattle(player: player.Player, opponent: player.Player):
    if player.monstersCount == 0:
        print("Você não tem monstros para atacar!")
        return

    while True:
        count = 0
        print("Você tem os seguintes monstros em campo que podem atacar: ")
        for monster in player.monstersInField:
            if monster.canAttack:
                count += 1
                print(f"{count}) {monster.name} - ATK {monster.ATK}")
        # consertar
        atacar = int(
            input("Digite 0 para retornar ou o índice do monstro para atacar com ele: ")
        )

        if atacar == 0:
            return
        elif atacar > 0 and atacar <= count:
            declareAttack(player, opponent, player.monstersInField[atacar])
        else:
            print("Opção inválida!")
            return


# Essa função aqui precisa mandar mensagem para o oponente
def declareAttack(
    player: player.Player, opponent: player.Player, playerMonster: cards.Monster
):
    print(f"Você selecionou {playerMonster.name} para atacar!")

    if opponent.monstersCount == 0:
        print("Realizando ataque diretamente ao oponente!")
        # Função para cálculo de dano
        playerMonster.canAttack = False
        return

    count = 0
    print("O oponente tem os seguintes monstros em campo: ")
    for monster in opponent.monstersInField:
        count += 1
        print(f"{count}) {monster.name} - ATK {monster.ATK}")

    declararAtaque = int(
        input(
            f"Digite 0 para retornar ou o índice do monstro para atacar ele com {playerMonster.name}: "
        )
    )
    while declararAtaque < 0 and declararAtaque > count:
        declararAtaque = int(input("Opção inválida! Tente novamente: "))

    if declararAtaque == 0:
        return
    elif declararAtaque > 0 or declararAtaque <= count:
        playerMonster.canAttack = False
        # Aqui, precisamos colocar o envio de mensagem. O oponente pode responder com armadilha
        # Condicional
        print(
            f"Você declarou um ataque com {playerMonster.name} ao {opponent.monstersInField[declararAtaque].name}!"
        )
        # if -> oponente tem armadilha? Se sim, esperar resposta
        # se não:
        result = damageCalc(
            player, opponent, playerMonster, opponent.monstersInField[declararAtaque]
        )
        if result > 0:
            print(f"{opponent.monstersInField[declararAtaque].name} foi destruído!")
            opponent.intoGraveyard(opponent.monstersInField[declararAtaque])
            opponent.monstersInField.pop(declararAtaque)
        elif result < 0:
            print(f"{playerMonster.name} foi destruído!")
            player.intoGraveyard(playerMonster)
            player.monstersInField.remove(playerMonster)
        elif result == 0:
            print("Ambos os monstros foram destruídos!")
            opponent.intoGraveyard(opponent.monstersInField[declararAtaque])
            opponent.monstersInField.pop(declararAtaque)
            player.intoGraveyard(playerMonster)
            player.monstersInField.remove(playerMonster)

        return


# Outra função que precisa mandar mensagem
def damageCalc(atkMonter: cards.Monster, targetMonster: cards.Monster):
    attackDifference = atkMonter.ATK - targetMonster.ATK
    playerDamage = 0
    opponentDamage = 0
    attackerDestroyed = False
    targetDestroyed = False
    if attackDifference > 0:  # Atacante vence
        opponentDamage = attackDifference
        targetDestroyed = True
    elif attackDifference < 0:  # Alvo vence
        playerDamage = abs(attackDifference)
        attackerDestroyed = True
    else:  # Bater cabeça
        attackerDestroyed = True
        targetDestroyed = True

    return {
        "playerDamage": playerDamage,
        "opponentDamage": opponentDamage,
        "attackerDestroyed": attackerDestroyed,
        "targetDestroyed": targetDestroyed,
    }
