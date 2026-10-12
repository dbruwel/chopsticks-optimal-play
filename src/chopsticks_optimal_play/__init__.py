"""Small Chopsticks analysis package.

This project is a relaxed exploration of optimal play in Chopsticks, with the
core state logic and graph search living in the package instead of a notebook.
"""

from .bot import OptimalBot
from .game import (
    ChopsticksGame,
    build_adjacency_matrix,
    compute_attractor,
    compute_player_0_attractor,
)

__all__ = [
    "ChopsticksGame",
    "OptimalBot",
    "build_adjacency_matrix",
    "compute_attractor",
    "compute_player_0_attractor",
]
