# Código deste teste foi realizado com auxílio do Gemini 2.5 Pro como dito no relatório

import unittest
from unittest.mock import Mock, patch, MagicMock

# Importa as classes reais e mocks necessários
from Components.YGOengine import YGOengine
from Components.YGOgamePhase import GamePhase
from Components.YGOplayer import Player
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import Card, CardType
from Components.cards.FacedownCard import FacedownCard
from Communication.network import Network
from Communication.messages_protocol import MessageConstructor, MessageType

# --- Mocks para as Cartas ---
# (Usamos MagicMock para simular cartas sem depender das classes reais de Spells/Traps)

mock_blue_eyes = MagicMock(spec=Monster)
mock_blue_eyes.name = "Blue-Eyes White Dragon"
mock_blue_eyes.ATK = 3000
mock_blue_eyes.type = CardType.MONSTER
mock_blue_eyes.canAttack = True
mock_blue_eyes.effect = Mock(return_value=None) # A engine chama .effect()

mock_dark_magician = MagicMock(spec=Monster)
mock_dark_magician.name = "Dark Magician"
mock_dark_magician.ATK = 2500
mock_dark_magician.type = CardType.MONSTER
mock_dark_magician.canAttack = True
mock_dark_magician.effect = Mock(return_value=None)

mock_raigeki = MagicMock(spec=Card)
mock_raigeki.name = "Raigeki"
mock_raigeki.type = CardType.SPELL
mock_raigeki.effectDescription = "Destrói todos os monstros do oponente."
mock_raigeki.effect = Mock(return_value=None) # A engine chama .effect()

mock_trap_hole = MagicMock(spec=Card)
mock_trap_hole.name = "Buraco Armadilha"
mock_trap_hole.type = CardType.TRAP
mock_trap_hole.attackingMonster = None
mock_trap_hole.effect = Mock(return_value=None) # A engine chama .effect()

mock_magic_cylinder = MagicMock(spec=Card)
mock_magic_cylinder.name = "Cilindro Mágico"
mock_magic_cylinder.type = CardType.TRAP
mock_magic_cylinder.attackingMonster = None
mock_magic_cylinder.effect = Mock(return_value=None) # A engine chama .effect()


