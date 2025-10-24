# Aqruivo para definição do protocolo de comunicação para cada mensagem

from __future__ import annotations
import typing
from typing import Dict, Any, List, Optional

from Components.YGOgamePhase import GamePhase


class MessageType:
    "Classe para definir os tipos de mensagens possíveis"

    # Setup e controle de jogo
    SETUP_JOGO = "SETUP_JOGO"
    INICIAR_TURNO = "INICIAR_TURNO"
    PASSAR_TURNO = "PASSAR_TURNO"
    SAIR = "SAIR"

    # Ações de jogo (com fase específica)
    INVOCAR_MONSTRO = "INVOCAR_MONSTRO"  # Apenas MAIN_1
    ATIVAR_MAGIA = "ATIVAR_MAGIA"  # MAIN_1
    COLOCAR_CARTA_BAIXO = "COLOCAR_CARTA_BAIXO"  # MAIN_1
    DECLARAR_ATAQUE = "DECLARAR_ATAQUE"  # BATTLE
    ATIVAR_ARMADILHA = "ATIVAR_ARMADILHA"  # BATTLE em resposta

    # Notificações
    COMPROU_CARTA = "COMPROU_CARTA"
    MUDOU_FASE = "MUDOU_FASE"
    RESULTADO_BATALHA = "RESULTADO_BATALHA"

    # Respostas
    CONFIRMACAO = "CONFIRMACAO"
    ERRO = "ERRO"


# ***Construtores de mensagens abaixo****
# já colocando Sintaxe, Gramática, Semântica pra ficar mais fácil de botar no relatório dps


