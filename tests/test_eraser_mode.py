"""Tests for Eraser / Demolish mode (single click and continuous drag brush)."""

import pygame
from py_warcraft_td.game import Game
from py_warcraft_td.towers.tower_catalog import get_tower_def


def test_eraser_mode_toggle():
    game = Game(width=1920, height=1080, headless=True)
    assert not game.is_eraser_mode

    game.toggle_eraser_mode()
    assert game.is_eraser_mode
    assert game.selected_build_def is None

    game.toggle_eraser_mode()
    assert not game.is_eraser_mode


def test_eraser_single_click_and_drag_brush():
    game = Game(width=1920, height=1080, headless=True)
    game.start_game(mode_waves=20, difficulty="Normal")
    arrow_def = get_tower_def("arrow_1")

    # Place 3 towers
    game._try_place_tower((2, 2), arrow_def)
    game._try_place_tower((3, 2), arrow_def)
    game._try_place_tower((4, 2), arrow_def)

    assert len(game.towers) == 3
    gold_before_erase = game.gold

    # 1. Enable Eraser Mode
    game.toggle_eraser_mode()
    assert game.is_eraser_mode

    # 2. Single click on (2, 2)
    # Simulate left click event
    pos_2_2 = game.layout.grid_to_pixel((2, 2))
    click_event = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"pos": (int(pos_2_2[0]), int(pos_2_2[1])), "button": 1}
    )
    pygame.event.post(click_event)
    game.handle_events()

    # Tower at (2, 2) must be gone without confirmation
    assert (2, 2) not in game.towers
    assert len(game.towers) == 2
    assert game.gold > gold_before_erase

    # 3. Drag brush across (3, 2) and (4, 2)
    pos_3_2 = game.layout.grid_to_pixel((3, 2))
    pos_4_2 = game.layout.grid_to_pixel((4, 2))

    motion_event_1 = pygame.event.Event(
        pygame.MOUSEMOTION, {"pos": (int(pos_3_2[0]), int(pos_3_2[1])), "buttons": (1, 0, 0)}
    )
    motion_event_2 = pygame.event.Event(
        pygame.MOUSEMOTION, {"pos": (int(pos_4_2[0]), int(pos_4_2[1])), "buttons": (1, 0, 0)}
    )
    pygame.event.post(motion_event_1)
    pygame.event.post(motion_event_2)
    game.handle_events()

    # Both towers erased by dragging!
    assert (3, 2) not in game.towers
    assert (4, 2) not in game.towers
    assert len(game.towers) == 0


def test_eraser_mode_exits_on_right_click_or_build_select():
    game = Game(width=1920, height=1080, headless=True)
    game.is_eraser_mode = True

    # Right click
    r_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (100, 100), "button": 3})
    pygame.event.post(r_click)
    game.handle_events()
    assert not game.is_eraser_mode

    # Re-enable and test Esc
    game.is_eraser_mode = True
    esc_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    pygame.event.post(esc_event)
    game.handle_events()
    assert not game.is_eraser_mode
