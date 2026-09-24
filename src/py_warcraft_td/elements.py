"""Element definitions, circle of advantage, and damage multiplier matrix."""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from py_warcraft_td.config import ELEMENT_COLORS


class Element(str, Enum):
    NONE = "NONE"
    LIGHT = "LIGHT"
    DARKNESS = "DARKNESS"
    WATER = "WATER"
    FIRE = "FIRE"
    NATURE = "NATURE"
    EARTH = "EARTH"


# Circle of Elements: Each element deals bonus damage to the next element in the list.
# Light > Darkness > Water > Fire > Nature > Earth > Light
ELEMENT_CIRCLE: List[Element] = [
    Element.LIGHT,
    Element.DARKNESS,
    Element.WATER,
    Element.FIRE,
    Element.NATURE,
    Element.EARTH,
]

ELEMENT_INDEX: Dict[Element, int] = {elem: i for i, elem in enumerate(ELEMENT_CIRCLE)}

ELEMENT_NAMES_DE: Dict[Element, str] = {
    Element.NONE: "Physisch",
    Element.LIGHT: "Licht",
    Element.DARKNESS: "Dunkelheit",
    Element.WATER: "Wasser",
    Element.FIRE: "Feuer",
    Element.NATURE: "Natur",
    Element.EARTH: "Erde",
}

ELEMENT_SYMBOLS: Dict[Element, str] = {
    Element.NONE: "⚪",
    Element.LIGHT: "✨",
    Element.DARKNESS: "🌑",
    Element.WATER: "💧",
    Element.FIRE: "🔥",
    Element.NATURE: "🌿",
    Element.EARTH: "⛰️",
}


def get_element_multiplier(attack_elem: Element, armor_elem: Element) -> float:
    """Calculate the damage multiplier based on attack element and target armor element.

    Returns:
        2.0 if attack_elem is super-effective against armor_elem.
        0.5 if armor_elem resists attack_elem.
        1.0 otherwise (neutral or physical/none).
    """
    if attack_elem == Element.NONE or armor_elem == Element.NONE:
        return 1.0

    if attack_elem not in ELEMENT_INDEX or armor_elem not in ELEMENT_INDEX:
        return 1.0

    atk_idx = ELEMENT_INDEX[attack_elem]
    arm_idx = ELEMENT_INDEX[armor_elem]
    n = len(ELEMENT_CIRCLE)

    # Super effective: attack element precedes target armor in circle (atk -> arm)
    if (atk_idx + 1) % n == arm_idx:
        return 2.0

    # Resisted: target armor precedes attack element in circle (arm -> atk)
    if (arm_idx + 1) % n == atk_idx:
        return 0.5

    # Neutral
    return 1.0


def get_strong_against(elem: Element) -> Optional[Element]:
    """Get the element that `elem` is strong against (deals 200% damage)."""
    if elem not in ELEMENT_INDEX:
        return None
    idx = ELEMENT_INDEX[elem]
    return ELEMENT_CIRCLE[(idx + 1) % len(ELEMENT_CIRCLE)]


def get_weak_against(elem: Element) -> Optional[Element]:
    """Get the element that `elem` is weak against (deals 50% damage)."""
    if elem not in ELEMENT_INDEX:
        return None
    idx = ELEMENT_INDEX[elem]
    return ELEMENT_CIRCLE[(idx - 1) % len(ELEMENT_CIRCLE)]


def get_armor_weakness(armor_elem: Element) -> Optional[Element]:
    """Get the attacking element that deals 200% damage against this armor element."""
    return get_weak_against(armor_elem)


def get_armor_resistance(armor_elem: Element) -> Optional[Element]:
    """Get the attacking element that is resisted (deals only 50% damage) by this armor element."""
    return get_strong_against(armor_elem)


def get_element_color(elem: Element) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Return primary and secondary RGB colors for an element."""
    return ELEMENT_COLORS.get(elem.value, ELEMENT_COLORS["NONE"])
