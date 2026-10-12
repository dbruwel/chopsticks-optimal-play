"""Play Chopsticks against the optimal bot in the terminal.

Run with ``chopsticks`` (after ``pip install -e .``) or
``python -m chopsticks_optimal_play``.
"""

from __future__ import annotations

import argparse

from .bot import OptimalBot
from .game import ChopsticksGame


def describe(game: ChopsticksGame, move: ChopsticksGame, bot: bool = False) -> str:
    """Describe a move as either a tap or a split."""
    player = game.player
    own, other = ("its", "your") if bot else ("your", "their")
    if move.state[player] != game.state[player]:
        return f"split   {own} {game.state[player]} -> {move.state[player]}"
    return f"tap     {other} {game.state[1 - player]} -> {move.state[1 - player]}"


def show(game: ChopsticksGame, you: int) -> None:
    print()
    print(f"  bot: {game.state[1 - you]}")
    print(f"  you: {game.state[you]}")
    print()


def ask_for_move(game: ChopsticksGame) -> ChopsticksGame:
    moves = game.get_neighbors()
    for number, move in enumerate(moves, start=1):
        print(f"  {number}. {describe(game, move)}")
    while True:
        answer = input("your move: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(moves):
            return moves[int(answer) - 1]
        print(f"pick a number from 1 to {len(moves)}")


def play(you: int, hints: bool = False) -> None:
    bot = OptimalBot()
    game = ChopsticksGame()

    while not game.is_terminal():
        show(game, you)
        if hints:
            winner = bot.outcome(game)
            if winner is None:
                print("  (hint: this one's a draw with good play)")
            else:
                who = "you" if winner == you else "the bot"
                print(f"  (hint: {who} can force a win in {bot.moves_to_win(game)})")

        if game.player == you:
            game = ask_for_move(game)
        else:
            move = bot.choose(game)
            print(f"bot plays: {describe(game, move, bot=True)}")
            game = move

    show(game, you)
    if game.state[you] == (0, 0):
        print("bot wins.")
    else:
        print("you win!")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Play Chopsticks against a bot that never makes a mistake."
    )
    parser.add_argument(
        "--first", action="store_true", help="go first (spoiler: you'll lose)"
    )
    parser.add_argument(
        "--hints", action="store_true", help="show who's winning before each move"
    )
    args = parser.parse_args()

    you = 0 if args.first else 1
    print("Chopsticks vs the bot. Both hands start on 1, hands die at 5.")
    print(f"you're going {'first' if you == 0 else 'second'}.")
    try:
        play(you, hints=args.hints)
    except (KeyboardInterrupt, EOFError):
        print("\nbye")


if __name__ == "__main__":
    main()
