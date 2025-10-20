from enum import Enum, auto
from Components.YGOplayer import Player
import Components.YGOactions as actions
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import Card

class GamePhase(Enum):
    DRAW = auto()
    MAIN_1 = auto()
    BATTLE = auto()
    MAIN_2 = auto()
    END = auto()


class YGOengine:
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.turnPlayer = player1
        self.nonTurnPlayer = player2
        self.currentPhase = GamePhase.DRAW
        self.turnCount = 1

        # Flags de controle por turno
        self.summonThisTurn = False

    def runTurn(self):
        print(f"\n--- Turno {self.turnCount} para {self.turnPlayer.name} ---")

        # Lógica da Draw Phase
        self.currentPhase = GamePhase.DRAW
        print(f"Fase: {self.currentPhase.name}")
        self.turnPlayer.drawCard()
        # Main Phase 1
        self.runMainPhase1()

        # Battle Phase
        if self.currentPhase == GamePhase.BATTLE:
            self.runBattlePhase()

        # Main Phase 2
        if self.currentPhase == GamePhase.MAIN_2:
            self.runMainPhase2()

        self.currentPhase = GamePhase.END
        print(f"Fase: {self.currentPhase.name}")
        print(f"--- Fim do Turno de {self.turnPlayer.name} ---")
        self.endTurn()

    def endTurn(self):
        # Trocando jogadores
        self.turnPlayer, self.nonTurnPlayer = self.nonTurnPlayer, self.turnPlayer
        self.turnCount += 1
        self.summonThisTurn = False

    def runMainPhase1(self):
        self.currentPhase = GamePhase.MAIN_1
        print(f"Fase: {self.currentPhase.name}")

        while True:
            print("Ações possíveis:")
            print("[1] Ver Mão")
            print("[2] Olhar Campo")
            print("[3] Olhar Cemitério")
            print("[4] Ir para Battle Phase")
            print("[5] Encerrar Turno")
            print("[6] Sair do Jogo")
            action = input(f"{self.turnPlayer.name}, escolha sua ação: ")

            if action == "1":
                actions.viewHand(self.turnPlayer, self.summonThisTurn)
            elif action == "2":
                actions.viewField(self.turnPlayer, self.nonTurnPlayer)
            elif action == "3":
                actions.viewGraveyard(self.turnPlayer)
            elif action == "4":
                self.currentPhase = GamePhase.BATTLE
                return
            elif action == "5":
                self.currentPhase = GamePhase.END
                return
            elif action == "6":
                print("Saindo do jogo...")
            else:
                print("Ação inválida. Tente novamente.")

    def runBattlePhase(self):
        print(f"Fase: {self.currentPhase.name}")
        while True:
            print("Ações possíveis:")
            print("[1] Declarar Ataque")
            print("[2] Ir para Main Phase 2")
            action = input(f"{self.turnPlayer.name}, ecolha sua ação na batalha: ")
            if action == "1":
                # 1. Escolher monstro atacante
                # 2. Escolher monstro alvo
                # 3. Dar ao oponente a chance de responder (ativar armadilha)
                # 4. Damage Step: Calcular dano, destruir monstros, etc.
            elif action == "2":
                # Fim da battle
                break;
            else:
                print("Ação inválida.")

        print("Fim da Battle Phase.")
        self.currentPhase = GamePhase.MAIN_2 # Transição obrigatória para a MP2

        def runMainPhase2(self):
            print(f"Fase: {self.currentPhase.name}")

            while True:
                print("Ações possíveis:")
                print("[1] Ver Mão")
                print("[2] Olhar Campo")
                print("[3] Olhar Cemitério")
                print("[4] Encerrar Turno")
                print("[5] Sair do Jogo")
                action = input(f"{self.turnPlayer.name}, escolha sua ação: ")

                if action == "1":
                    actions.viewHand(self.turnPlayer, self.summonThisTurn)
                elif action == "2":
                    actions.viewField(self.turnPlayer, self.nonTurnPlayer)
                elif action == "3":
                    actions.viewGraveyard(self.turnPlayer)
                elif action == "4":
                    self.currentPhase = GamePhase.END
                    return
                elif action == "5":
                    print("Saindo do jogo...")
                else:
                    print("Ação inválida. Tente novamente.")

    # Métodos para MainPhase

    # Função para invocar monstros
    def summonMonster(self, player : Player, monster: Monster) -> dict:
        if player.monstersCount >= 3:
            print("Você atingiu o limite de monstros em campo (max: 3)") # Tirar
            return {"success": False, "reason": "MONSTER_ZONE_FULL"}

        # A ação foi bem-sucedida. Altera o estado do jogo.
        player.monstersInField.append(monster)
        print(f"Você invocou {monster.name}!") # Tirar
        player.monstersCount += 1

        return {"success": True, "card_name": monster.name}

    # Função para colocar carta virada para baixo
    def setCard(self, player : Player, card: Card) -> dict:
        if player.spellsAndTrapsCount >= 3:
            print("Você atingiu o limite de magias e armadilhas em campo (max 3)") # Tirar
            return {"success": False, "reason": "SPELL_TRAP_ZONE_FULL"}

        player.spellsAndTrapsInField.append(card)
        print(f"Você colocou a carta {card.name} virada para baixo") # Tirar
        player.spellsAndTrapsCount += 1
        return {"success": True, "card_name": card.name}

    # Função para ativar magia
    def activateSpell(self, player : Player, opponent : Player, spell: Card):
        if player.spellsAndTrapsCount >= 3:
            print("Você atingiu o limite de magias e armadilhas em campo (max 3)") # Tirar
            return {"success": False, "reason": "SPELL_TRAP_ZONE_FULL"}

        print(f"Ativando a magia {spell.name}: ") # Tirar
        spell.apply_effect(player, opponent)
        return {"success": True, "card_name": spell.name}

    # Métodos para fase de batalha:

    # Retorna uma lista de monstros que podem atacar
    def getAttackableMonsters(self, player: Player) -> list[Monster]:
        return [m for m in player.monstersInField if m.canAttack]

    # Retorna uma lista de monstros que podem ser alvos de um ataque
    def getAttackTargets(self, opponent: Player) -> list[Monster]:
        return opponent.monstersInField


    # Resolve um ataque declarado, calcula os resultados e aplica ao estado do jogo.
    def resolveAttack(self, attackingPlayer : Player, defendingPlayer : Player, attackerMonster : Monster, targetMonster : Monster):

        if not attackerMonster.canAttack:
            print(f"LÓGICA DE SERVIDOR: Tentativa de ataque ilegal com {attackerMonster.name}.")
            return # Ou envia uma mensagem de erro para o cliente

        print(f"LÓGICA DE SERVIDOR: {attackerMonster.name} ataca {targetMonster.name}!")

        # Futuramente: Aqui é o ponto para o oponente responder (enviar mensagem de 'ativar armadilha?')

        results = damageCalc(attackerMonster, targetMonster)

        # Aplica os danos
        attackingPlayer.life -= results["playerDamage"]
        defendingPlayer.life -= results["opponentDamage"]

        # Atualiza status do monstro atacante
        attackerMonster.canAttack = False

        # Move monstros destruídos para o cemitério
        if results["attackerDestroyed"]:
            print(f"LÓGICA DE SERVIDOR: {attackerMonster.name} foi destruído.")
            attackingPlayer.monsterIntoGraveyard(attackerMonster)

        if results["targetDestroyed"]:
            print(f"LÓGICA DE SERVIDOR: {targetMonster.name} foi destruído.")
            defendingPlayer.monsterIntoGraveyard(targetMonster)

        # Retorna o resultado para que o servidor possa enviá-lo a ambos os clientes
        return results

    # Calcula o resultado de uma batalha sem alterar o estado do jogo.
    # Retorna um dicionário com os danos e quais monstros são destruídos.
    def damageCalc(self, atkMonter: Monster, targetMonster: Monster):

        attackDifference = atkMonter.ATK - targetMonster.ATK;

        playerDamage = 0;
        opponentDamage = 0;
        attackerDestroyed = False;
        targetDestroyed = False;

        if attackDifference > 0: # Atacante vence
            opponentDamage = attackDifference;
            targetDestroyed = True;
        elif attackDifference < 0: # Alvo vence
            playerDamage = abs(attackDifference);
            attackerDestroyed = True;
        else: # Bater cabeça
            attackerDestroyed = True;
            targetDestroyed = True;

        return {
            "playerDamage": playerDamage,
            "opponentDamage": opponentDamage,
            "attackerDestroyed": attackerDestroyed,
            "targetDestroyed": targetDestroyed,
        }
