"""Tests for wave generation schedules in Quick and Full game modes."""

from py_warcraft_td.waves import generate_wave_schedule


def test_quick_mode_20_waves():
    schedule = generate_wave_schedule(total_waves=20)
    assert len(schedule) == 20

    # Boss waves every 5 waves
    assert schedule[4].modifier == "boss"   # Wave 5
    assert schedule[9].modifier == "boss"   # Wave 10
    assert schedule[14].modifier == "boss"  # Wave 15
    assert schedule[19].modifier == "boss"  # Wave 20

    # Flying waves exist
    flying_waves = [w for w in schedule if w.is_flying]
    assert len(flying_waves) >= 2


def test_full_mode_60_waves():
    schedule = generate_wave_schedule(total_waves=60)
    assert len(schedule) == 60
    assert schedule[0].wave_num == 1
    assert schedule[59].wave_num == 60
    assert schedule[59].modifier == "boss"

    # HP increases monotonically across waves
    assert schedule[59].base_hp > schedule[0].base_hp
