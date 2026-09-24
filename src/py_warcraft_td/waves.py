"""Wave generation and definitions for Quick Game (20 waves) and Full Game (60 waves)."""

from dataclasses import dataclass
from typing import List
from py_warcraft_td.elements import Element


@dataclass
class WaveConfig:
    wave_num: int
    name: str
    creep_count: int
    armor_element: Element
    is_flying: bool
    modifier: str           # "normal", "fast", "tank", "swarm", "boss", "shielded", "regen"
    base_hp: float
    speed: float
    gold_reward: int
    spawn_interval: float


# Creep flavor names according to element and modifier
CREEP_NAMES = {
    Element.NONE: {
        "normal": "Goblinschurke",
        "fast": "Räuberwolf",
        "tank": "Oger-Brecher",
        "swarm": "Gnollhorde",
        "boss": "Kriegshäuptling",
        "flying": "Harpien-Späherin",
    },
    Element.LIGHT: {
        "normal": "Sonnenadept",
        "fast": "Lichtblitz",
        "tank": "Templer",
        "swarm": "Glühwürmchen",
        "boss": "Lichtarchon",
        "flying": "Pegasus-Reiter",
    },
    Element.DARKNESS: {
        "normal": "Schattengul",
        "fast": "Nachtpirscher",
        "tank": "Abscheulichkeit",
        "swarm": "Gruftkäfer",
        "boss": "Schreckenslord",
        "flying": "Gargoyle",
    },
    Element.WATER: {
        "normal": "Flusskriecher",
        "fast": "Sturmwelle",
        "tank": "Gezeitengolem",
        "swarm": "Murlocs",
        "boss": "Leviathan",
        "flying": "Gischtadler",
    },
    Element.FIRE: {
        "normal": "Feuerkobold",
        "fast": "Höllenhund",
        "tank": "Magmagolem",
        "swarm": "Funkenbrut",
        "boss": "Ragnaros-Avatar",
        "flying": "Phönix",
    },
    Element.NATURE: {
        "normal": "Dornenpirscher",
        "fast": "Raptor",
        "tank": "Uralter Urtum",
        "swarm": "Waldspinnen",
        "boss": "Smaragd-Drache",
        "flying": "Chimäre",
    },
    Element.EARTH: {
        "normal": "Steinsucher",
        "fast": "Kieselroller",
        "tank": "Felsenkoloss",
        "swarm": "Kobold-Bergleute",
        "boss": "Gebirgstitan",
        "flying": "Fledermausreiter",
    },
}


def _get_creep_name(elem: Element, mod: str, is_flying: bool) -> str:
    sub = CREEP_NAMES.get(elem, CREEP_NAMES[Element.NONE])
    if is_flying:
        return sub.get("flying", "Flugbestie")
    return sub.get(mod, "Monster")


def generate_wave_schedule(total_waves: int = 60, difficulty_mult: float = 1.0) -> List[WaveConfig]:
    """Generate a rich, balanced progression of waves."""
    schedule: List[WaveConfig] = []

    # Repeating sequence of elements
    elements_cycle = [
        Element.NONE,
        Element.LIGHT,
        Element.DARKNESS,
        Element.WATER,
        Element.FIRE,
        Element.NATURE,
        Element.EARTH,
    ]

    for w in range(1, total_waves + 1):
        # Element rotation
        elem = elements_cycle[(w - 1) % len(elements_cycle)]

        # Base HP exponential scaling
        # Level 1: ~45 HP, Level 20: ~2,500 HP, Level 60: ~120,000 HP
        hp_growth = 38.0 * (1.14 ** (w - 1)) * difficulty_mult

        is_flying = False
        modifier = "normal"
        speed = 70.0
        count = 15
        interval = 0.65
        gold_per_creep = max(1, int(1.8 + w * 0.45))

        # Modifiers and special waves
        if w % 5 == 0:
            # Boss Wave every 5 levels
            modifier = "boss"
            count = 1 if w <= 15 else (2 if w <= 35 else 3)
            hp_growth *= 10.0  # Massive HP for bosses
            speed = 52.0
            interval = 2.0
            gold_per_creep *= 8
        elif w in (4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59):
            # Flying Wave
            is_flying = True
            modifier = "fast"
            count = 12
            speed = 88.0
            hp_growth *= 0.65
            interval = 0.75
        elif w % 4 == 0:
            # Swarm Wave
            modifier = "swarm"
            count = 25
            speed = 75.0
            hp_growth *= 0.40
            interval = 0.35
            gold_per_creep = max(1, int(gold_per_creep * 0.5))
        elif w % 3 == 0:
            # Fast runner wave
            modifier = "fast"
            count = 14
            speed = 100.0
            hp_growth *= 0.75
            interval = 0.55
        elif w % 7 == 0:
            # Shielded wave
            modifier = "shielded"
            count = 12
            speed = 65.0
            hp_growth *= 1.2
            interval = 0.70
        elif w % 6 == 0:
            # Regen wave
            modifier = "regen"
            count = 14
            speed = 68.0
            hp_growth *= 1.1
            interval = 0.65

        name = _get_creep_name(elem, modifier, is_flying)

        cfg = WaveConfig(
            wave_num=w,
            name=name,
            creep_count=count,
            armor_element=elem,
            is_flying=is_flying,
            modifier=modifier,
            base_hp=max(20.0, hp_growth),
            speed=speed,
            gold_reward=gold_per_creep,
            spawn_interval=interval,
        )
        schedule.append(cfg)

    return schedule
