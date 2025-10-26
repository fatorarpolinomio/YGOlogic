from typing import Set
from Components.YGOplayer import Player
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import Card, CardType
from Components.YGOgamePhase import GamePhase
import Components.cards.Traps
from Communication.network import Network
from Communication.messages_protocol import MessageConstructor, MessageType
import time


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

        # NOVO: Adiciona um estado para rastrear um ataque em andamento
        self.pending_attack = None # Vai armazenar (attacker_obj, target_obj, attacker_idx, target_idx)

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
            return {"success": False, "reason": "VOCE_JA_INVOCOU_NESTE_TURNO"}

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
                "type": monster.type.name,
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
            tem_armadilha=True, ativar_armadilha=True, trap_name=trap.name
        )
        self.send_network_message(message)

        return {"success": True, "card_name": trap.name}

    def checkForTrapResponse(self, defendingPlayer: Player, attacker_monster: Monster):
        """
        Verifica se o jogador defensor tem armadilhas que podem ser ativadas
        em resposta a este ataque.
        """
        valid_traps = []
        # verifica as armadilhas do jogador defensor
        for trap in defendingPlayer.spellsAndTrapsInField:
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
            attacker_index=attacker_idx,
            attacker_name=attackerMonster.name,
            attacker_atk=attackerMonster.ATK,
            target_index=target_idx,
        )
        self.send_network_message(message)

        print("Aguardando resposta do oponente...")
        response_message = None
        while response_message is None:
            response_message = self.network.get_message()
            time.sleep(0.1)

        if (
            response_message
            and response_message.get("tipo") == MessageType.ATIVAR_ARMADILHA
            and response_message.get("ativar") == True
        ):
            trap_name = response_message.get("trap_name")

            if trap_name == "Cilindro Mágico":
                attackingPlayer.life -= attackerMonster.ATK
            elif trap_name == "Força do Espelho":
                for monster in list(attackingPlayer.monstersInField):
                    attackingPlayer.monsterIntoGraveyard(monster)
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
                    dano_atacante=results["playerDamage"],
                    dano_defensor=results["opponentDamage"],
                    atacante_destruido=results["attackerDestroyed"],
                    defensor_destruido=results["targetDestroyed"],
                    atacante_index=attacker_idx,
                    defensor_index=target_idx,
                )
                self.send_network_message(message)

                # retorna o resultado para que o servidor possa enviá-lo a ambos os clientes
                return results

    # **Métodos (handlers) para processar mensagens recebidas do oponente***

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
            card_data = payload.get("card")
            if not card_data:
                print("Erro de rede: Mensagem INVOCAR_MONSTRO sem card_data.")
                return

        
            # Criamos um "dummy monster" (um objeto monstro local)
            # com os dados recebidos para representar a carta do oponente.
            # NOTA: Isso assume que seu construtor de Monstro aceita
            # (name, level, attribute, type, ATK, DEF, description)
            # Se for diferente, ajuste aqui.
            card_type_str = card_data.get("type")
            card_type_enum = CardType[card_type_str]
            new_monster = Monster(
                name=card_data.get("name"),
                ATK=card_data.get("ATK"),
                type=card_type_enum
            )

            if self.turnPlayer.monstersCount < 3:
                self.turnPlayer.monstersInField.append(new_monster)
                self.turnPlayer.monstersCount += 1
                print(f"Oponente invocou: {new_monster.name}")
            else:
                print(
                    "Erro de sincronia: Oponente invocou, mas o campo já estava cheio."
                )

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

            set_card = Card(
                name="Carta Baixada",
                ATK=None,
                type=CardType[card_type_str],
                effectDescription="Carta baixada pelo oponente.",
            )
            if self.turnPlayer.spellsAndTrapsCount < 3:
                self.turnPlayer.spellsAndTrapsInField.append(set_card)
                self.turnPlayer.spellsAndTrapsCount += 1
                print(f"Oponente baixou uma carta.")
            else:
                print(
                    "Erro de sincronia: Oponente baixou carta, mas o campo já estava cheio."
                )

        except Exception as e:
            print(f"Erro ao processar carta baixada do oponente: {e}")

    def handle_opponent_activate_spell(self, payload: dict):
        """
        Processa o RECEBIMENTO da mensagem 'ATIVAR_MAGIA'.
        Aplica o efeito da magia no estado do jogo.
        """
        try:
            card_data = payload.get("card")
            if not card_data:
                print("Erro de rede: Mensagem ATIVAR_MAGIA sem card_data.")
                return

            card_name = card_data.get("name")
            print(f"Oponente ativou: {card_name}")

            # NOTA: Esta é uma lógica simplificada.
            # O ideal seria ter uma "fábrica de cartas" para instanciar
            # o objeto 'spell' correto e chamar 'spell.apply_effect()'.
            # Por enquanto, usaremos lógica hardcoded como em 'resolveAttack'.

            # 'self.turnPlayer' é o oponente
            # 'self.nonTurnPlayer' é o jogador local
            
            if card_name == "Raigeki":
                print("Oponente usou Raigeki! Seus monstros são destruídos.")
                # 'list()' é usado para criar uma cópia,
                # pois vamos modificar a lista original
                for monster in list(self.nonTurnPlayer.monstersInField):
                    self.nonTurnPlayer.monsterIntoGraveyard(monster)
            
            elif card_name == "Pot of Greed":
                    print("Oponente usou Pot of Greed. (Comprou 2 cartas)")
                    # A lógica de compra real acontece no lado do oponente.
                    # Aqui apenas notificamos a interface.
                    pass 

            elif card_name == "Heavy Storm":
                print("Oponente usou Heavy Storm! S/T destruídas.")
                # Destroi S/T do oponente (self.turnPlayer)
                for card in list(self.turnPlayer.spellsAndTrapsInField):
                    self.turnPlayer.spellTrapIntoGraveyard(card)
                # Destroi S/T do jogador local (self.nonTurnPlayer)
                for card in list(self.nonTurnPlayer.spellsAndTrapsInField):
                    self.nonTurnPlayer.spellTrapIntoGraveyard(card)
            
            else:
                print(f"Efeito de '{card_name}' não implementado para recebimento.")

            # (Opcional) Adicionar a magia ao cemitério do oponente
            # Se for necessário rastrear o cemitério dele.

        except Exception as e:
            print(f"Erro ao processar magia do oponente: {e}")

    def handle_opponent_declare_attack(self, payload: dict, interface):
        """
        Processa o RECEBIMENTO da mensagem 'DECLARAR_ATAQUE'.
        Verifica por armadilhas locais e envia uma resposta 'ATIVAR_ARMADILHA'.
        (Esta lógica foi movida de Main.py e corrigida)
        """
        try:
            print("Oponente declarou um ataque!")

            # 'self.turnPlayer' é o Oponente (Atacante)
            # 'self.nonTurnPlayer' é o Jogador Local (Defensor)

            attacker_idx = payload.get("attacker_index")
            target_idx = payload.get("target_index")

            # Pega o monstro atacante do oponente
            attacker_monster = self.turnPlayer.monstersInField[attacker_idx]

            # Pega o monstro alvo (local)
            target_monster = (
                self.nonTurnPlayer.monstersInField[target_idx]
                if target_idx is not None
                else None
            )

            # 1. Pergunta ao engine se o defensor (local) tem armadilhas
            #    Passando 'self.nonTurnPlayer' como o defensor
            valid_traps = self.checkForTrapResponse(
                self.nonTurnPlayer, attacker_monster
            )

            trap_to_activate = None
            if valid_traps:
                # 2. Se houver, pergunta ao jogador defensor (local, via interface)
                trap_to_activate = interface.promptTrapActivation(
                    valid_traps, attacker_monster
                )

            # 3. Responde ao atacante
            if trap_to_activate:
                # Ativa a armadilha localmente
                # 'self.nonTurnPlayer' é o jogador local ativando a armadilha
                # A própria função activateTrap enviará a mensagem de resposta
                self.activateTrap(
                    self.nonTurnPlayer, self.turnPlayer, trap_to_activate
                )
            else:
                # Envia a resposta "NÃO"
                tem_traps = bool(valid_traps)  # Verifica se haviam traps disponíveis
                message = MessageConstructor.ativar_armadilha(
                    tem_armadilha=tem_traps, ativar_armadilha=False
                )
                self.send_network_message(message)

        except Exception as e:
            print(f"Erro ao processar declaração de ataque do oponente: {e}")

    def handle_opponent_battle_result(self, payload: dict):
        """
        Processa o RECEBIMENTO da mensagem 'RESULTADO_BATALHA'.
        Aplica os resultados da batalha ao estado do jogo local.
        """
        try:
            # 'self.turnPlayer' é o Oponente (Atacante)
            # 'self.nonTurnPlayer' é o Jogador Local (Defensor)
            
            dano_ao_oponente = payload.get("dano_ao_atacante", 0)
            dano_ao_local = payload.get("dano_ao_defensor", 0)
            oponente_destruido = payload.get("monstro_atacante_destruido", False)
            local_destruido = payload.get("monstro_defensor_destruido", False)
            oponente_idx = payload.get("atacante_idx")
            local_idx = payload.get("defensor_idx")

            # Pega idx dos monstros ANTES de qualquer remoção
            monster_atacante = None
            if oponente_idx is not None and len(self.turnPlayer.monstersInField) > oponente_idx:
                monster_atacante = self.turnPlayer.monstersInField[oponente_idx]
            
            monster_defensor = None
            if local_idx is not None and len(self.nonTurnPlayer.monstersInField) > local_idx:
                monster_defensor = self.nonTurnPlayer.monstersInField[local_idx]

            print("\n--- Resultado da Batalha ---")
            
            # 1. Aplicar dano
            if dano_ao_oponente > 0:
                self.turnPlayer.life -= dano_ao_oponente
                print(f"Oponente ({self.turnPlayer.name}) sofre {dano_ao_oponente} de dano.")
            if dano_ao_local > 0:
                self.nonTurnPlayer.life -= dano_ao_local
                print(f"Você ({self.nonTurnPlayer.name}) sofre {dano_ao_local} de dano.")

            # 2. Mover monstros destruídos para o cemitério
            if oponente_destruido and monster_atacante:
                print(f"Monstro do oponente '{monster_atacante.name}' foi destruído.")
                self.turnPlayer.monsterIntoGraveyard(monster_atacante)
            
            if local_destruido and monster_defensor:
                print(f"Seu monstro '{monster_defensor.name}' foi destruído.")
                self.nonTurnPlayer.monsterIntoGraveyard(monster_defensor)
            
            if not oponente_destruido and not local_destruido and dano_ao_local == 0 and dano_ao_oponente == 0:
                    print("Nenhum monstro foi destruído e nenhum dano foi sofrido.")
            
            # 3. Atualizar 'canAttack' do monstro atacante (se ele não foi destruído)
            if not oponente_destruido and monster_atacante:
                monster_atacante.canAttack = False

        except Exception as e:
            print(f"Erro ao processar resultado da batalha do oponente: {e}")
            