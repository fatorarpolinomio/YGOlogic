from __future__ import annotations
import typing
from typing import override

from .YGOcards import Card, CardType

if typing.TYPE_CHECKING:
    from ..YGOplayer import Player


class FacedownCard(Card):
    """Representa uma carta genérica virada para baixo."""

    def __init__(self):
        super().__init__(
            name="Carta Baixada",
            ATK=None,
            type=CardType.SPELL,  # O tipo real é desconhecido, mas o campo 'type' é obrigatório.
            effect="Esta carta está virada para baixo.",
        )

    @override
    def effect(self, player: Player, opponent: Player):
        # Uma carta virada para baixo não tem efeito até ser virada para cima.
        pass
