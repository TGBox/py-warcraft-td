"""Tests for the 6-element circle and damage calculation in Element TD."""

import pytest
from py_warcraft_td.elements import (
    Element,
    ELEMENT_CIRCLE,
    get_element_multiplier,
    get_strong_against,
    get_weak_against,
)


def test_element_circle_order():
    """Verify circle: Light > Darkness > Water > Fire > Nature > Earth > Light."""
    expected = [
        Element.LIGHT,
        Element.DARKNESS,
        Element.WATER,
        Element.FIRE,
        Element.NATURE,
        Element.EARTH,
    ]
    assert ELEMENT_CIRCLE == expected


def test_element_advantages_200_percent():
    """Each element must deal 200% (2.0x) damage to the next element in the circle."""
    assert get_element_multiplier(Element.LIGHT, Element.DARKNESS) == 2.0
    assert get_element_multiplier(Element.DARKNESS, Element.WATER) == 2.0
    assert get_element_multiplier(Element.WATER, Element.FIRE) == 2.0
    assert get_element_multiplier(Element.FIRE, Element.NATURE) == 2.0
    assert get_element_multiplier(Element.NATURE, Element.EARTH) == 2.0
    assert get_element_multiplier(Element.EARTH, Element.LIGHT) == 2.0


def test_element_weaknesses_50_percent():
    """Each element must deal 50% (0.5x) damage when attacking its preceding counter."""
    assert get_element_multiplier(Element.DARKNESS, Element.LIGHT) == 0.5
    assert get_element_multiplier(Element.WATER, Element.DARKNESS) == 0.5
    assert get_element_multiplier(Element.FIRE, Element.WATER) == 0.5
    assert get_element_multiplier(Element.NATURE, Element.FIRE) == 0.5
    assert get_element_multiplier(Element.EARTH, Element.NATURE) == 0.5
    assert get_element_multiplier(Element.LIGHT, Element.EARTH) == 0.5


def test_element_neutral_and_physical():
    """Non-adjacent elements or physical (NONE) attacks deal 100% (1.0x) damage."""
    assert get_element_multiplier(Element.LIGHT, Element.FIRE) == 1.0
    assert get_element_multiplier(Element.WATER, Element.EARTH) == 1.0
    assert get_element_multiplier(Element.NONE, Element.LIGHT) == 1.0
    assert get_element_multiplier(Element.FIRE, Element.NONE) == 1.0


def test_helpers_strong_weak():
    assert get_strong_against(Element.FIRE) == Element.NATURE
    assert get_weak_against(Element.FIRE) == Element.WATER
    assert get_strong_against(Element.LIGHT) == Element.DARKNESS
    assert get_weak_against(Element.LIGHT) == Element.EARTH
