import unittest
from Communication.messages_protocol import MessageConstructor, MessageType
from Components.YGOgamePhase import GamePhase
from Components.cards.YGOcards import CardType

class TestMessageConstructor(unittest.TestCase):

    def test_passar_turno(self):
        """Verifica se a mensagem de passar turno é criada corretamente."""
        message = MessageConstructor.passar_turno()
        expected = {"tipo": MessageType.PASSAR_TURNO}
        self.assertEqual(message, expected)

    def test_invocar_monstro(self):
        """Verifica se a mensagem de invocar monstro é criada corretamente."""
        # Dados da carta como um dicionário (simulando o que a engine teria)
        card_data = {
            "name": "Dragão Branco de Olhos Azuis",
            "ATK": 3000,
            "type": CardType.MONSTER.name, # .name para "MONSTER"
        }
        
        message = MessageConstructor.invocar_monstro(
            card_index=0, 
            card_data=card_data, 
            fase=GamePhase.MAIN_1
        )
        
        expected = {
            "tipo": MessageType.INVOCAR_MONSTRO,
            "fase": GamePhase.MAIN_1.name,
            "card_index": 0,
            "card": {
                "name": "Dragão Branco de Olhos Azuis",
                "ATK": 3000,
                "type": "MONSTER",
                "effect": "",  # Protocolo adiciona "" por padrão se não existir
            },
        }
        self.assertEqual(message, expected)

    def test_resultado_batalha(self):
        """Verifica a mensagem de resultado de batalha."""
        message = MessageConstructor.resultado_batalha(
            dano_ao_atacante=500,
            dano_ao_defensor=0,
            monstro_atacante_destruido=True,
            monstro_defensor_destruido=False,
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
            "defensor_idx": 1
        }
        self.assertEqual(message, expected)