from chopsticks_optimal_play import (
    OptimalBot,
    ChopsticksGame,
    build_adjacency_matrix,
    compute_attractor,
    compute_player_0_attractor,
)


def test_rectify_state_resets_large_hands_to_zero():
    game = ChopsticksGame(((7, 1), (3, 5)))
    assert game.state == ((0, 1), (3, 0))


def test_neighbors_are_generated_for_valid_moves():
    game = ChopsticksGame(((1, 1), (1, 1)))
    neighbors = game.get_neighbors()
    assert neighbors
    assert all(isinstance(neighbor, ChopsticksGame) for neighbor in neighbors)


def test_analysis_reports_a_nonempty_player_zero_attractor():
    adjacency_matrix, index_to_node = build_adjacency_matrix(ChopsticksGame())
    attractor = compute_player_0_attractor(adjacency_matrix, index_to_node)
    states = {index_to_node[i] for i in attractor}
    assert states
    assert len(states) < len(index_to_node)
    assert any(node.player_0_win() for node in states)


def test_dead_hands_cannot_attack_or_be_attacked():
    game = ChopsticksGame(((0, 3), (0, 2)))
    states = {neighbor.state for neighbor in game.get_neighbors()}
    # Only one attack (3 onto 2), plus the splits of 3.
    assert ((0, 3), (0, 0)) in states
    assert ((0, 3), (0, 2)) not in states  # no "passing" with the dead hand
    assert ((0, 3), (3, 2)) not in states  # no reviving the opponent's dead hand


def test_splits_never_kill_your_own_hand():
    game = ChopsticksGame(((4, 4), (1, 2)))
    assert all(neighbor.state[0] == (4, 4) for neighbor in game.get_neighbors())


def test_finished_games_have_no_moves():
    assert ChopsticksGame(((1, 1), (0, 0)), player=1).get_neighbors() == []
    assert ChopsticksGame(((0, 0), (1, 1)), player=0).get_neighbors() == []


def test_second_player_can_force_a_win():
    adjacency_matrix, index_to_node = build_adjacency_matrix(ChopsticksGame())
    player_0 = compute_attractor(adjacency_matrix, index_to_node, player=0)
    player_1 = compute_attractor(adjacency_matrix, index_to_node, player=1)

    assert len(index_to_node) == 382
    assert not set(player_0) & set(player_1)
    assert 0 not in player_0
    assert player_1[0] == 26


def test_bot_never_loses_a_won_position():
    bot = OptimalBot()
    for game in bot.nodes:
        if game.is_terminal() or bot.outcome(game) != game.player:
            continue
        move = bot.choose(game)
        assert bot.outcome(move) == game.player
        assert bot.moves_to_win(move) == bot.moves_to_win(game) - 1


def test_bot_beats_you_if_you_go_first():
    bot = OptimalBot()
    game = ChopsticksGame()
    while not game.is_terminal():
        if game.player == 0:
            game = game.get_neighbors()[0]  # a not-very-clever human
        else:
            game = bot.choose(game)
    assert game.player_1_win()
