from __future__ import annotations

import numpy as np

from .game import ChopsticksGame, build_adjacency_matrix, compute_attractor


class OptimalBot:
    """A Chopsticks player that uses the solved game to pick its moves.

    When it can force a win it takes the fastest one. When it can't, it stays in
    the draw region if it can, and otherwise drags the game out as long as
    possible, hoping the other player slips up.
    """

    def __init__(self, start: ChopsticksGame | None = None):
        self.start = start or ChopsticksGame()
        adjacency, self.nodes = build_adjacency_matrix(self.start)
        self.index = {node: i for i, node in enumerate(self.nodes)}
        self.successors = [list(np.flatnonzero(row)) for row in adjacency]
        self.attractors = {
            player: compute_attractor(adjacency, self.nodes, player=player)
            for player in (0, 1)
        }

    def outcome(self, game: ChopsticksGame):
        """Return who can force a win from ``game`` (0 or 1), or None for a draw."""
        i = self.index[game]
        for player in (0, 1):
            if i in self.attractors[player]:
                return player
        return None

    def moves_to_win(self, game: ChopsticksGame):
        """Return how many moves the winner needs from ``game``, or None for a draw."""
        winner = self.outcome(game)
        if winner is None:
            return None
        return self.attractors[winner][self.index[game]]

    def choose(self, game: ChopsticksGame) -> ChopsticksGame:
        """Return the position the bot moves to from ``game``."""
        i = self.index[game]
        if not self.successors[i]:
            raise ValueError("the game is already over")

        mine = self.attractors[game.player]
        theirs = self.attractors[1 - game.player]

        if i in mine:
            target = min((j for j in self.successors[i] if j in mine), key=mine.get)
        else:
            safe = [j for j in self.successors[i] if j not in theirs]
            target = safe[0] if safe else max(self.successors[i], key=theirs.get)

        # Return the neighbour built from ``game`` so left/right stay where they were.
        return next(n for n in game.get_neighbors() if n == self.nodes[target])
