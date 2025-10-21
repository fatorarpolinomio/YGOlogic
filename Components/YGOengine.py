from enum import Enum, auto
from Components.YGOplayer import Player
import Components.YGOactions as actions
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import Card
from Communication.network import Network
from Communication.messages_protocol import MessageConstructor, MessageType

class GamePhase(Enum):
    DRAW = auto()
    MAIN_1 = auto()
    BATTLE = auto()
    END = auto()

class YGOengine:
    def __init__(self, player1: Player, player2: Player, network: Network = None, is_host: bool = True):
        self.player1 = player1
        self.player2 = player2
        self.turnPlayer = player1
        self.nonTurnPlayer = player2
        self.currentPhase = GamePhase.DRAW
        self.turnCount = 1

        # Flags de controle por turno
        self.summonThisTurn = False

        # para rede
        self.network = network
        self.is_host = is_host

    def send_network_message(self, message):
        "Função auxiliar para enviar mensagens pela rede"
        if self.network and self.network.is_connected:
            success = self.network.send_message(message)
            if not success:
                print("Falha ao enviar mensagem pela rede")
            return success
        return False
    
    def advanceToNextPhase(self):
        """Avança o jogo para a próxima fase lógica."""
        if self.currentPhase == GamePhase.DRAW:
            self.currentPhase = GamePhase.MAIN_1
        elif self.currentPhase == GamePhase.MAIN_1:
            self.currentPhase = GamePhase.BATTLE
        elif self.currentPhase == GamePhase.BATTLE:
            self.currentPhase = GamePhase.END

        # Notifica mudança de fase
        message = MessageConstructor.mudou_fase(self.currentPhase.name)
        self.send_network_message(message)

        # Retorna a nova fase para o orquestrador saber o que aconteceu.
        return self.currentPhase

    def endTurn(self):
        """Executa a lógica de fim de turno."""

        # notificando fim de turno antes de trocar os jogadores
        message = MessageConstructor.passar_turno()
        self.send_network_message(message)

        self.turnPlayer, self.nonTurnPlayer = self.nonTurnPlayer, self.turnPlayer
        self.turnCount += 1
        self.summonThisTurn = False
        self.currentPhase = GamePhase.DRAW

    def getLegalActions(self) -> list[str]:
        """Pergunta ao Engine: 'O que o jogador pode fazer agora?'"""
        actions = ["VIEW_HAND", "VIEW_FIELD", "VIEW_GRAVEYARD"]
        if self.currentPhase == GamePhase.MAIN_1:
            actions.append("GO_TO_BATTLE_PHASE")
            actions.append("END_TURN")
        elif self.currentPhase == GamePhase.BATTLE:
            actions.append("DECLARE_ATTACK")
            actions.append("END_TURN")

        return actions

    def runTurn(self):
        print(f"\n--- Turno {self.turnCount} para {self.turnPlayer.name} ---")

        # Lógica da Draw Phase
        self.currentPhase = GamePhase.DRAW
        print(f"Fase: {self.currentPhase.name}")
        # jogador do pimeiro turno não compra
        should_draw = self.turnCount > 1

        # Notifica início de turno
        message = MessageConstructor.iniciar_turno(self.turnCount, should_draw)
        self.send_network_message(message)

        if should_draw:
            self.turnPlayer.drawCard()
            # notifica que comprou carta (sem revelar qual)
            draw_message = MessageConstructor.comprou_carta()
            self.send_network_message(draw_message) 
        
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

    #def endTurn(self):
        # Trocando jogadores
    #    self.turnPlayer, self.nonTurnPlayer = self.nonTurnPlayer, self.turnPlayer
    #    self.turnCount += 1
    #    self.summonThisTurn = False

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
                # notificando com mensagem SAIR
                message = MessageConstructor.sair()
                self.send_network_message(message)
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
                break
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
                    print("Saindo do jogo..")
                else:
                    print("Ação inválida. Tente novamente.")

    # Métodos para MainPhase

    # Função para invocar monstros
    def summonMonster(self, player : Player, monster: Monster) -> dict:
        if player.monstersCount >= 3:
            print("Você atingiu o limite de monstros em campo (max: 3)") # Tirar
            return {"success": False, "reason": "MONSTER_ZONE_FULL"}

        if self.summonThisTurn:
            print("Você já realizou uma invocação neste turno")
            return {"success": False, "reason": "JA_INVOCOU_NESTE_TURNO"}
        
        # Remove da mão e adiciona ao campo
        if monster in player.hand:
            player.hand.remove(monster)

        # A ação foi bem-sucedida. Altera o estado do jogo.
        player.monstersInField.append(monster)
        print(f"Você invocou {monster.name}!") # Tirar
        player.monstersCount += 1
        self.summonThisTurn = True

        # Envia mensagem para o oponente
        card_index = len(player.monstersInField) - 1  # Índice no campo
        message = MessageConstructor.invocar_monstro(
            card_index=card_index,
            card_data={
                "name": monster.name,
                "ATK": monster.ATK,
                "type": monster.type.name,
                "effect": monster.effectDescription
            }
        )
        self.send_network_message(message)

        return {"success": True, "card_name": monster.name}

    # Função para colocar carta virada para baixo
    def setCard(self, player : Player, card: Card) -> dict:
        if player.spellsAndTrapsCount >= 3:
            print("Você atingiu o limite de magias e armadilhas em campo (max 3)") # Tirar
            return {"success": False, "reason": "SPELL_TRAP_ZONE_FULL"}

        # Remove da mão e adiciona ao campo
        if card in player.hand:
            player.hand.remove(card)    

        player.spellsAndTrapsInField.append(card)
        print(f"Você colocou a carta {card.name} virada para baixo") # Tirar
        player.spellsAndTrapsCount += 1

        # para enviar mensagem (sem revelar o nome da carta)
        card_index = len(player.spellsAndTrapsInField) - 1
        message = MessageConstructor.colocar_carta_baixo(
            card_index=card_index,
            card_type=card.type.name
        )
        self.send_network_message(message)

        return {"success": True, "card_name": card.name}

    # Função para ativar magia
    def activateSpell(self, player : Player, opponent : Player, spell: Card):
        if player.spellsAndTrapsCount >= 3:
            print("Você atingiu o limite de magias e armadilhas em campo (max 3)") # Tirar
            return {"success": False, "reason": "SPELL_TRAP_ZONE_FULL"}

        print(f"Ativando a magia {spell.name}: ") # Tirar

        # Remove da mão (se ainda estiver lá)
        if spell in player.hand:
            card_index = player.hand.index(spell)
            player.hand.remove(spell)

        spell.apply_effect(player, opponent) # aplica o efeito
        player.graveyard.append(spell) # move para o cemitério

        # Envia mensagem
        message = MessageConstructor.ativar_magia(
            card_index=card_index,  
            card_data={
                "name": spell.name,
                "type": spell.type.name,
                "effect": spell.effectDescription
            }
        )
        self.send_network_message(message)

        return {"success": True, "card_name": spell.name}

    # Métodos para fase de batalha:
    
    def activateTrap(self, player : Player, opponent : Player, trap: Card):
        print(f"Ativando a armadilha: {trap.name}")
        # pegando index para mensagem
        if trap in player.spellsAndTrapsInField:
            trap_index = player.spellsAndTrapsInField.index(trap)
        else:
            trap_index = -1

        trap.apply_effect(player, opponent)

        # movendo para cemitério
        if trap in player.spellsAndTrapsInField:
            player.spellsAndTrapsInField.remove(trap)
            player.spellsAndTrapsCount -= 1
        player.graveyard.append(trap)
        
        # enviando mensagem
        message = MessageConstructor.ativar_armadilha(
            tem_armadilha=True,
            ativar_armadilha=True,
            trap_index=trap_index
        )
        self.send_network_message(message)

        return {"success": True, "card_name": trap.name}
    
    # Retorna uma lista de monstros que podem atacar
    def getAttackableMonsters(self, player: Player) -> list[Monster]:
        return [m for m in player.monstersInField if m.canAttack]

    # Retorna uma lista de monstros que podem ser alvos de um ataque
    def getAttackTargets(self, opponent: Player) -> list[Monster]:
        return opponent.monstersInField

    # Calcula o resultado de uma batalha sem alterar o estado do jogo.
    # Retorna um dicionário com os danos e quais monstros são destruídos.
    def damageCalc(self, atkMonter: Monster, targetMonster: Monster):

        attackDifference = atkMonter.ATK - targetMonster.ATK

        playerDamage = 0
        opponentDamage = 0
        attackerDestroyed = False
        targetDestroyed = False

        if attackDifference > 0: # Atacante vence
            opponentDamage = attackDifference
            targetDestroyed = True
        elif attackDifference < 0: # Alvo vence
            playerDamage = abs(attackDifference)
            attackerDestroyed = True
        else: # Bater cabeça
            attackerDestroyed = True
            targetDestroyed = True

        return {
            "playerDamage": playerDamage,
            "opponentDamage": opponentDamage,
            "attackerDestroyed": attackerDestroyed,
            "targetDestroyed": targetDestroyed,
        }
    
    # Resolve um ataque declarado, calcula os resultados e aplica ao estado do jogo.
    def resolveAttack(self, attackingPlayer : Player, defendingPlayer : Player, attackerMonster : Monster, targetMonster : Monster):

        if not attackerMonster.canAttack:
            print(f"LÓGICA DE SERVIDOR: Tentativa de ataque ilegal com {attackerMonster.name}.")
            return # Ou envia uma mensagem de erro para o cliente

        print(f"LÓGICA DE SERVIDOR: {attackerMonster.name} ataca {targetMonster.name}!")

        # Futuramente: Aqui é o ponto para o oponente responder (enviar mensagem de 'ativar armadilha?')

        results = self.damageCalc(attackerMonster, targetMonster)

        # Aplica os danos
        attackingPlayer.life -= results["playerDamage"]
        defendingPlayer.life -= results["opponentDamage"]

        # Atualiza status do monstro atacante
        attackerMonster.canAttack = False

        # pegando índices antes de mover para o cemitério (é necessário para mensagem)
        attacker_idx = attackingPlayer.monstersInField.index(attackerMonster)
        target_idx = defendingPlayer.monstersInField.index(targetMonster)

        # Move monstros destruídos para o cemitério
        if results["attackerDestroyed"]:
            print(f"LÓGICA DE SERVIDOR: {attackerMonster.name} foi destruído.")
            attackingPlayer.monsterIntoGraveyard(attackerMonster)

        if results["targetDestroyed"]:
            print(f"LÓGICA DE SERVIDOR: {targetMonster.name} foi destruído.")
            defendingPlayer.monsterIntoGraveyard(targetMonster)
        
        # Mostra resultado
        if results["playerDamage"] > 0:
            print(f"Você recebeu {results['playerDamage']} de dano! Vida: {attackingPlayer.life}")
        if results["opponentDamage"] > 0:
            print(f"Oponente recebeu {results['opponentDamage']} de dano! Vida: {defendingPlayer.life}")

        # envia resultado da batalha
        message = MessageConstructor.resultado_batalha(
            dano_ao_atacante=results["playerDamage"],
            dano_ao_defensor=results["opponentDamage"],
            monstro_atacante_destruido=results["attackerDestroyed"],
            monstro_defensor_destruido=results["targetDestroyed"],
            atacante_index=attacker_idx,
            defensor_index=target_idx
        )
        self.send_network_message(message)

        # retorna o resultado para que o servidor possa enviá-lo a ambos os clientes
        return results
