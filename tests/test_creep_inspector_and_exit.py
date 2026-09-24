"""Tests for creep inspection, numerical health display, weakness calculations,
unit counter, and exit game functionality.
"""

import os
import pygame
import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from py_warcraft_td.config import create_layout_config
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import (
    Element,
    get_armor_weakness,
    get_armor_resistance,
    get_element_multiplier,
)
from py_warcraft_td.game import Game
from py_warcraft_td.icons import IconRenderer
from py_warcraft_td.towers.tower_base import Tower
from py_warcraft_td.towers.tower_catalog import get_tower_def
from py_warcraft_td.ui import UIManager


def test_armor_weakness_and_resistance_rules():
    """Verify that weakness always matches 200% incoming damage, and resistance matches 50% incoming damage."""
    # Element circle: LIGHT -> DARK -> WATER -> FIRE -> NATURE -> EARTH -> LIGHT
    # Attacker -> Defender = 2.0x (attacker precedes defender)
    # Therefore, defender's WEAKNESS is the preceding element in the circle!
    for armor_elem in [Element.LIGHT, Element.DARKNESS, Element.WATER, Element.FIRE, Element.NATURE, Element.EARTH]:
        weak_elem = get_armor_weakness(armor_elem)
        assert weak_elem is not None
        assert get_element_multiplier(weak_elem, armor_elem) == 2.0

        res_elem = get_armor_resistance(armor_elem)
        assert res_elem is not None
        assert get_element_multiplier(res_elem, armor_elem) == 0.5


def test_vector_icons_for_monster_and_exit():
    """Ensure vector icons for monster and exit render valid pygame Surfaces."""
    pygame.init()
    monster_ico = IconRenderer.get_icon("monster", 24)
    assert isinstance(monster_ico, pygame.Surface)
    assert monster_ico.get_width() == 24 and monster_ico.get_height() == 24

    exit_ico = IconRenderer.get_icon("exit", 20)
    assert isinstance(exit_ico, pygame.Surface)
    assert exit_ico.get_width() == 20 and exit_ico.get_height() == 20


def test_active_creeps_counter():
    """Verify that active creep counter accurately counts alive creeps."""
    game = Game(width=1920, height=1080, headless=True)
    game.start_game(mode_waves=20, difficulty="Normal")

    c1 = Creep(1, "Goblin", 1, 100.0, 60.0, Element.EARTH, 10, layout=game.layout)
    c2 = Creep(2, "Harpy", 1, 150.0, 75.0, Element.WATER, 15, is_flying=True, layout=game.layout)
    c3 = Creep(3, "Dragon", 1, 500.0, 50.0, Element.FIRE, 50, modifier="boss", layout=game.layout)

    game.creeps = [c1, c2, c3]
    active_count = sum(1 for c in game.creeps if not c.is_dead and not c.has_leaked)
    assert active_count == 3

    # Mark c1 dead
    c1.is_dead = True
    active_count = sum(1 for c in game.creeps if not c.is_dead and not c.has_leaked)
    assert active_count == 2

    # Mark c2 leaked
    c2.has_leaked = True
    active_count = sum(1 for c in game.creeps if not c.is_dead and not c.has_leaked)
    assert active_count == 1


def test_creep_selection_and_inspection():
    """Verify selecting a creep via clicking on the field sets selected_creep."""
    game = Game(width=1920, height=1080, headless=True)
    game.start_game(mode_waves=20, difficulty="Normal")

    c = Creep(1, "Feuer-Elementar", 3, 450.0, 65.0, Element.FIRE, 20, layout=game.layout)
    c.x = 200.0
    c.y = 250.0
    c.hp = 320.0
    game.creeps = [c]

    # Simulate clicking near the creep (202, 251)
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (202, 251)})
    pygame.event.post(ev)
    game.handle_events()

    assert game.selected_creep == c
    assert game.selected_placed_tower is None
    assert game.selected_build_def is None

    # Simulate pressing ESC to deselect
    ev_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    pygame.event.post(ev_esc)
    game.handle_events()

    assert game.selected_creep is None


def test_creep_inspector_ui_rendering():
    """Verify that _draw_creep_inspector renders without crash and displays stats."""
    pygame.init()
    screen = pygame.Surface((1920, 1080))
    ui = UIManager(screen)
    layout = create_layout_config(1920, 1080)

    creep = Creep(10, "Wald-Gorgon", 5, 1200.0, 70.0, Element.NATURE, 25, modifier="tank", layout=layout)
    creep.hp = 850.0
    creep.slow_timer = 2.5
    creep.slow_factor = 0.6
    creep.burn_timer = 1.8
    creep.burn_dps = 45.0

    deselected = False
    def on_deselect():
        nonlocal deselected
        deselected = True

    panel_rect = pygame.Rect(layout.sidebar_x, layout.sidebar_y, layout.sidebar_width, layout.sidebar_height)
    ui.draw_sidebar(
        layout=layout,
        gold=500,
        unlocked_elements={},
        selected_build_def=None,
        selected_placed_tower=None,
        on_select_build_def=lambda td: None,
        on_upgrade_tower=lambda t: None,
        on_sell_tower=lambda t: None,
        selected_creep=creep,
        on_deselect_creep=on_deselect,
    )

    # Click the close [X] button or bottom deselect button
    close_x = panel_rect.right - 25
    close_y = panel_rect.y + 25
    handled = ui.handle_click((close_x, close_y))
    assert handled is True
    assert deselected is True


def test_creep_death_clears_selection():
    """Verify that when a selected creep dies or leaks, update() cleans it up."""
    game = Game(width=1920, height=1080, headless=True)
    game.start_game(mode_waves=20, difficulty="Normal")

    c = Creep(1, "Schattenpirscher", 2, 200.0, 90.0, Element.DARKNESS, 15, layout=game.layout)
    game.creeps = [c]
    game.selected_creep = c

    c.is_dead = True
    game.update(0.1)

    assert game.selected_creep is None
    assert c not in game.creeps


def test_exit_game_buttons():
    """Verify that exit buttons quit the game or return to menu."""
    game = Game(width=1920, height=1080, headless=True)

    # In start menu
    assert game.running is True
    game._quit_game()
    assert game.running is False

    # In game, return to menu
    game.running = True
    game.start_game(mode_waves=20, difficulty="Normal")
    assert game.game_state == "PLAYING"
    game._return_to_menu()
    assert game.game_state == "START_MENU"
