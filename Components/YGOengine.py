from enum import Enum, auto
from Components.YGOplayer import Player
import Components.YGOactions as actions


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
