"""Tests for creep behavior, elemental damage, status effects, and leak mechanics."""

from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import Element
from py_warcraft_td.pathfinding import grid_to_pixel


def test_creep_element_damage_multiplier():
    """Creep with Darkness armor takes 200% from Light and 50% from Water."""
    creep = Creep(
        creep_id=1,
        name="TestCreep",
        wave_num=1,
        max_hp=1000.0,
        speed=80.0,
        armor_element=Element.DARKNESS,
        gold_reward=5,
    )

    # Light attack deals 200%
    dmg, mult = creep.take_damage(100.0, Element.LIGHT)
    assert mult == 2.0
    assert dmg == 200.0
    assert creep.hp == 800.0

    # Water attack deals 50%
    dmg, mult = creep.take_damage(100.0, Element.WATER)
    assert mult == 0.5
    assert dmg == 50.0
    assert creep.hp == 750.0


def test_creep_status_effects():
    """Verify slow, burn, and sunder application and tick down."""
    creep = Creep(
        creep_id=2,
        name="TestCreep",
        wave_num=1,
        max_hp=500.0,
        speed=100.0,
        armor_element=Element.NONE,
        gold_reward=5,
    )

    # Apply 40% slow for 2s
    creep.apply_slow(0.40, 2.0)
    assert creep.slow_factor == 0.60
    assert creep.slow_timer == 2.0

    # Apply burn: 50 DPS for 2s
    creep.apply_burn(50.0, 2.0)

    # Update for 1 second
    creep.update(1.0)
    assert creep.slow_timer == 1.0
    # Burn did ~50 damage
    assert 449.0 <= creep.hp <= 451.0


def test_creep_leak_and_respawn():
    """In Element TD, leaked creeps deduct life and respawn at start with remaining HP."""
    path = [(0, 8), (1, 8), (2, 8)]
    creep = Creep(
        creep_id=3,
        name="TestCreep",
        wave_num=1,
        max_hp=200.0,
        speed=100.0,
        armor_element=Element.NONE,
        gold_reward=5,
        path=path,
    )
    creep.hp = 120.0  # Damaged
    creep.has_leaked = True

    # Respawn
    creep.respawn_at_start(path)
    assert not creep.has_leaked
    assert creep.hp == 120.0  # Retains damaged HP
    assert creep.path_index == 0
    spawn_px = grid_to_pixel((0, 8))
    assert creep.x == spawn_px[0]
    assert creep.y == spawn_px[1]
