# Código deste teste foi realizado com auxílio do Gemini 2.5 Pro como dito no relatório

import unittest
from Communication.messages_protocol import MessageConstructor, MessageType

# Importação necessária,baseada no messages_protocol.py
from Components.YGOgamePhase import GamePhase 

class TestMessageProtocol(unittest.TestCase):

    def test_constructor_definir_nome(self):
        name = "Yugi"
        msg = MessageConstructor.definir_nome(name)
        
        expected = {
            "tipo": MessageType.DEFINIR_NOME,
            "name": name
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_setup_jogo(self):
        mao_inicial = [{"name": "Mago Negro", "ATK": 2500, "type": "MONSTER", "effect": "..."}]
        msg = MessageConstructor.setup_jogo(mao_inicial)
        
        expected = {
            "tipo": MessageType.SETUP_JOGO,
            "sua_mao": mao_inicial
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_iniciar_turno(self):
        msg = MessageConstructor.iniciar_turno(numero_turno=2, comprar_carta=True)
        
        expected = {
            "tipo": MessageType.INICIAR_TURNO,
            "turno": 2,
            "comprar": True
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_passar_turno(self):
        msg = MessageConstructor.passar_turno()
        
        expected = {
            "tipo": MessageType.PASSAR_TURNO
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_sair(self):
        msg = MessageConstructor.sair()
        expected = {"tipo": MessageType.SAIR}
        self.assertDictEqual(msg, expected)

    def test_constructor_invocar_monstro(self):
        # ESTE TESTE FOI CORRIGIDO
        # A assinatura antiga era (index, posicao)
        # A nova é (card_index, card_data)
        index = 1
        card_data = {"name": "Mago Negro", "ATK": 2500, "type": "MONSTER"}
        
        msg = MessageConstructor.invocar_monstro(index, card_data)
        
        expected = {
            "tipo": MessageType.INVOCAR_MONSTRO,
            "fase": GamePhase.MAIN_1.name,
            "card_index": index,
            "card": {
                "name": card_data["name"],
                "ATK": card_data["ATK"],
                "type": card_data["type"],
            },
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_ativar_magia(self):
        index = 0
        card_data = {"name": "Buraco Negro", "type": "MAGIC", "effect": "Destroi tudo"}
        msg = MessageConstructor.ativar_magia(index, card_data)
        
        expected = {
            "tipo": MessageType.ATIVAR_MAGIA,
            "fase": GamePhase.MAIN_1.name,
            "card_index": index,
            "card": {
                "name": card_data["name"],
                "type": card_data["type"],
                "effect": card_data["effect"],
            },
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_colocar_carta_baixo(self):
        index = 2
        card_type = "TRAP"
        msg = MessageConstructor.colocar_carta_baixo(index, card_type)
        
        expected = {
            "tipo": MessageType.COLOCAR_CARTA_BAIXO,
            "fase": GamePhase.MAIN_1.name,
            "card_index": index,
            "card_type": card_type,
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_declarar_ataque_monstro(self):
        # ESTE TESTE FOI CORRIGIDO E DIVIDIDO
        # A assinatura antiga era (attacker_idx, defender_idx)
        # A nova é (attacker_index, attacker_name, attacker_atk, target_index=None)
        
        attacker_idx = 0
        attacker_name = "Dragão Branco"
        attacker_atk = 3000
        target_idx = 1
        
        msg = MessageConstructor.declarar_ataque(attacker_idx, attacker_name, attacker_atk, target_idx)
        
        expected = {
            "tipo": MessageType.DECLARAR_ATAQUE,
            "fase": GamePhase.BATTLE.name,
            "attacker_index": attacker_idx,
            "attacker_name": attacker_name,
            "attacker_atk": attacker_atk,
            "target_index": target_idx,
            "ataque_direto": False
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_declarar_ataque_direto(self):
        # Testando o caso de ataque direto (target_index=None)
        attacker_idx = 0
        attacker_name = "Dragão Branco"
        attacker_atk = 3000
        
        msg = MessageConstructor.declarar_ataque(attacker_idx, attacker_name, attacker_atk, target_index=None)
        
        expected = {
            "tipo": MessageType.DECLARAR_ATAQUE,
            "fase": GamePhase.BATTLE.name,
            "attacker_index": attacker_idx,
            "attacker_name": attacker_name,
            "attacker_atk": attacker_atk,
            "target_index": None,
            "ataque_direto": True
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_ativar_armadilha(self):
        # Testando o caso de ativar a armadilha
        msg = MessageConstructor.ativar_armadilha(tem_armadilha=True, ativar_armadilha=True, trap_name="Cilindro Magico")
        
        expected = {
            "tipo": MessageType.ATIVAR_ARMADILHA,
            "fase": GamePhase.BATTLE.name,
            "tem_armadilha": True,
            "ativar": True,
            "trap_name": "Cilindro Magico",
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_nao_ativar_armadilha(self):
        # Testando o caso de não ativar (ou não ter)
        msg = MessageConstructor.ativar_armadilha(tem_armadilha=True, ativar_armadilha=False)
        
        expected = {
            "tipo": MessageType.ATIVAR_ARMADILHA,
            "fase": GamePhase.BATTLE.name,
            "tem_armadilha": True,
            "ativar": False,
            "trap_name": None,
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_comprou_carta(self):
        msg = MessageConstructor.comprou_carta()
        expected = {"tipo": MessageType.COMPROU_CARTA}
        self.assertDictEqual(msg, expected)

    def test_constructor_mudou_fase(self):
        nova_fase = GamePhase.END.name
        msg = MessageConstructor.mudou_fase(nova_fase)
        
        expected = {
            "tipo": MessageType.MUDOU_FASE,
            "fase": nova_fase
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_resultado_batalha(self):
        # Este teste já estava correto
        msg = MessageConstructor.resultado_batalha(
            dano_atacante=500,
            dano_defensor=0,
            atacante_destruido=True,
            defensor_destruido=False,
            atacante_index=0,
            defensor_index=1
        )
        
        expected = {
            "tipo": MessageType.RESULTADO_BATALHA,
            "dano_atacante": 500,
            "dano_defensor": 0,
            "atacante_destruido": True,
            "defensor_destruido": False,
            "atacante_idx": 0,
            "defensor_idx": 1,
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_confirmacao(self):
        msg = MessageConstructor.confirmacao(action_type=MessageType.INVOCAR_MONSTRO, success=True)
        
        expected = {
            "tipo": MessageType.CONFIRMACAO,
            "action": MessageType.INVOCAR_MONSTRO,
            "success": True,
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_erro(self):
        msg = MessageConstructor.erro(mensagem_erro="Ação ilegal")
        
        expected = {
            "tipo": MessageType.ERRO,
            "message": "Ação ilegal"
        }
        self.assertDictEqual(msg, expected)


if __name__ == '__main__':
    unittest.main()