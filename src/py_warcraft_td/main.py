"""CLI entrypoint for py-warcraft-td with Fullscreen and Ultrawide support."""

import argparse
import sys
from py_warcraft_td.game import Game


def main() -> None:
    parser = argparse.ArgumentParser(description="Element TD - Warcraft III Python Game Adaptation")
    parser.add_argument("--quick", action="store_true", help="Start directly in Quick Mode (20 waves)")
    parser.add_argument("--difficulty", choices=["Normal", "Hard", "Chaos"], default="Normal", help="Game difficulty")
    parser.add_argument("--fullscreen", action="store_true", help="Launch in Fullscreen mode (toggle with F11 in-game)")
    parser.add_argument("--ultrawide", action="store_true", help="Launch in 2560x1080 (21:9 Ultrawide) resolution")
    parser.add_argument("--res", choices=["1920x1080", "2560x1080", "1360x768"], default="1920x1080", help="Screen resolution")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio effects")
    parser.add_argument("--headless", action="store_true", help="Run without opening display window (for testing)")
    parser.add_argument("--test-frames", type=int, default=0, help="Run for N frames and exit (for automated testing)")

    args = parser.parse_args()

    # Determine resolution
    if args.ultrawide:
        w, h = 2560, 1080
    elif args.res == "2560x1080":
        w, h = 2560, 1080
    elif args.res == "1360x768":
        w, h = 1360, 768
    else:
        w, h = 1920, 1080

    game = Game(width=w, height=h, fullscreen=args.fullscreen, headless=args.headless)
    if args.no_audio:
        game.audio.enabled = False

    if args.quick:
        game.start_game(mode_waves=20, difficulty=args.difficulty)

    if args.test_frames > 0:
        if game.game_state == "START_MENU":
            game.start_game(mode_waves=20, difficulty="Normal")

        for _ in range(args.test_frames):
            game.update(1.0 / 60.0)
            game.draw()
        print(f"Automated test completed successfully across {args.test_frames} frames ({w}x{h})!")
        return

    game.run()


if __name__ == "__main__":
    main()
