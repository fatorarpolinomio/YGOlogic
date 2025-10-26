import unittest
from Communication.messages_protocol import MessageConstructor, MessageType

class TestMessageProtocol(unittest.TestCase):

    def test_constructor_definir_nome(self):
        name = "Yugi"
        msg = MessageConstructor.definir_nome(name)
        
        expected = {
            "tipo": MessageType.DEFINIR_NOME,
            "name": name
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_passar_turno(self):
        msg = MessageConstructor.passar_turno()
        
        expected = {
            "tipo": MessageType.PASSAR_TURNO
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_invocar_monstro(self):
        index = 1
        posicao = "DEF"
        msg = MessageConstructor.invocar_monstro(index, posicao)
        
        expected = {
            "tipo": MessageType.INVOCAR_MONSTRO,
            "hand_index": index,
            "posicao": posicao
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_declarar_ataque(self):
        attacker_idx = 0
        defender_idx = 1
        msg = MessageConstructor.declarar_ataque(attacker_idx, defender_idx)
        
        expected = {
            "tipo": MessageType.DECLARAR_ATAQUE,
            "atacante_idx": attacker_idx,
            "defensor_idx": defender_idx
        }
        self.assertDictEqual(msg, expected)

    def test_constructor_resultado_batalha(self):
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

if __name__ == '__main__':
    unittest.main()