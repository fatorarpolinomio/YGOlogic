from Components.YGOplayer import Player
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import Card, CardType
from Components.YGOgamePhase import GamePhase
import Components.cards.Traps
from Communication.network import Network
from Communication.messages_protocol import MessageConstructor, MessageType


# Classe geral, com a lógica das ações sem inputs ou prints
class YGOengine:
    def __init__(
        self,
        player1: Player,
        player2: Player,
        network: Network,
        is_host: bool = True,
    ):
        self.player1 = player1
        self.player2 = player2
        self.turnPlayer = player1
        self.nonTurnPlayer = player2

        if is_host:
            self.turnPlayer = player1
            self.nonTurnPlayer = player2
        else:
            self.turnPlayer = player2  # O host (oponente) começa
            self.nonTurnPlayer = player1

        self.currentPhase = GamePhase.DRAW
        self.turnCount = 1

        # Flags de controle por turno
        self.summonThisTurn = False

        # para rede
        self.network = network
        self.is_host = is_host
    
    
    def handle_opponent_pass_turn(self):
        """
        Processa o RECEBIMENTO da mensagem 'PASSAR_TURNO'.
        Apenas atualiza o estado interno (troca jogadores, incrementa turno),
        SEM enviar uma nova mensagem de rede.
        """
        print(f"Recebido: Oponente ({self.turnPlayer.name}) passou o turno.")
        
        # Reseta status de ataque dos monstros do jogador anterior
        for monster in self.turnPlayer.monstersInField:
            if not monster.canAttack:
                monster.canAttack = True

        # Inverte os jogadores
        self.turnPlayer, self.nonTurnPlayer = (
            self.nonTurnPlayer,
            self.turnPlayer,
        )  
        
        self.turnCount += 1
        self.summonThisTurn = False  # Reseta a flag de invocação
        self.currentPhase = GamePhase.DRAW  # Próximo turno começa na Draw Phase

        print(f"Iniciando seu turno (Turno {self.turnCount}) - {self.turnPlayer.name}")

    def handle_opponent_summon_monster(self, payload: dict):
        """
        Processa o RECEBIMENTO da mensagem 'INVOCAR_MONSTRO'.
        Cria uma "representação" do monstro e a adiciona ao campo
        do oponente (self.nonTurnPlayer).
        """
        try:
            card_data = payload.get("card_data")
            if not card_data:
                print("Erro de rede: Mensagem INVOCAR_MONSTRO sem card_data.")
                return

            print(f"Oponente invocou: {card_data.get('name')}")

            # Criamos um "dummy monster" (um objeto monstro local)
            # com os dados recebidos para representar a carta do oponente.
            # NOTA: Isso assume que seu construtor de Monstro aceita
            # (name, level, attribute, type, ATK, DEF, description)
            # Se for diferente, ajuste aqui.
            dummy_monster = Monster(
                name=card_data.get("name"),
                level=4,  # Nível padrão (não enviado)
                attribute="LIGHT",  # Atributo padrão (não enviado)
                type=CardType[card_data.get("type", "MONSTER")],
                ATK=card_data.get("ATK"),
                DEF=1000,  # DEF padrão (não enviado)
                description="Carta invocada pelo oponente.",
            )

            # Adiciona o monstro ao campo do oponente (que é o nonTurnPlayer local)
            self.nonTurnPlayer.monstersInField.append(dummy_monster)
            self.nonTurnPlayer.monstersCount += 1

        except Exception as e:
            print(f"Erro ao processar invocação do oponente: {e}")

    def handle_opponent_set_card(self, payload: dict):
        """
        Processa o RECEBIMENTO da mensagem 'COLOCAR_CARTA_BAIXO'.
        Cria uma "representação" da carta e a adiciona ao campo
        do oponente (self.nonTurnPlayer).
        """
        try:
            card_type_str = payload.get("card_type")
            if not card_type_str:
                print("Erro de rede: Mensagem COLOCAR_CARTA_BAIXO sem card_type.")
                return

            print("Oponente baixou uma carta.")

            # Criamos uma "dummy card" genérica
            # NOTA: Isso assume que seu construtor de Card aceita
            # (name, type, description)
            dummy_card = Card(
                name="Carta Baixada",
                type=CardType[card_type_str],
                description="Carta baixada pelo oponente.",
            )
            dummy_card.setted = True  # Marca a carta como "setada"

            # Adiciona a carta ao campo do oponente (que é o nonTurnPlayer local)
            self.nonTurnPlayer.spellsAndTrapsInField.append(dummy_card)
            self.nonTurnPlayer.spellsAndTrapsCount += 1

        except Exception as e:
            print(f"Erro ao processar carta baixada do oponente: {e}")
            
    def send_network_message(self, message):
        "Função auxiliar para enviar mensagens pela rede"
        if self.network and self.network.is_connected:
            success = self.network.send_message(message)
            if not success:
                print("Falha ao enviar mensagem pela rede")
            return success
        return False

    def receive_network_message(self, message):
        "Função auxiliar para receber mensagens pela rede"
        if self.network and self.network.is_connected:
            success = self.network.receive_message(message)
            if not success:
                print("Falha ao receber mensagem pela rede")
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

        # Os monstros agora podem atacar no próximo turno do controlador
        for monster in self.turnPlayer.monstersInField:
            if not monster.canAttack:
                monster.canAttack = True

        self.turnPlayer, self.nonTurnPlayer = (
            self.nonTurnPlayer,
            self.turnPlayer,
        )  # Invertendo jogadores
        self.turnCount += 1  # Incrementando contagem do turno
        self.summonThisTurn = False  # Agora, o dono do turno pode invocar
        self.currentPhase = GamePhase.DRAW  # Começa comprando uma

        # notificando fim de turno antes de trocar os jogadores
        message = MessageConstructor.passar_turno()
        self.send_network_message(message)

    # Usado para ações que mudam o estado do jogo
    def processPlayerAction(self, actionCommand: str, payload: dict = None) -> dict:
        if actionCommand == "GO_TO_BATTLE_PHASE":
            self.advanceToNextPhase()
            return {"success": True, "message": "Iniciando a Fase de Batalha."}

        elif actionCommand == "END_TURN":
            self.endTurn()
            return {"success": True, "message": "Turno encerrado. Próximo jogador."}

        elif actionCommand == "DECLARE_ATTACK":
            return {"message": "Declarando ataque."}

        elif actionCommand == "SUMMON_MONSTER":
            monsterToSummon = payload.get("card")
            if not monsterToSummon:
                return {"success": False, "reason": "Nenhum monstro especificado."}
            return self.summonMonster(self.turnPlayer, monsterToSummon)

        elif actionCommand == "SET_CARD":
            cardToSet = payload.get("card")
            if not cardToSet:
                return {"success": False, "reason": "Nenhuma carta especificada."}
            return self.setCard(self.turnPlayer, cardToSet)

        elif actionCommand == "ACTIVATE_SPELL":
            cardToActivate = payload.get("card")
            if not cardToActivate:
                return {"success": False, "reason": "Nenhuma carta especificada."}
            return self.activateSpell(
                self.turnPlayer, self.nonTurnPlayer, cardToActivate
            )

        elif actionCommand == "DRAW_CARD":
            return self.drawCard()

        return {"success": False, "reason": "Comando desconhecido."}

    def drawCard(self):
        if len(self.turnPlayer.deck) == 0:
            # Se isso aqui acontecer, o jogador perde
            return {"success": False, "reason": "DECK_EMPTY"}
        self.turnPlayer.drawCard()
        return {"success": True, "message": "Você comprou 1 carta."}

    # Métodos para MainPhase
    # Eu posso:
    # 1) Invocar um monstro
    # 2) Setar uma carta
    # 3) Ativar uma magia

    # Função para invocar monstros
    def summonMonster(self, player: Player, monster: Monster) -> dict:
        #  atingiu o limite de monstros em campo (max: 3)
        if player.monstersCount >= 3:
            return {"success": False, "reason": "MONSTER_ZONE_FULL"}

        # Se já realizou uma invocação neste turno
        if self.summonThisTurn:
            return {"success": False, "reason": "JA_INVOCOU_NESTE_TURNO"}

        # Remove da mão e adiciona ao campo
        if monster in player.hand:
            player.hand.remove(monster)
        # A ação foi bem-sucedida. Altera o estado do jogo.
        player.monstersInField.append(monster)
        player.monstersCount += 1
        self.summonThisTurn = True

        # Envia mensagem para o oponente
        card_index = len(player.monstersInField) - 1  # Índice no campo
        message = MessageConstructor.invocar_monstro(
            card_index=card_index,
            card_data={
                "name": monster.name,
                "ATK": monster.ATK,
                "type": monster.type.name
            },
        )
        self.send_network_message(message)

        return {"success": True, "card_name": monster.name}

    # Função para colocar carta virada para baixo
    def setCard(self, player: Player, card: Card) -> dict:
        if player.spellsAndTrapsCount >= 3:
            return {"success": False, "reason": "SPELL_TRAP_ZONE_FULL"}

        # Remove da mão e adiciona ao campo
        if card in player.hand:
            player.hand.remove(card)

        player.spellsAndTrapsInField.append(card)
        player.spellsAndTrapsCount += 1

        # para enviar mensagem (sem revelar o nome da carta)
        card_index = len(player.spellsAndTrapsInField) - 1
        message = MessageConstructor.colocar_carta_baixo(
            card_index=card_index, card_type=card.type.name
        )
        self.send_network_message(message)

        return {"success": True, "card_name": card.name}

    # Função para ativar magia
    def activateSpell(self, player: Player, opponent: Player, spell: Card):
        if player.spellsAndTrapsCount >= 3:
            return {"success": False, "reason": "SPELL_TRAP_ZONE_FULL"}

        # Remove da mão (se ainda estiver lá)

        card_index = player.hand.index(spell)

        spell.apply_effect(player, opponent)  # aplica o efeito
        player.hand.remove(spell)
        player.spellTrapIntoGraveyard(spell)  # move para o cemitério

        # Envia mensagem
        message = MessageConstructor.ativar_magia(
            card_index=card_index,
            card_data={
                "name": spell.name,
                "type": spell.type.name,
                "effect": spell.effectDescription,
            },
        )
        self.send_network_message(message)

        return {"success": True, "card_name": spell.name}

    # Métodos para fase de batalha:
    # Eu posso:
    # Selecionar um monstro para ser o atacante
    # Selecionar um monstro para ser o alvo do ataque e atacar
    # Se o ataque passar, teremos cálculo de dano e/ou eventual destruição de monstro(s)
    # Ativar uma armadilha em resposta a um ataque

    def activateTrap(self, player: Player, opponent: Player, trap: Card):
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
            tem_armadilha=True, ativar_armadilha=True, trap_index=trap_index
        )
        self.send_network_message(message)

        return {"success": True, "card_name": trap.name}

    def checkForTrapResponse(self, attacker_monster: Monster):
        """
        Verifica se o jogador defensor tem armadilhas que podem ser ativadas
        em resposta a este ataque.
        """
        valid_traps = []
        for trap in self.turnPlayer.spellsAndTrapsInField:
            if trap.type == CardType.TRAP:
                # Armadilha como Cilindro ou Buraco precisam saber QUEM está atacando
                if hasattr(trap, "attackingMonster"):
                    trap.attackingMonster = attacker_monster  #
                valid_traps.append(trap)

        if not valid_traps:
            return None  # Nenhuma armadilha para ativar

        return valid_traps

    # Retorna uma lista de monstros que podem atacar
    def getAttackableMonsters(self, player: Player) -> list[Monster]:
        return [m for m in player.monstersInField if m.canAttack]

    # Retorna uma lista de monstros que podem ser alvos de um ataque
    def getAttackTargets(self, opponent: Player) -> list[Monster]:
        return opponent.monstersInField

    # Calcula o resultado de uma batalha sem alterar o estado do jogo.
    # Retorna um dicionário com os danos e quais monstros são destruídos.
    def damageCalc(self, atkMonter: Monster, targetMonster: Monster):
        # Isso aqui é para ataque direto
        if targetMonster == None:
            return {
                "playerDamage": 0,
                "opponentDamage": atkMonter.ATK,
                "attackerDestroyed": False,
                "targetDestroyed": False,
            }

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

    # Resolve um ataque declarado, calcula os resultados e aplica ao estado do jogo.
    def resolveAttack(
        self,
        attackingPlayer: Player,
        defendingPlayer: Player,
        attackerMonster: Monster,
        targetMonster: Monster,
    ):
        if not attackerMonster.canAttack:
            return  # Ou envia uma mensagem de erro para o cliente

        # 1. Envia a declaração de ataque e ESPERA a resposta
        attacker_idx = attackingPlayer.monstersInField.index(attackerMonster)
        target_idx = (
            defendingPlayer.monstersInField.index(targetMonster)
            if targetMonster
            else None
        )
        message = MessageConstructor.declarar_ataque(
            atacante_index=attacker_idx, defensor_index=target_idx
        )
        self.send_network_message(message)

        print("Aguardando resposta do oponente...")
        response_message = None
        while response_message is None:
            response_message = self.network.get_message()
        # AQUI O JOGO DO ATACANTE "CONGELA" ATÉ RECEBER A RESPOSTA
        response_message = None
        while response_message is None:
            response_message = self.network.get_message()

        if (
            response_message
            and response_message.get("tipo") == MessageType.ATIVAR_ARMADILHA
            and response_message.get("ativar") == True
        ):
            trap_name = response_message.get("trap_name")

            if trap_name == "Cilindro Mágico":
                attackingPlayer.life -= attackerMonster.ATK
            elif trap_name == "Força do Espelho":
                Components.cards.Traps.MirrorForce(defendingPlayer, attackingPlayer)
            elif trap_name == "Buraco Armadilha":
                attackingPlayer.monsterIntoGraveyard(attackerMonster)
            elif trap_name == "Aparelho de Evacuação Obrigatória":
                if attackerMonster in attackingPlayer.monstersInField:
                    attackingPlayer.monstersInField.remove(attackerMonster)
                attackingPlayer.hand.append(attackerMonster)

            # Marcar o monstro como tendo atacado (mesmo que negado)
            attackerMonster.canAttack = False
            return {"attack_negated": True, "trap_name": trap_name}

        else:
            results = self.damageCalc(attackerMonster, targetMonster)

            # Aplica os danos
            attackingPlayer.life -= results["playerDamage"]
            defendingPlayer.life -= results["opponentDamage"]

            # Atualiza status do monstro atacante
            attackerMonster.canAttack = False

            if targetMonster != None:
                # pegando índices antes de mover para o cemitério (é necessário para mensagem)

                target_idx = defendingPlayer.monstersInField.index(targetMonster)

                # Move monstros destruídos para o cemitério
                if results["attackerDestroyed"]:
                    attackingPlayer.monsterIntoGraveyard(attackerMonster)

                if results["targetDestroyed"]:
                    defendingPlayer.monsterIntoGraveyard(targetMonster)

                # envia resultado da batalha
                message = MessageConstructor.resultado_batalha(
                    dano_ao_atacante=results["playerDamage"],
                    dano_ao_defensor=results["opponentDamage"],
                    monstro_atacante_destruido=results["attackerDestroyed"],
                    monstro_defensor_destruido=results["targetDestroyed"],
                    atacante_index=attacker_idx,
                    defensor_index=target_idx,
                )
                self.send_network_message(message)

                # retorna o resultado para que o servidor possa enviá-lo a ambos os clientes
                return results