class MessageConstructor:
    "classe responsável por construir mensagens seguindo o protocolo"

    @staticmethod
    def setup_jogo(mao_inicial):
        """
        Sintaxe: {"tipo":SETUP_JOGO", "sua_mao": [lista_de_cartas]}
        Gramática: "tipo" = "SETUP_JOGO" | sua_mao é uma lista_de_cartas = [{name, ATK, type, effect}, ...]
        Semântica: Enviado pelo HOST para o GUEST no início do jogo
                   Contém as 3 cartas iniciais que o guest deve ter
        """
        return {"tipo": MessageType.SETUP_JOGO, "sua_mao": mao_inicial}

    @staticmethod
    def iniciar_turno(numero_turno, comprar_carta):
        """
        Sintaxe: {"tipo": "INICIAR_TURNO", "turno": int, "comprar": bool}
        Gramática: turno = número do turno (int>=1), comprar (bool)
        Semântica: Notifica início de turno e se deve comprar carta
                   Jogador que começa (turno 1) NÃO compra
        """
        return {
            "tipo": MessageType.INICIAR_TURNO,
            "turno": numero_turno,
            "comprar": comprar_carta,
        }

    @staticmethod
    def passar_turno():
        """
        Sintaxe: {"tipo": "PASSAR_TURNO"}
        Gramática: "tipo" = "PASSAR_TURNO"
        Semântica: Indica fim do turno, passa a vez para o oponente
        """
        return {"tipo": MessageType.PASSAR_TURNO}

    @staticmethod
    def sair():
        """
        Sintaxe: {"tipo": "SAIR"}
        Gramática: "tipo" = "SAIR"
        Semântica: Jogador desistiu/encerrou conexão, encerra a partida
        """
        return {"tipo": MessageType.SAIR}

    @staticmethod
    def invocar_monstro(card_index, card_data):
        """
        Sintaxe: {"tipo": "INVOCAR_MONSTRO", "fase": "MAIN_1", "card_index": int, "card": {"name": str, "ATK": int, "type": str, "effect": str}}
        Gramática: "tipo" = "INVOCAR_MONSTRO" | "fase" é o objeto "GamePhase.MAIN_1" |
                            card_index (int) | card = {name: str, ATK: int, type: str, effect: str}
        Semântica: Jogador invoca um monstro da mão em posição de ataque
                   Receptor valida as regras: apenas 1 invocação permitida por turno e apenas na MAIN_1, atualizando o campo.
        """
        return {
            "tipo": MessageType.INVOCAR_MONSTRO,
            "fase": GamePhase.MAIN_1.name,
            "card_index": card_index,
            "card": {
                "name": card_data["name"],
                "ATK": card_data["ATK"],
                "type": card_data["type"],
                "effect": card_data.get("effect", ""),
            },
        }

    @staticmethod
    def ativar_magia(card_index, card_data):
        """
        Sintaxe: {"tipo": "ATIVAR_MAGIA", "fase": "MAIN_1", "card_index": int, "card": {...}}
        Gramática: "tipo" = "ATIVAR_MAGIA" | "fase" é o objeto "GamePhase.MAIN_1" |
                            card_index (int) | card = {name: str, type: str, effect: str}
        Semântica: Jogador ativa uma magia da mão, efeito é aplicado imediatamente
                   Carta vai para o cemitério.
        """
        return {
            "tipo": MessageType.ATIVAR_MAGIA,
            "fase": GamePhase.MAIN_1.name,
            "card_index": card_index,
            "card": {
                "name": card_data["name"],
                "type": card_data["type"],
                "effect": card_data.get("effect", ""),
            },
        }

    @staticmethod
    def colocar_carta_baixo(card_index, card_type):
        """
        Sintaxe: {"tipo": "COLOCAR_CARTA_BAIXO", "fase": "MAIN_1", "card_index": int, "card_type": str}
        Gramática: "tipo" = "COLOCAR PARA BAIXO" | "fase" = "MAIN_1" | card_index (int)  card_type = "MAGIC" ou "TRAP"
        Semântica: Jogador coloca magia/armadilha virada para baixo
                   Oponente NÃO vê o nome da carta, apenas o tipo
        """
        return {
            "tipo": MessageType.COLOCAR_CARTA_BAIXO,
            "fase": GamePhase.MAIN_1.name,
            "card_index": card_index,
            "card_type": card_type,  # Apenas tipo visível
        }

    @staticmethod
    def declarar_ataque(attacker_index, attacker_name, attacker_atk, target_index=None):
        """
        Sintaxe: {"tipo": "DECLARAR_ATAQUE", "fase": "BATTLE",
                  "attacker_index": int, "attacker_name": str, "attacker_atk": int,
                  "target_index": int|null, "ataque_direto": bool}
        Gramática: // target_index = índice do monstro alvo OU null (ataque direto)
                   ataque_direto (bool)
        Semântica: Jogador declara ataque com UM monstro
                   Se target_index = null, é ataque direto (oponente perde ATK em PV)
                   Se target_index != null, combate entre monstros
        """
        is_direct = target_index is None
        return {
            "tipo": MessageType.DECLARAR_ATAQUE,
            "fase": GamePhase.BATTLE.name,
            "attacker_index": attacker_index,
            "attacker_name": attacker_name,
            "attacker_atk": attacker_atk,
            "target_index": target_index,
            "ataque_direto": is_direct,
        }

    @staticmethod
    def ativar_armadilha(tem_armadilha, ativar_armadilha=False, trap_index=None):
        """
        Sintaxe: {"tipo": "ATIVAR_ARMADILHA", "fase": "BATTLE",
                  "tem_armadilha": bool, "ativar": bool, "trap_index": int|null}
        Gramática: "tipo" = "ATIVAR_ARMADILHA" | "fase" -> "BATTLE" |tem_armadilha (bool) |
                   ativar (bool) | trap_index (int) ou null
        Semântica: Oponente responde ao ataque declarado
                   Se ativar=True, especifica qual armadilha (trap_index)
                   Se ativar=False, ataque prossegue normalmente
        """
        return {
            "tipo": MessageType.ATIVAR_ARMADILHA,
            "fase": GamePhase.BATTLE.name,
            "tem_armadilha": tem_armadilha,
            "ativar": ativar_armadilha,
            "trap_index": trap_index,
        }

    @staticmethod
    def comprou_carta():
        """
        Sintaxe: {"tipo": "COMPROU_CARTA"}
        Gramática: "tipo" = "COMPROU_CARTA"
        Semântica: Notifica que jogador comprou carta, não revela qual carta
        """
        return {"tipo": MessageType.COMPROU_CARTA}

    @staticmethod
    def mudou_fase(nova_fase):
        """
        Sintaxe: {"tipo": "MUDOU_FASE", "fase": str}
        Gramática: fase = "DRAW" | "MAIN_1" | "BATTLE" | "END"
        Semântica: Notifica mudança de fase do turno
        """
        return {"tipo": MessageType.MUDOU_FASE, "fase": nova_fase}

    @staticmethod
    def resultado_batalha(
        dano_ao_atacante,
        dano_ao_defensor,
        monstro_atacante_destruido,
        monstro_defensor_destruido,
        atacante_index,
        defensor_index,
    ):
        """
        Sintaxe: {"tipo": "RESULTADO_BATALHA", "dano_atacante": int, "dano_defensor": int,
                    "atacante_destruido": bool, "defensor_destruido": bool,
                    "atacante_idx": int, "defensor_idx": int|null}
        Gramática: dano_atacante/defensor (int) = PV perdidos por cada jogador
                     atacante/defensor_destruido (bool) = indicando destruição
                     atacante/defensor_idx (int) = índice do monstro no campo
        Semântica: Enviado pelo jogador atacante após a resolução de uma batalha.
        Notifica ambos os jogadores sobre todo o resultado: dano de vida e quais monstros foram destruídos.
        (ação que deve ser tomada): Ambos os jogadores devem aplicar o dano à sua vida e
              mover os monstros indicados para o cemitério.
        """
        return {
            "tipo": MessageType.RESULTADO_BATALHA,
            "dano_atacante": dano_ao_atacante,
            "dano_defensor": dano_ao_defensor,
            "atacante_destruido": monstro_atacante_destruido,
            "defensor_destruido": monstro_defensor_destruido,
            "atacante_idx": atacante_index,
            "defensor_idx": defensor_index,
        }

    @staticmethod
    def confirmacao(action_type, success):
        """
        Sintaxe: {"tipo": "CONFIRMACAO", "action": str, "success": bool, "message": str}
        Gramática: // | action = ação confirmada (str) | success (bool) | message (str)
        Semântica: Mensagem genérica que confirma recebimento e processamento de uma ação
        """
        return {
            "tipo": MessageType.CONFIRMACAO,
            "action": action_type,
            "success": success,
        }

    @staticmethod
    def erro(mensagem_erro):
        """
        Sintaxe: {"tipo": "ERRO", "message": str}
        Gramática: "tipo" = "ERRO" | message = descrição do erro (str)
        Semântica: Indica erro no processamento de mensagem
        """
        return {"tipo": MessageType.ERRO, "message": mensagem_erro}
