import unittest
from unittest.mock import Mock, patch, MagicMock

# Importe as classes e enums do seu projeto
from Components.YGOengine import YGOengine
from Components.YGOgamePhase import GamePhase

# Como os testes não precisam da implementação real dessas classes,
# podemos usar Mocks com 'spec=True'.
# Se este arquivo de teste estiver em um diretório diferente,
# você pode precisar ajustar o 'sys.path' ou simplesmente
# criar Mocks genéricos sem 'spec'.

# Para este exemplo, vamos supor que podemos importar as definições
# para que o 'spec' funcione corretamente.
from Components.YGOplayer import Player
from Components.cards.Monsters import Monster
from Components.cards.YGOcards import Card, CardType
from Communication.network import Network
from Communication.messages_protocol import MessageType

# --- Mocks para as Cartas ---
# Criamos instâncias de Mock para simular cartas reais.
# Usamos MagicMock para que atributos como ATK possam ser definidos
# e comparados (ex: 3000 > 2500)

# Monstro Atacante
mock_blue_eyes = MagicMock(spec=Monster)
mock_blue_eyes.name = "Blue-Eyes White Dragon"
mock_blue_eyes.ATK = 3000
mock_blue_eyes.type = CardType.MONSTER
mock_blue_eyes.canAttack = True

# Monstro Alvo
mock_dark_magician = MagicMock(spec=Monster)
mock_dark_magician.name = "Dark Magician"
mock_dark_magician.ATK = 2500
mock_dark_magician.type = CardType.MONSTER
mock_dark_magician.canAttack = True

# Magia
mock_raigeki = MagicMock(spec=Card)
mock_raigeki.name = "Raigeki"
mock_raigeki.type = CardType.SPELL
mock_raigeki.effectDescription = "Destrói todos os monstros do oponente."

# Armadilha
mock_trap_hole = MagicMock(spec=Card)
mock_trap_hole.name = "Buraco Armadilha"
mock_trap_hole.type = CardType.TRAP
mock_trap_hole.attackingMonster = None # O engine irá popular isso

# Armadilha de Negação de Ataque
mock_magic_cylinder = MagicMock(spec=Card)
mock_magic_cylinder.name = "Cilindro Mágico"
mock_magic_cylinder.type = CardType.TRAP
mock_magic_cylinder.attackingMonster = None


