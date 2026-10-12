from __future__ import annotations

from collections import deque
from collections.abc import Sequence

import numpy as np

State = tuple[tuple[int, int], tuple[int, int]]


class ChopsticksGame:
    """Represent a position in Chopsticks and the player whose turn it is.

    Parameters
    ----------
    state : tuple[tuple[int, int], tuple[int, int]], optional
        The state of the two players' hands, by default ``((1, 1), (1, 1))``.
    player : int, optional
        The index of the player whose turn it is, by default ``0``.

    Notes
    -----
    Any hand value greater than or equal to 5 is treated as 0, matching the
    original notebook logic and the standard Chopsticks "burst" rule.
    """

    def __init__(self, state=((1, 1), (1, 1)), player: int = 0):
        self.player = int(player)
        self.state = self.rectify_state(state)

    @staticmethod
    def compare_player_states(state1, state2):
        """Return whether two player hands are the same up to ordering."""
        return frozenset(state1) == frozenset(state2)

    def compare_states(self, state1, state2):
        """Return whether two full states are equal for this game."""
        return self.compare_player_states(
            state1[0], state2[0]
        ) and self.compare_player_states(state1[1], state2[1])

    @staticmethod
    def rectify_state(state: Sequence[Sequence[int]]) -> State:
        """Normalize a game state by resetting any hand of 5 or more to 0."""
        if len(state) != 2 or len(state[0]) != 2 or len(state[1]) != 2:
            raise ValueError("state must be a pair of two-handed tuples")

        def zero(value: int) -> int:
            return value if value < 5 else 0

        return (
            (zero(int(state[0][0])), zero(int(state[0][1]))),
            (zero(int(state[1][0])), zero(int(state[1][1]))),
        )

    def __eq__(self, other):
        return (
            self.compare_states(self.state, other.state) and self.player == other.player
        )

    def __repr__(self):
        return f"ChopsticksGame(state={self.state}, player={self.player})"

    def __hash__(self):
        return hash((frozenset(self.state[0]), frozenset(self.state[1]), self.player))

    def player_0_win(self):
        """Return whether player 0 has eliminated the other player."""
        return self.state[1] == (0, 0)

    def player_1_win(self):
        """Return whether player 1 has eliminated the other player."""
        return self.state[0] == (0, 0)

    def is_terminal(self):
        """Return whether either player has been knocked out."""
        return self.player_0_win() or self.player_1_win()

    def enumerate_states(self):
        """Generate legal next states from the current position.

        Rules used here:

        * Attack: tap one of the opponent's live hands with one of your live
          hands. The tapped hand gains the attacker's value, and dies on 5+.
        * Split: redistribute your total across your two hands, keeping both
          at 4 or below. A split that is just the same hands swapped around
          is not a move. Splitting can revive a dead hand.
        * Once either player is out, the game is over and there are no moves.

        Returns
        -------
        list[State]
            Every distinct legal attack or split available to the active player.
        """
        if self.is_terminal():
            return []

        player = self.player
        other = 1 - player
        mine = self.state[player]
        theirs = self.state[other]

        def zero(value: int) -> int:
            return value if value < 5 else 0

        # Hands are unordered, so only try each distinct live value once.
        attackers = sorted({value for value in mine if value})
        targets = [i for i in (0, 1) if theirs[i]]
        if theirs[0] == theirs[1]:
            targets = targets[:1]

        attack_other_states = []
        for attacker in attackers:
            for i in targets:
                hands = list(theirs)
                hands[i] = zero(theirs[i] + attacker)
                attack_other_states.append(tuple(hands))

        total = mine[0] + mine[1]
        switch_player_states = [
            (switch, total - switch)
            for switch in range(max(total - 4, 0), total // 2 + 1)
        ]

        if player == 0:
            attack_states = [(mine, attack) for attack in attack_other_states]
            switch_states = [(switch, theirs) for switch in switch_player_states]
        else:
            attack_states = [(attack, mine) for attack in attack_other_states]
            switch_states = [(theirs, switch) for switch in switch_player_states]

        filtered_switch_states = [
            state
            for state in switch_states
            if not self.compare_states(state, self.state)
        ]

        return attack_states + filtered_switch_states

    def get_neighbors(self):
        """Generate the accessible successor states for this game position."""
        states = self.enumerate_states()
        return [self.__class__(state, 1 - self.player) for state in states]


def build_adjacency_matrix(start_node: ChopsticksGame):
    """Build the game graph and return its adjacency matrix.

    Parameters
    ----------
    start_node : ChopsticksGame
        The initial position used as the root for the breadth-first search.

    Returns
    -------
    tuple[numpy.ndarray, list[ChopsticksGame]]
        The adjacency matrix and the node list in index order.
    """
    node_to_index = {}
    index_to_node = []
    adjacency = {}
    queue = deque([start_node])
    visited = set()

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        if current not in node_to_index:
            node_to_index[current] = len(index_to_node)
            index_to_node.append(current)

        current_index = node_to_index[current]
        adjacency.setdefault(current_index, set())

        for neighbor in current.get_neighbors():
            if neighbor not in node_to_index:
                node_to_index[neighbor] = len(index_to_node)
                index_to_node.append(neighbor)
            neighbor_index = node_to_index[neighbor]
            adjacency.setdefault(current_index, set()).add(neighbor_index)
            queue.append(neighbor)

    n = len(index_to_node)
    matrix = np.zeros((n, n), dtype=int)
    for i, neighbors in adjacency.items():
        for j in neighbors:
            matrix[i, j] = 1

    return matrix, index_to_node


def compute_attractor(adj_matrix, index_to_node, player: int = 0):
    """Compute the attractor set for ``player``, layer by layer.

    A state is in layer ``k`` if ``player`` can force a win from it in at most
    ``k`` moves (counting both players' moves), and not in fewer.

    Parameters
    ----------
    adj_matrix : numpy.ndarray
        The adjacency matrix of the game graph.
    index_to_node : list[ChopsticksGame]
        The node list associated with ``adj_matrix``.
    player : int, optional
        The player trying to force a win, by default ``0``.

    Returns
    -------
    dict[int, int]
        Maps each node index in the attractor to its layer.
    """
    n = len(index_to_node)
    successors = [set(np.where(adj_matrix[i] == 1)[0]) for i in range(n)]

    def wins(node: ChopsticksGame) -> bool:
        return node.player_0_win() if player == 0 else node.player_1_win()

    layers = {i: 0 for i, node in enumerate(index_to_node) if wins(node)}
    layer = 0

    while True:
        layer += 1
        new_states = set()
        for state_index in range(n):
            if state_index in layers:
                continue

            node = index_to_node[state_index]
            successor_indices = successors[state_index]

            if node.player == player:
                if any(target in layers for target in successor_indices):
                    new_states.add(state_index)
            else:
                if successor_indices and all(
                    target in layers for target in successor_indices
                ):
                    new_states.add(state_index)

        if not new_states:
            return layers
        layers.update({state_index: layer for state_index in new_states})


def compute_player_0_attractor(adj_matrix, index_to_node):
    """Compute the attractor set for player 0 under the game graph.

    Parameters
    ----------
    adj_matrix : numpy.ndarray
        The adjacency matrix of the game graph.
    index_to_node : list[ChopsticksGame]
        The node list associated with ``adj_matrix``.

    Returns
    -------
    set[int]
        Indices of nodes in the player-0 attractor set.
    """
    return set(compute_attractor(adj_matrix, index_to_node, player=0))