class TestYGOEngineFlow(unittest.TestCase):

    def setUp(self):
        """
        Configura um ambiente de teste limpo.
        Usa Mocks para Player e Network, mas simula o ESTADO real do Player.
        """
        # 1. Mock da Rede
        self.mock_network = Mock(spec=Network)
        self.mock_network.is_connected = True

        # 2. Mocks dos Jogadores (com 'spec' para garantir o contrato da classe)
        self.player1 = Mock(spec=Player, name="Jogador 1")
        self.player2 = Mock(spec=Player, name="Jogador 2")
        
        # 3. MELHORIA: Listas de Estado Reais
        # O mock do Player irá manipular estas listas, permitindo que a
        # engine funcione e que possamos testar o estado real.
        self.p1_state = {
            "life": 4000, "hand": [], "deck": [], "graveyard": [],
            "monstersInField": [], "monstersCount": 0,
            "spellsAndTrapsInField": [], "spellsAndTrapsCount": 0
        }
        self.p2_state = {
            "life": 4000, "hand": [], "deck": [], "graveyard": [],
            "monstersInField": [], "monstersCount": 0,
            "spellsAndTrapsInField": [], "spellsAndTrapsCount": 0
        }

        # Configura os Mocks para usarem as listas de estado
        for attr, value in self.p1_state.items():
            setattr(self.player1, attr, value)
        for attr, value in self.p2_state.items():
            setattr(self.player2, attr, value)

        # 4. MELHORIA: Mocks de Métodos com `side_effect`
        # Isso simula a lógica REAL do YGOplayer.py (decrementar contadores, mover cartas)
        
        def p1_drawCard():
            if not self.player1.deck: raise IndexError("Deck vazio")
            card = self.player1.deck.pop(0)
            self.player1.hand.append(card)
        self.player1.drawCard.side_effect = p1_drawCard

        def p1_monsterIntoGraveyard(monster):
            if monster in self.player1.monstersInField:
                self.player1.monstersInField.remove(monster)
                self.player1.graveyard.append(monster)
                self.player1.monstersCount -= 1 # Simula a lógica real
        self.player1.monsterIntoGraveyard.side_effect = p1_monsterIntoGraveyard

        def p1_spellTrapIntoGraveyard(spell):
            if spell in self.player1.spellsAndTrapsInField:
                self.player1.spellsAndTrapsInField.remove(spell)
                self.player1.spellsAndTrapsCount -= 1 # Simula a lógica real
            elif spell in self.player1.hand:
                self.player1.hand.remove(spell)
            self.player1.graveyard.append(spell)
        self.player1.spellTrapIntoGraveyard.side_effect = p1_spellTrapIntoGraveyard
        
        # --- Repete para o Player 2 ---
        def p2_drawCard():
            if not self.player2.deck: raise IndexError("Deck vazio")
            card = self.player2.deck.pop(0)
            self.player2.hand.append(card)
        self.player2.drawCard.side_effect = p2_drawCard
        
        def p2_monsterIntoGraveyard(monster):
            if monster in self.player2.monstersInField:
                self.player2.monstersInField.remove(monster)
                self.player2.graveyard.append(monster)
                self.player2.monstersCount -= 1 # Simula a lógica real
        self.player2.monsterIntoGraveyard.side_effect = p2_monsterIntoGraveyard

        def p2_spellTrapIntoGraveyard(spell):
            if spell in self.player2.spellsAndTrapsInField:
                self.player2.spellsAndTrapsInField.remove(spell)
                self.player2.spellsAndTrapsCount -= 1 # Simula a lógica real
            elif spell in self.player2.hand:
                self.player2.hand.remove(spell)
            self.player2.graveyard.append(spell)
        self.player2.spellTrapIntoGraveyard.side_effect = p2_spellTrapIntoGraveyard

        # 5. Instância da Engine
        self.engine = YGOengine(
            self.player1, self.player2, self.mock_network, is_host=True
        )

        # 6. Reseta mocks de cartas e estado da engine
        mock_blue_eyes.canAttack = True
        mock_dark_magician.canAttack = True
        
        self.mock_network.reset_mock()
        mock_raigeki.effect.reset_mock()
        mock_trap_hole.effect.reset_mock()
        mock_magic_cylinder.effect.reset_mock()
        self.engine.pending_attack = None

    ## --- Testes de Fluxo de Jogo e Estado ---

    def test_initial_state_as_host(self):
        self.assertEqual(self.engine.turnPlayer, self.player1)
        self.assertEqual(self.engine.nonTurnPlayer, self.player2)
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)

    def test_end_turn(self):
        mock_blue_eyes.canAttack = False
        self.player1.monstersInField.append(mock_blue_eyes)
        self.engine.summonThisTurn = True
        self.engine.currentPhase = GamePhase.END

        self.engine.endTurn()

        self.assertEqual(self.engine.turnPlayer, self.player2)
        self.assertEqual(self.engine.turnCount, 2)
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)
        self.assertFalse(self.engine.summonThisTurn)
        self.assertTrue(mock_blue_eyes.canAttack) # Resetado para o próximo turno
        self.mock_network.send_message.assert_called_with(
            MessageConstructor.passar_turno()
        )

    ## --- Testes de Ações (Main Phase) ---

    def test_draw_card_success(self):
        self.player1.deck.append(mock_dark_magician) # Adiciona ao deck
        
        result = self.engine.drawCard()

        self.assertTrue(result["success"])
        self.assertIn(mock_dark_magician, self.player1.hand)
        self.player1.drawCard.assert_called_once() # Valida que o mock foi chamado

    def test_draw_card_deck_empty(self):
        self.player1.deck = [] # Deck vazio
        self.player1.drawCard.side_effect = IndexError # Configura o mock para falhar
        
        result = self.engine.drawCard()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "DECK_EMPTY")

    def test_summon_monster_success(self):
        self.player1.hand.append(mock_blue_eyes)
        self.engine.summonThisTurn = False

        result = self.engine.summonMonster(self.player1, mock_blue_eyes)

        self.assertTrue(result["success"])
        self.assertIn(mock_blue_eyes, self.player1.monstersInField)
        self.assertNotIn(mock_blue_eyes, self.player1.hand)
        # Valida o estado simulado pelo side_effect
        self.assertEqual(self.player1.monstersCount, 1) 
        self.assertTrue(self.engine.summonThisTurn)
        self.mock_network.send_message.assert_called_once()

    # MELHORADO: Teste para `setCard` validando FacedownCard
    @patch('Components.YGOengine.FacedownCard') # Caminho do import dentro da YGOengine
    def test_set_card_success(self, mock_facedown_class):
        # Cria uma instância mock para a carta baixada
        mock_facedown_instance = MagicMock(spec=FacedownCard)
        mock_facedown_class.return_value = mock_facedown_instance

        self.player1.hand.append(mock_trap_hole)

        result = self.engine.setCard(self.player1, mock_trap_hole)

        self.assertTrue(result["success"])
        # Valida que FacedownCard foi chamado com a carta real
        mock_facedown_class.assert_called_with(mock_trap_hole)
        # Valida que a *instância* baixada foi para o campo
        self.assertIn(mock_facedown_instance, self.player1.spellsAndTrapsInField)
        self.assertNotIn(mock_trap_hole, self.player1.hand)
        # Valida o estado simulado
        self.assertEqual(self.player1.spellsAndTrapsCount, 1) 
        self.mock_network.send_message.assert_called_once()

    # MELHORADO: Teste para `activateSpell` validando .effect()
    def test_activate_spell_success(self):
        self.player1.hand.append(mock_raigeki)
        
        result = self.engine.activateSpell(self.player1, self.player2, mock_raigeki)

        self.assertTrue(result["success"])
        # Valida se o efeito (mockado) foi chamado
        mock_raigeki.effect.assert_called_with(self.player1, self.player2)
        # Valida se a carta foi para o cemitério (via side_effect mock)
        self.player1.spellTrapIntoGraveyard.assert_called_with(mock_raigeki)
        self.assertIn(mock_raigeki, self.player1.graveyard)
        self.assertNotIn(mock_raigeki, self.player1.hand)
        self.mock_network.send_message.assert_called_once()

    ## --- Testes de Batalha (Lado Atacante - P1) ---

    def test_declare_attack_sends_message(self):
        self.player1.monstersInField.append(mock_blue_eyes)
        self.player2.monstersInField.append(mock_dark_magician)
        
        self.engine.declareAttack(mock_blue_eyes, mock_dark_magician)

        self.assertEqual(self.engine.pending_attack, (mock_blue_eyes, mock_dark_magician))
        self.mock_network.send_message.assert_called_with(
            MessageConstructor.declarar_ataque(attacker_index=0, target_index=0)
        )

    def test_handle_attack_response_no_trap(self):
        # Setup: P1 (local) atacou P2
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField.append(mock_blue_eyes)
        self.player2.monstersInField.append(mock_dark_magician)
        self.player2.monstersCount = 1 # Estado inicial
        self.engine.pending_attack = (mock_blue_eyes, mock_dark_magician)
        
        payload = {"ativar": False, "tem_armadilha": False}
        
        self.engine.handle_attack_response(payload)

        # Verifica se o ataque foi resolvido
        self.assertIsNone(self.engine.pending_attack)
        self.assertFalse(mock_blue_eyes.canAttack)
        
        # Verifica estado (via _apply_battle_results_p1)
        self.assertEqual(self.player2.life, 3500) # P2 tomou 500
        self.assertEqual(self.player2.monstersCount, 0) # P2 perdeu monstro
        self.player2.monsterIntoGraveyard.assert_called_with(mock_dark_magician)
        
        # Verifica se o resultado foi enviado
        self.mock_network.send_message.assert_called_with(
            MessageConstructor.resultado_batalha(
                dano_atacante=0, dano_defensor=500,
                atacante_destruido=False, defensor_destruido=True,
                atacante_index=0, defensor_index=0
            )
        )

    # MELHORADO: Testa o patch para findTrapByName
    @patch('Components.cards.Traps.findTrapByName')
    def test_handle_opponent_activate_trap_magic_cylinder(self, mock_find_trap):
        # Setup: P1 (local) atacou, P2 (oponente) ativou armadilha
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField.append(mock_blue_eyes)
        self.player2.monstersInField.append(mock_dark_magician)
        self.engine.pending_attack = (mock_blue_eyes, mock_dark_magician)
        
        payload = {"card": {"name": "Cilindro Mágico"}}
        
        # Configura o mock da CARTA (Cilindro)
        # Simula o efeito real de Traps.py: Cilindro.effect()
        def reflect_damage(player_p2, opponent_p1):
            # 'player_p2' é quem ativou (P2), 'opponent_p1' é o P1
            opponent_p1.life -= mock_magic_cylinder.attackingMonster.ATK
        
        mock_magic_cylinder.effect.side_effect = reflect_damage
        # Configura o mock do BUSCADOR
        mock_find_trap.return_value = mock_magic_cylinder

        self.engine.handle_opponent_activate_trap(payload)

        # Verifica se o ataque foi resolvido
        self.assertIsNone(self.engine.pending_attack)
        self.assertFalse(mock_blue_eyes.canAttack)
        
        # Verifica se P1 (atacante) tomou o dano
        self.assertEqual(self.player1.life, 1000) # 4000 - 3000 ATK
        
        # Verifica se nenhum monstro foi destruído
        self.player1.monsterIntoGraveyard.assert_not_called()
        self.player2.monsterIntoGraveyard.assert_not_called()
        
        # Verifica se o resultado (da armadilha) foi enviado
        self.mock_network.send_message.assert_called_once()
        sent_msg = self.mock_network.send_message.call_args[0][0]
        self.assertEqual(sent_msg["tipo"], MessageType.RESULTADO_BATALHA)
        self.assertEqual(sent_msg["dano_atacante"], 3000) # Dano aplicado ao P1
        self.assertFalse(sent_msg["atacante_destruido"])


    ## --- Testes de Batalha (Lado Defensor - P2) ---

    # MELHORADO: Testa a verificação de armadilhas com FacedownCard
    def test_check_for_trap_response_finds_traps(self):
        # Simula FacedownCards no campo do defensor (P2)
        mock_fd_trap = MagicMock(spec=FacedownCard)
        mock_fd_trap.card = mock_trap_hole # A carta "real" dentro
        
        mock_fd_cylinder = MagicMock(spec=FacedownCard)
        mock_fd_cylinder.card = mock_magic_cylinder

        mock_fd_spell = MagicMock(spec=FacedownCard)
        mock_fd_spell.card = mock_raigeki # Uma magia baixada (não-armadilha)

        self.player2.spellsAndTrapsInField.extend([mock_fd_spell, mock_fd_trap, mock_fd_cylinder])
        
        # P2 é o defensor
        valid_traps = self.engine.checkForTrapResponse(self.player2, mock_blue_eyes)
        
        self.assertEqual(len(valid_traps), 2)
        self.assertIn(mock_trap_hole, valid_traps) # Retorna a carta real
        self.assertIn(mock_magic_cylinder, valid_traps)
        self.assertNotIn(mock_raigeki, valid_traps)
        
        # Verifica se a engine populou o monstro atacante na armadilha *interna*
        self.assertEqual(mock_trap_hole.attackingMonster, mock_blue_eyes)

    def test_handle_opponent_declare_attack_no_trap(self):
        # P1 (oponente) ataca P2 (local)
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField.append(mock_blue_eyes)
        self.player2.monstersInField.append(mock_dark_magician)
        
        mock_interface = Mock() # Mock da UI
        mock_interface.promptTrapActivation.return_value = None
        
        payload = {"attacker_index": 0, "target_index": 0}
        
        self.engine.handle_opponent_declare_attack(payload, mock_interface)
        
        # Não deve perguntar ao jogador se não há armadilhas válidas
        mock_interface.promptTrapActivation.assert_not_called()
        
        # Deve enviar uma resposta "não" para a rede
        self.mock_network.send_message.assert_called_with(
            MessageConstructor.ativar_armadilha(ativar=False, tem_armadilha=False)
        )

    @patch('Components.YGOengine.YGOengine.activateTrap') # Mocka a função de ativação
    def test_handle_opponent_declare_attack_activates_trap(self, mock_activate_trap):
        # P1 (oponente) ataca P2 (local)
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField.append(mock_blue_eyes)
        self.player2.monstersInField.append(mock_dark_magician)
        
        # Simula FacedownCard com a armadilha
        mock_fd_trap = MagicMock(spec=FacedownCard)
        mock_fd_trap.card = mock_trap_hole
        self.player2.spellsAndTrapsInField.append(mock_fd_trap)
        
        mock_interface = Mock()
        # Simula o jogador escolhendo ativar a armadilha
        mock_interface.promptTrapActivation.return_value = mock_trap_hole 
        
        payload = {"attacker_index": 0, "target_index": 0}
        
        self.engine.handle_opponent_declare_attack(payload, mock_interface)
            
        mock_interface.promptTrapActivation.assert_called_once()
        
        # Deve chamar a ativação da armadilha (P2 ativa contra P1)
        mock_activate_trap.assert_called_with(
            self.player2, self.player1, mock_trap_hole
        )
        # A 'activateTrap' (mockada) é que enviaria a msg, não este handler
        self.mock_network.send_message.assert_not_called()

    def test_handle_opponent_battle_result(self):
        # P1 (oponente) atacou, P2 (local) defendeu
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField.append(mock_blue_eyes)
        self.player2.monstersInField.append(mock_dark_magician)
        self.player2.monstersCount = 1 # Estado inicial
        mock_blue_eyes.canAttack = True 
        
        # Payload do resultado (P1 venceu)
        payload = {
            "dano_atacante": 0,    # Payload da rede
            "dano_defensor": 500,  # Payload da rede
            "atacante_destruido": False,
            "defensor_destruido": True,
            "atacante_idx": 0,
            "defensor_idx": 0
        }
        
        self.engine.handle_opponent_battle_result(payload)
        
        # Verifica se o estado local (P2) foi atualizado
        self.assertEqual(self.player2.life, 3500)
        self.player2.monsterIntoGraveyard.assert_called_with(mock_dark_magician)
        self.assertEqual(self.player2.monstersCount, 0) # Validado pelo side_effect

        # Verifica se o estado do oponente (P1) também foi atualizado
        self.player1.monsterIntoGraveyard.assert_not_called()
        self.assertFalse(mock_blue_eyes.canAttack) # Marcou como atacado


if __name__ == '__main__':
    unittest.main()