class TestYGOEngine(unittest.TestCase):

    def setUp(self):
        """
        Configura um ambiente de teste limpo antes de cada teste.
        """
        # 1. Mock da Rede
        self.mock_network = Mock(spec=Network)
        self.mock_network.is_connected = True
        self.mock_network.get_message.return_value = None # Padrão é não receber nada

        # 2. Mocks dos Jogadores
        # Usamos listas reais em vez de mocks de lista para facilitar
        # a verificação de "card in player.hand".
        self.player1 = Mock(spec=Player, name="Jogador 1")
        self.player1.life = 4000
        self.player1.hand = []
        self.player1.deck = []
        self.player1.monstersInField = []
        self.player1.spellsAndTrapsInField = []
        self.player1.graveyard = []
        self.player1.monstersCount = 0
        self.player1.spellsAndTrapsCount = 0

        self.player2 = Mock(spec=Player, name="Jogador 2")
        self.player2.life = 4000
        self.player2.hand = []
        self.player2.deck = []
        self.player2.monstersInField = []
        self.player2.spellsAndTrapsInField = []
        self.player2.graveyard = []
        self.player2.monstersCount = 0
        self.player2.spellsAndTrapsCount = 0
        
        # 3. Mocks de Métodos dos Jogadores
        # Simulamos o que os métodos do Jogador fariam com suas listas
        def p1_draw():
            card = self.player1.deck.pop(0)
            self.player1.hand.append(card)
        self.player1.drawCard.side_effect = p1_draw

        def p1_monster_to_gy(monster):
            if monster in self.player1.monstersInField:
                self.player1.monstersInField.remove(monster)
                self.player1.graveyard.append(monster)
                self.player1.monstersCount -= 1
        self.player1.monsterIntoGraveyard.side_effect = p1_monster_to_gy
        
        def p1_spell_to_gy(spell):
            if spell in self.player1.spellsAndTrapsInField:
                self.player1.spellsAndTrapsInField.remove(spell)
            self.player1.graveyard.append(spell)
            if self.player1.spellsAndTrapsCount > 0:
                 self.player1.spellsAndTrapsCount -= 1
        self.player1.spellTrapIntoGraveyard.side_effect = p1_spell_to_gy


        def p2_monster_to_gy(monster):
            if monster in self.player2.monstersInField:
                self.player2.monstersInField.remove(monster)
                self.player2.graveyard.append(monster)
                self.player2.monstersCount -= 1
        self.player2.monsterIntoGraveyard.side_effect = p2_monster_to_gy

        # 4. Instância da Engine (SUT - System Under Test)
        # O P1 é o host e começa o turno.
        self.engine = YGOengine(
            self.player1, self.player2, self.mock_network, is_host=True
        )

        # 5. Resetar mocks de cartas (importante para 'canAttack')
        mock_blue_eyes.canAttack = True
        mock_dark_magician.canAttack = True
        
        # Resetar contagens de mock call
        self.mock_network.reset_mock()
        mock_raigeki.apply_effect.reset_mock()
        mock_trap_hole.apply_effect.reset_mock()
        mock_magic_cylinder.apply_effect.reset_mock()


    ## --- Testes de Fluxo de Jogo e Estado ---

    def test_initial_state_as_host(self):
        self.assertEqual(self.engine.turnPlayer, self.player1)
        self.assertEqual(self.engine.nonTurnPlayer, self.player2)
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)
        self.assertEqual(self.engine.turnCount, 1)
        self.assertFalse(self.engine.summonThisTurn)

    def test_initial_state_as_guest(self):
        # Cria uma nova engine para este teste
        guest_engine = YGOengine(
            self.player1, self.player2, self.mock_network, is_host=False
        )
        self.assertEqual(guest_engine.turnPlayer, self.player2) # Oponente (host) começa
        self.assertEqual(guest_engine.nonTurnPlayer, self.player1)
        self.assertEqual(guest_engine.currentPhase, GamePhase.DRAW)

    def test_advance_to_next_phase(self):
        self.engine.currentPhase = GamePhase.DRAW
        self.engine.advanceToNextPhase()
        self.assertEqual(self.engine.currentPhase, GamePhase.MAIN_1)

        self.engine.advanceToNextPhase()
        self.assertEqual(self.engine.currentPhase, GamePhase.BATTLE)

        self.engine.advanceToNextPhase()
        self.assertEqual(self.engine.currentPhase, GamePhase.END)
        
        # Deve ter notificado a rede 3 vezes
        self.assertEqual(self.mock_network.send_message.call_count, 3)

    def test_end_turn(self):
        # Configura um monstro que atacou
        mock_blue_eyes.canAttack = False
        self.player1.monstersInField = [mock_blue_eyes]
        self.engine.summonThisTurn = True
        self.engine.currentPhase = GamePhase.END
        self.engine.turnCount = 1

        self.engine.endTurn()

        # Verifica se os jogadores trocaram
        self.assertEqual(self.engine.turnPlayer, self.player2)
        self.assertEqual(self.engine.nonTurnPlayer, self.player1)
        
        # Verifica se o estado do turno foi resetado
        self.assertEqual(self.engine.turnCount, 2)
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)
        self.assertFalse(self.engine.summonThisTurn)
        
        # Verifica se o monstro do P1 pode atacar no próximo turno dele
        self.assertTrue(mock_blue_eyes.canAttack)
        
        # Verifica se a rede foi notificada
        self.mock_network.send_message.assert_called_once()

    ## --- Testes de Ações do Jogador (Main Phase) ---

    def test_draw_card_success(self):
        self.player1.deck = [mock_dark_magician]
        self.player1.hand = []
        
        result = self.engine.drawCard()

        self.assertTrue(result["success"])
        self.assertIn(mock_dark_magician, self.player1.hand)
        self.assertEqual(len(self.player1.deck), 0)
        self.player1.drawCard.assert_called_once() # Verifica se o método do player foi chamado

    def test_draw_card_deck_empty(self):
        self.player1.deck = []
        
        result = self.engine.drawCard()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "DECK_EMPTY")

    def test_summon_monster_success(self):
        self.player1.hand = [mock_blue_eyes]
        self.player1.monstersInField = []
        self.player1.monstersCount = 0
        self.engine.summonThisTurn = False

        result = self.engine.summonMonster(self.player1, mock_blue_eyes)

        self.assertTrue(result["success"])
        self.assertIn(mock_blue_eyes, self.player1.monstersInField)
        self.assertNotIn(mock_blue_eyes, self.player1.hand)
        self.assertEqual(self.player1.monstersCount, 1)
        self.assertTrue(self.engine.summonThisTurn)
        self.mock_network.send_message.assert_called_once()

    def test_summon_monster_fail_zone_full(self):
        self.player1.monstersCount = 3
        result = self.engine.summonMonster(self.player1, mock_blue_eyes)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "MONSTER_ZONE_FULL")

    def test_summon_monster_fail_already_summoned(self):
        self.engine.summonThisTurn = True
        result = self.engine.summonMonster(self.player1, mock_blue_eyes)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "VOCE_JA_INVOCOU_NESTE_TURNO")

    def test_set_card_success(self):
        self.player1.hand = [mock_trap_hole]
        self.player1.spellsAndTrapsInField = []
        self.player1.spellsAndTrapsCount = 0

        result = self.engine.setCard(self.player1, mock_trap_hole)

        self.assertTrue(result["success"])
        self.assertIn(mock_trap_hole, self.player1.spellsAndTrapsInField)
        self.assertNotIn(mock_trap_hole, self.player1.hand)
        self.assertEqual(self.player1.spellsAndTrapsCount, 1)
        self.mock_network.send_message.assert_called_once()

    def test_set_card_fail_zone_full(self):
        self.player1.spellsAndTrapsCount = 3
        result = self.engine.setCard(self.player1, mock_trap_hole)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "SPELL_TRAP_ZONE_FULL")

    @patch('YGOengine.MessageConstructor') # Mocka o construtor de mensagens
    def test_activate_spell_success(self, mock_msg_constructor):
        self.player1.hand = [mock_raigeki]
        self.player1.graveyard = []
        # Simula o 'index()' da lista real
        
        result = self.engine.activateSpell(self.player1, self.player2, mock_raigeki)

        self.assertTrue(result["success"])
        # Verifica se o efeito foi aplicado
        mock_raigeki.apply_effect.assert_called_with(self.player1, self.player2)
        # Verifica se a carta foi para o cemitério
        self.assertNotIn(mock_raigeki, self.player1.hand)
        self.player1.spellTrapIntoGraveyard.assert_called_with(mock_raigeki)
        # Verifica se a rede foi notificada
        self.mock_network.send_message.assert_called_once()
        mock_msg_constructor.ativar_magia.assert_called_once()


    ## --- Testes de Ações do Jogador (Battle Phase) ---

    def test_damage_calc_scenarios(self):
        # 1. Atacante vence
        res_atk_wins = self.engine.damageCalc(mock_blue_eyes, mock_dark_magician)
        self.assertEqual(res_atk_wins["playerDamage"], 0)
        self.assertEqual(res_atk_wins["opponentDamage"], 500) # 3000 - 2500
        self.assertTrue(res_atk_wins["targetDestroyed"])
        self.assertFalse(res_atk_wins["attackerDestroyed"])

        # 2. Defensor vence
        res_def_wins = self.engine.damageCalc(mock_dark_magician, mock_blue_eyes)
        self.assertEqual(res_def_wins["playerDamage"], 500) # abs(2500 - 3000)
        self.assertEqual(res_def_wins["opponentDamage"], 0)
        self.assertFalse(res_def_wins["targetDestroyed"])
        self.assertTrue(res_def_wins["attackerDestroyed"])

        # 3. Empate
        res_tie = self.engine.damageCalc(mock_blue_eyes, mock_blue_eyes)
        self.assertEqual(res_tie["playerDamage"], 0)
        self.assertEqual(res_tie["opponentDamage"], 0)
        self.assertTrue(res_tie["targetDestroyed"])
        self.assertTrue(res_tie["attackerDestroyed"])
        
        # 4. Ataque Direto
        res_direct = self.engine.damageCalc(mock_blue_eyes, None)
        self.assertEqual(res_direct["playerDamage"], 0)
        self.assertEqual(res_direct["opponentDamage"], 3000) # ATK do Blue-Eyes
        self.assertFalse(res_direct["targetDestroyed"])
        self.assertFalse(res_direct["attackerDestroyed"])

    def test_resolve_attack_no_trap_response(self):
        self.player1.monstersInField = [mock_blue_eyes]
        self.player2.monstersInField = [mock_dark_magician]
        self.player1.life = 4000
        self.player2.life = 4000
        
        # Simula o oponente respondendo "não" à armadilha
        self.mock_network.get_message.return_value = {
            "tipo": MessageType.ATIVAR_ARMADILHA,
            "ativar": False
        }
        
        result = self.engine.resolveAttack(self.player1, self.player2, mock_blue_eyes, mock_dark_magician)

        # Verifica o estado do jogo
        self.assertFalse(mock_blue_eyes.canAttack) # Marcou como atacado
        self.assertEqual(self.player1.life, 4000)
        self.assertEqual(self.player2.life, 3500) # Perdeu 500 LP
        
        # Verifica se o monstro correto foi para o cemitério
        self.player2.monsterIntoGraveyard.assert_called_with(mock_dark_magician)
        self.player1.monsterIntoGraveyard.assert_not_called()
        self.assertNotIn(mock_dark_magician, self.player2.monstersInField)

        # Verifica comunicação de rede (1. Declarar, 2. Resultado)
        self.assertEqual(self.mock_network.send_message.call_count, 2)
        
        # Verifica o resultado retornado
        self.assertEqual(result["opponentDamage"], 500)
        self.assertTrue(result["targetDestroyed"])

    def test_resolve_attack_with_trap_response_magic_cylinder(self):
        self.player1.monstersInField = [mock_blue_eyes]
        self.player2.monstersInField = [mock_dark_magician]
        self.player1.life = 4000
        
        # Simula o oponente respondendo "sim" com "Cilindro Mágico"
        self.mock_network.get_message.return_value = {
            "tipo": MessageType.ATIVAR_ARMADILHA,
            "ativar": True,
            "trap_name": "Cilindro Mágico"
        }
        
        result = self.engine.resolveAttack(self.player1, self.player2, mock_blue_eyes, mock_dark_magician)

        # Verifica o estado do jogo
        self.assertFalse(mock_blue_eyes.canAttack) # Marcou como atacado
        self.assertEqual(self.player1.life, 1000) # Tomou 3000 de dano
        
        # Verifica se nenhum monstro foi destruído
        self.player2.monsterIntoGraveyard.assert_not_called()
        self.player1.monsterIntoGraveyard.assert_not_called()

        # Verifica comunicação de rede (Apenas 1. Declarar)
        # A resposta da armadilha é enviada pelo *oponente* (simulado aqui)
        self.assertEqual(self.mock_network.send_message.call_count, 1)
        
        # Verifica o resultado retornado
        self.assertTrue(result["attack_negated"])
        self.assertEqual(result["trap_name"], "Cilindro Mágico")

    def test_check_for_trap_response_finds_traps(self):
        self.player2.spellsAndTrapsInField = [mock_raigeki, mock_trap_hole, mock_magic_cylinder]
        
        # O defensor é o player2
        valid_traps = self.engine.checkForTrapResponse(self.player2, mock_blue_eyes)
        
        self.assertEqual(len(valid_traps), 2)
        self.assertIn(mock_trap_hole, valid_traps)
        self.assertIn(mock_magic_cylinder, valid_traps)
        self.assertNotIn(mock_raigeki, valid_traps) # Não é armadilha
        
        # Verifica se o engine populou o monstro atacante na armadilha
        self.assertEqual(mock_trap_hole.attackingMonster, mock_blue_eyes)
        self.assertEqual(mock_magic_cylinder.attackingMonster, mock_blue_eyes)


    ## --- Testes de Handlers de Rede (Mensagens Recebidas) ---
    
    def test_handle_opponent_pass_turn(self):
        # Simula o oponente (P1) terminando o turno
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.engine.currentPhase = GamePhase.END
        
        self.engine.handle_opponent_pass_turn()

        # Agora é o turno do P2 (local)
        self.assertEqual(self.engine.turnPlayer, self.player2)
        self.assertEqual(self.engine.nonTurnPlayer, self.player1)
        self.assertEqual(self.engine.currentPhase, GamePhase.DRAW)
        self.assertEqual(self.engine.turnCount, 2)

    @patch('YGOengine.Monster') # Mocka a classe Monstro
    def test_handle_opponent_summon_monster(self, mock_monster_class):
        # Simula o recebimento de uma invocação do P1 (oponente)
        self.engine.turnPlayer = self.player1
        self.player1.monstersInField = []
        self.player1.monstersCount = 0
        
        # O payload recebido
        payload = {
            "card": {"name": "Opponent Monster", "ATK": 1000, "type": "MONSTER"}
        }
        
        # Configura o mock da classe para retornar um mock de instância
        mock_opponent_monster = MagicMock()
        mock_monster_class.return_value = mock_opponent_monster
        
        self.engine.handle_opponent_summon_monster(payload)

        # Verifica se o construtor de Monstro foi chamado com os dados corretos
        mock_monster_class.assert_called_with(
            name="Opponent Monster",
            ATK=1000,
            type=CardType.MONSTER
        )
        # Verifica se o monstro "dummy" foi adicionado ao campo do oponente (P1)
        self.assertIn(mock_opponent_monster, self.player1.monstersInField)
        self.assertEqual(self.player1.monstersCount, 1)

    def test_handle_opponent_activate_spell_raigeki(self):
        # O P1 (oponente) ativa Raigeki
        # O P2 (local) tem um monstro
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player2.monstersInField = [mock_dark_magician]
        
        payload = {"card": {"name": "Raigeki"}}
        
        self.engine.handle_opponent_activate_spell(payload)
        
        # Verifica se o monstro do P2 (local) foi para o cemitério
        self.player2.monsterIntoGraveyard.assert_called_with(mock_dark_magician)
        self.assertNotIn(mock_dark_magician, self.player2.monstersInField)

    def test_handle_opponent_declare_attack_local_has_no_trap(self):
        # P1 (oponente) ataca P2 (local)
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField = [mock_blue_eyes]
        self.player2.monstersInField = [mock_dark_magician]
        self.player2.spellsAndTrapsInField = [] # P2 não tem armadilhas
        
        # Mock da interface que pergunta ao jogador
        mock_interface = Mock()
        mock_interface.promptTrapActivation.return_value = None # Jogador escolhe "não"
        
        payload = {"attacker_index": 0, "target_index": 0}
        
        self.engine.handle_opponent_declare_attack(payload, mock_interface)
        
        # Não deve perguntar ao jogador se não há armadilhas válidas
        mock_interface.promptTrapActivation.assert_not_called()
        
        # Deve enviar uma resposta "não" para a rede
        self.mock_network.send_message.assert_called_once()
        # (Opcional) Verificar o conteúdo da mensagem
        args, kwargs = self.mock_network.send_message.call_args
        sent_message = args[0]
        self.assertEqual(sent_message['tipo'], MessageType.ATIVAR_ARMADILHA)
        self.assertFalse(sent_message['payload']['ativar'])
        self.assertFalse(sent_message['payload']['tem_armadilha'])

    def test_handle_opponent_declare_attack_local_activates_trap(self):
        # P1 (oponente) ataca P2 (local)
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField = [mock_blue_eyes]
        self.player2.monstersInField = [mock_dark_magician]
        self.player2.spellsAndTrapsInField = [mock_trap_hole] # P2 tem uma armadilha
        
        # Mock da interface que pergunta ao jogador
        mock_interface = Mock()
        # Jogador escolhe "sim", ativar a armadilha
        mock_interface.promptTrapActivation.return_value = mock_trap_hole 
        
        payload = {"attacker_index": 0, "target_index": 0}
        
        # Patch a função 'activateTrap' para verificar se ela é chamada
        # sem executar sua lógica interna (que enviaria outra msg de rede)
        with patch.object(self.engine, 'activateTrap') as mock_activate_trap:
            self.engine.handle_opponent_declare_attack(payload, mock_interface)
            
            # Deve perguntar ao jogador
            mock_interface.promptTrapActivation.assert_called_once()
            
            # Deve chamar a ativação da armadilha localmente
            mock_activate_trap.assert_called_with(
                self.player2, self.player1, mock_trap_hole
            )
            
            # A *própria* activateTrap enviaria a mensagem,
            # então a send_message *deste* método não deve ser chamada.
            self.mock_network.send_message.assert_not_called()

    def test_handle_opponent_battle_result(self):
        # P1 (oponente) foi o atacante
        # P2 (local) foi o defensor
        self.engine.turnPlayer = self.player1
        self.engine.nonTurnPlayer = self.player2
        self.player1.monstersInField = [mock_blue_eyes]
        self.player2.monstersInField = [mock_dark_magician]
        self.player1.life = 4000
        self.player2.life = 4000
        mock_blue_eyes.canAttack = True # Estava apto a atacar
        
        # Payload do resultado (P1 venceu, P2 tomou dano e perdeu monstro)
        payload = {
            "dano_ao_atacante": 0,
            "dano_ao_defensor": 500,
            "monstro_atacante_destruido": False,
            "monstro_defensor_destruido": True,
            "atacante_idx": 0,
            "defensor_idx": 0
        }
        
        self.engine.handle_opponent_battle_result(payload)
        
        # Verifica se o estado local (P2) foi atualizado
        self.assertEqual(self.player2.life, 3500)
        self.player2.monsterIntoGraveyard.assert_called_with(mock_dark_magician)
        
        # Verifica se o estado do oponente (P1) foi atualizado
        self.assertEqual(self.player1.life, 4000)
        self.player1.monsterIntoGraveyard.assert_not_called()
        
        # Verifica se o monstro do oponente (P1) foi marcado como "já atacou"
        self.assertFalse(mock_blue_eyes.canAttack)

if __name__ == '__main__':
    unittest.main()