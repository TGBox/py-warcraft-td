"""Tests for procedural vector icons and sprites."""

import pygame
from py_warcraft_td.elements import Element, ELEMENT_CIRCLE
from py_warcraft_td.icons import IconRenderer
from py_warcraft_td.sprites import SpriteRenderer
from py_warcraft_td.towers.tower_catalog import ALL_TOWERS


def test_vector_icons_generation():
    """Verify all UI and utility icons render valid Pygame surfaces."""
    icon_names = [
        "gold",
        "heart",
        "swords",
        "wings",
        "lock",
        "lightning",
        "upgrade",
        "close",
        "play",
        "pause",
        "fast_forward",
        "trophy",
        "skull",
    ]
    for name in icon_names:
        surf = IconRenderer.get_icon(name, size=24)
        assert isinstance(surf, pygame.Surface)
        assert surf.get_width() == 24
        assert surf.get_height() == 24


def test_element_vector_badges():
    """Verify each of the 6 elements plus physical has a valid vector badge."""
    elements_to_test = [Element.NONE] + ELEMENT_CIRCLE
    for elem in elements_to_test:
        surf = IconRenderer.get_element_icon(elem, size=20)
        assert isinstance(surf, pygame.Surface)
        assert surf.get_width() == 20
        assert surf.get_height() == 20


def test_tower_sprites_all_categories():
    """Verify procedural sprite generation for all 59 towers in the catalog."""
    for tid, tdef in ALL_TOWERS.items():
        surf = SpriteRenderer.get_tower_sprite(tdef, size=48, is_selected=False)
        assert isinstance(surf, pygame.Surface)
        assert surf.get_width() == 48
        assert surf.get_height() == 48

        # Also test selected state
        sel_surf = SpriteRenderer.get_tower_sprite(tdef, size=48, is_selected=True)
        assert isinstance(sel_surf, pygame.Surface)


def test_creep_sprites_all_modifiers_and_elements():
    """Verify creep sprites for all modifiers across all elements."""
    modifiers = ["normal", "fast", "tank", "swarm", "boss"]
    for elem in ELEMENT_CIRCLE:
        for mod in modifiers:
            # Ground
            g_surf = SpriteRenderer.get_creep_sprite(elem, mod, is_flying=False, size=36, anim_frame=0)
            assert isinstance(g_surf, pygame.Surface)
            assert g_surf.get_width() == 36

            # Flying
            f_surf = SpriteRenderer.get_creep_sprite(elem, mod, is_flying=True, size=42, anim_frame=1)
            assert isinstance(f_surf, pygame.Surface)
            assert f_surf.get_width() == 42
