from enum import Enum, auto


# Enum para definir os estados do jogo
class GamePhase(Enum):
    DRAW = auto()
    MAIN_1 = auto()
    BATTLE = auto()
    END = auto()
