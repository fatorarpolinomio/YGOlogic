from Components.cards.Monsters import Monster
import Components.cards.Spells as Spells
import Components.cards.Traps as Traps
from Components.cards.YGOcards import CardType


# Criando deck padrão para cada jogador (sim, ambos terão o mesmo deck, isso aqui é um ep de redes meu deus)
standardDeck = [
    # Monsters ---> Percebi que precisamos colocar o nível das cartas de monstros
    Monster("Mago Negro", 2500, CardType.MONSTER, ""),
    Monster("Dragão Negro de Olhos Vermelhos", 2400, CardType.MONSTER, ""),
    Monster("Dragão Branco de Olhos Azuis", 3000, CardType.MONSTER, ""),
    Monster("Dragão Filhote", 1200, CardType.MONSTER, ""),  # nível 3 (arrumar dps)
    Monster("Guardião Celta", 1400, CardType.MONSTER, ""),  # nível 4
    Monster("Dragão do Brilho", 1900, CardType.MONSTER, ""),  # nível 4
    Monster("Elfa Mística", 800, CardType.MONSTER, ""),  # nível 4
    Monster("Kaiser Violento", 1800, CardType.MONSTER, ""),  # nível 5
    Monster("Caveira Invocada", 2500, CardType.MONSTER, ""),  # nível 6
    # Magic
    Spells.Raigeki(),
    Spells.DianKeto(),
    Spells.PoteDaGanancia(),
    Spells.TempestadePesada(),
    # Traps
    Traps.MirrorForce(),
    Traps.Cilindro(),
    Traps.BuracoArmadilha(),
    Traps.Aparelho(),
    Traps.NegateAttack(),
]
