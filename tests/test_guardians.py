"""Tests for Guardian Altar, Boss summoning, and interest upgrades."""

from py_warcraft_td.elements import Element
from py_warcraft_td.guardians import GuardianManager


def test_guardian_summoning_flow():
    gm = GuardianManager()
    assert gm.available_tokens == 0
    assert not gm.can_summon()

    # Receive token at wave 5
    gm.add_token()
    assert gm.can_summon()

    # Summon Fire Guardian
    path = [(0, 8), (1, 8)]
    boss = gm.summon_guardian(Element.FIRE, wave_num=5, path=path)
    assert boss is not None
    assert boss.armor_element == Element.FIRE
    assert boss.modifier == "boss"
    assert gm.available_tokens == 0

    # Defeating Fire Guardian
    tier, msg = gm.on_guardian_killed(Element.FIRE)
    assert tier == 1
    assert gm.essences[Element.FIRE] == 1


def test_interest_upgrade_choice():
    gm = GuardianManager()
    gm.add_token()

    # Choose interest upgrade instead of element
    bonus = gm.choose_interest_upgrade()
    assert bonus == 0.005
    assert gm.interest_bonus == 0.005
    assert gm.available_tokens == 0
