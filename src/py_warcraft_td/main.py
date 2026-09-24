"""CLI entrypoint for py-warcraft-td."""

import argparse
import sys
from py_warcraft_td.game import Game


def main() -> None:
    parser = argparse.ArgumentParser(description="Element TD - Warcraft III Python Game Adaptation")
    parser.add_argument("--quick", action="store_true", help="Start directly in Quick Mode (20 waves)")
    parser.add_argument("--difficulty", choices=["Normal", "Hard", "Chaos"], default="Normal", help="Game difficulty")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio effects")
    parser.add_argument("--headless", action="store_true", help="Run without opening display window (for testing)")
    parser.add_argument("--test-frames", type=int, default=0, help="Run for N frames and exit (for automated testing)")

    args = parser.parse_args()

    game = Game(headless=args.headless)
    if args.no_audio:
        game.audio.enabled = False

    if args.quick:
        game.start_game(mode_waves=20, difficulty=args.difficulty)

    if args.test_frames > 0:
        # Automated headless test run
        if game.game_state == "START_MENU":
            game.start_game(mode_waves=20, difficulty="Normal")

        for _ in range(args.test_frames):
            game.update(1.0 / 60.0)
            game.draw()
        print(f"Automated test completed successfully across {args.test_frames} frames!")
        return

    game.run()


if __name__ == "__main__":
    main()
