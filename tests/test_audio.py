"""Tests for procedural audio catalog generation."""

from py_warcraft_td.audio import AudioManager


def test_audio_catalog_synthesis():
    """Verify AudioManager synthesizes procedural sound catalog."""
    am = AudioManager(enabled=True)
    # Check key audio effects
    expected_keys = [
        "arrow_shot",
        "cannon_shot",
        "light_beam",
        "dark_pulse",
        "water_splash",
        "fire_blast",
        "nature_shot",
        "earth_slam",
        "gold_interest",
        "creep_death",
        "guardian_summon",
        "victory",
        "game_over",
    ]
    for k in expected_keys:
        assert k in am.sounds, f"Missing sound {k}"
