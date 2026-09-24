"""Tests for tower definitions, catalog integrity, and unlocking rules."""

from py_warcraft_td.elements import Element
from py_warcraft_td.towers.tower_catalog import (
    ALL_TOWERS,
    BASE_ELEMENTAL_TOWERS,
    DUAL_TOWERS,
    STARTER_TOWERS,
    TRIPLE_TOWERS,
    get_available_towers,
    get_tower_def,
)


def test_tower_counts():
    """Verify exact tower composition requested by user."""
    assert len(STARTER_TOWERS) == 6        # 2 starters x 3 tiers
    assert len(BASE_ELEMENTAL_TOWERS) == 18 # 6 base elements x 3 tiers
    assert len(DUAL_TOWERS) == 15           # 15 dual combinations
    assert len(TRIPLE_TOWERS) == 20         # 20 triple combinations
    assert len(ALL_TOWERS) == 59


def test_starter_towers_available_by_default():
    """Starter tier 1 towers (Arrow 1 and Cannon 1) must be available without any element essences."""
    available = get_available_towers({})
    ids = [t.id for t in available]
    assert "arrow_1" in ids
    assert "cannon_1" in ids
    # Dual/triple should not be available
    assert "trickery" not in ids
    assert "laser" not in ids


def test_element_unlocks_base_and_combinations():
    """Unlocking Light and Fire essences must unlock Light, Fire, and Electricity tower."""
    essences = {Element.LIGHT: 1, Element.FIRE: 1}
    available = get_available_towers(essences)
    ids = [t.id for t in available]

    assert "light_1" in ids
    assert "fire_1" in ids
    assert "electricity" in ids  # Dual: Light + Fire
    assert "ice" not in ids      # Requires Water
    assert "laser" not in ids    # Requires Darkness


def test_triple_tower_unlock():
    """Triple tower (e.g. Laser: Light + Darkness + Fire) requires all 3 elements."""
    essences = {Element.LIGHT: 1, Element.DARKNESS: 1, Element.FIRE: 1}
    available = get_available_towers(essences)
    ids = [t.id for t in available]

    assert "laser" in ids
    assert "trickery" in ids     # Light + Dark
    assert "electricity" in ids  # Light + Fire
    assert "doom" in ids         # Dark + Fire
    assert "prisma" not in ids   # Requires Water


def test_tower_stats_sanity():
    """Verify all towers have positive costs, ranges, damage, and cooldowns."""
    for tid, tdef in ALL_TOWERS.items():
        assert tdef.cost > 0, f"{tid} cost invalid"
        assert tdef.range_px >= 100.0, f"{tid} range invalid"
        assert tdef.damage > 0.0, f"{tid} damage invalid"
        assert tdef.attack_cooldown > 0.0, f"{tid} cooldown invalid"
        assert tdef.targets in ("ground", "air", "both"), f"{tid} targets invalid"
