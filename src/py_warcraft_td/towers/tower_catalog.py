"""Comprehensive catalog of all towers in py-warcraft-td (Element TD).

Includes:
- 2 Starter Towers (Arrow, Cannon)
- 6 Base Elemental Towers (Tier 1 to 3)
- 15 Dual-Element Towers (all 2-element combinations)
- 20 Triple-Element Towers (all 3-element combinations)
Total = 43 unique tower types with full gameplay attributes, abilities, and WC3 lore.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from py_warcraft_td.elements import Element


@dataclass
class TowerAbility:
    """Special abilities and status effects granted by a tower."""
    slow_factor: float = 0.0        # e.g. 0.35 = 35% speed reduction
    slow_duration: float = 0.0      # Duration of slow in seconds
    splash_radius: float = 0.0      # Splash damage radius in pixels
    burn_dps: float = 0.0           # Burn damage per second
    burn_duration: float = 0.0      # Burn duration in seconds
    poison_dps: float = 0.0         # Poison damage per second
    poison_duration: float = 0.0    # Poison duration in seconds
    chain_bounces: int = 0          # Number of lightning bounces
    chain_decay: float = 0.8        # Damage multiplier per bounce
    armor_sunder: float = 0.0       # Extra damage taken factor (e.g. 0.30 = +30% damage taken)
    sunder_duration: float = 0.0
    gold_bounty_bonus: int = 0      # Extra gold awarded on kill
    stun_duration: float = 0.0      # Brief stun in seconds
    knockback_dist: float = 0.0     # Pixels knocked backwards along path


@dataclass
class TowerDefinition:
    """Immutable definition and attributes for a tower type."""
    id: str
    name: str
    category: str                   # "starter", "base", "dual", "triple"
    elements: List[Element]         # Elements required to build/upgrade
    tier: int                       # 1, 2, or 3
    cost: int                       # Gold build cost
    range_px: float                 # Range radius in pixels
    damage: float                   # Base attack damage
    attack_cooldown: float          # Seconds between attacks (cooldown)
    targets: str                    # "ground", "air", "both"
    attack_type: str                # "projectile", "instant_beam", "chain", "splash", "aura"
    projectile_speed: float         # Pixels per second (if projectile)
    ability: TowerAbility = field(default_factory=TowerAbility)
    description: str = ""
    sound_effect: str = "arrow_shot"
    upgrade_to: Optional[str] = None


# ==========================================
# 1. STARTER TOWERS (Non-elemental)
# ==========================================
STARTER_TOWERS: Dict[str, TowerDefinition] = {
    "arrow_1": TowerDefinition(
        id="arrow_1",
        name="Pfeilturm I",
        category="starter",
        elements=[],
        tier=1,
        cost=15,
        range_px=140.0,
        damage=16.0,
        attack_cooldown=0.65,
        targets="both",
        attack_type="projectile",
        projectile_speed=520.0,
        description="Zuverlässiger Grundturm mit schnellen Pfeilen. Trifft Boden- und Lufteinheiten.",
        sound_effect="arrow_shot",
        upgrade_to="arrow_2",
    ),
    "arrow_2": TowerDefinition(
        id="arrow_2",
        name="Pfeilturm II",
        category="starter",
        elements=[],
        tier=2,
        cost=35,
        range_px=155.0,
        damage=45.0,
        attack_cooldown=0.55,
        targets="both",
        attack_type="projectile",
        projectile_speed=560.0,
        description="Verstärkter Pfeilturm mit erhöhter Feuerrate und Reichweite.",
        sound_effect="arrow_shot",
        upgrade_to="arrow_3",
    ),
    "arrow_3": TowerDefinition(
        id="arrow_3",
        name="Pfeilturm III",
        category="starter",
        elements=[],
        tier=3,
        cost=85,
        range_px=170.0,
        damage=120.0,
        attack_cooldown=0.45,
        targets="both",
        attack_type="projectile",
        projectile_speed=600.0,
        description="Meisterlicher Scharfschützenturm für kontinuierlichen Schaden gegen Luft und Boden.",
        sound_effect="arrow_shot",
        upgrade_to=None,
    ),
    "cannon_1": TowerDefinition(
        id="cannon_1",
        name="Kanonenturm I",
        category="starter",
        elements=[],
        tier=1,
        cost=25,
        range_px=125.0,
        damage=42.0,
        attack_cooldown=1.35,
        targets="ground",
        attack_type="splash",
        projectile_speed=380.0,
        ability=TowerAbility(splash_radius=50.0),
        description="Schwere Artillerie mit Flächenschaden gegen dichte Gruppen von Bodeneinheiten.",
        sound_effect="cannon_shot",
        upgrade_to="cannon_2",
    ),
    "cannon_2": TowerDefinition(
        id="cannon_2",
        name="Kanonenturm II",
        category="starter",
        elements=[],
        tier=2,
        cost=60,
        range_px=140.0,
        damage=110.0,
        attack_cooldown=1.25,
        targets="ground",
        attack_type="splash",
        projectile_speed=400.0,
        ability=TowerAbility(splash_radius=60.0),
        description="Verbesserter Mörser mit größerem Explosionsradius.",
        sound_effect="cannon_shot",
        upgrade_to="cannon_3",
    ),
    "cannon_3": TowerDefinition(
        id="cannon_3",
        name="Kanonenturm III",
        category="starter",
        elements=[],
        tier=3,
        cost=130,
        range_px=155.0,
        damage=260.0,
        attack_cooldown=1.15,
        targets="ground",
        attack_type="splash",
        projectile_speed=420.0,
        ability=TowerAbility(splash_radius=72.0),
        description="Belagerungshaubitze, die gewaltige Druckwellen im Labyrinth erzeugt.",
        sound_effect="cannon_shot",
        upgrade_to=None,
    ),
}


# ==========================================
# 2. BASE ELEMENTAL TOWERS (Tier 1 - 3)
# ==========================================
BASE_ELEMENTAL_TOWERS: Dict[str, TowerDefinition] = {
    # --- LIGHT ---
    "light_1": TowerDefinition(
        id="light_1",
        name="Lichtturm I",
        category="base",
        elements=[Element.LIGHT],
        tier=1,
        cost=75,
        range_px=180.0,
        damage=65.0,
        attack_cooldown=0.60,
        targets="both",
        attack_type="instant_beam",
        projectile_speed=0.0,
        description="Schneller Lichtstrahl mit hoher Reichweite. Stark gegen Dunkelheit.",
        sound_effect="light_beam",
        upgrade_to="light_2",
    ),
    "light_2": TowerDefinition(
        id="light_2",
        name="Lichtturm II",
        category="base",
        elements=[Element.LIGHT],
        tier=2,
        cost=180,
        range_px=200.0,
        damage=180.0,
        attack_cooldown=0.52,
        targets="both",
        attack_type="instant_beam",
        projectile_speed=0.0,
        description="Gleißender Sonnenstrahl, der Gegner sofort versengt.",
        sound_effect="light_beam",
        upgrade_to="light_3",
    ),
    "light_3": TowerDefinition(
        id="light_3",
        name="Lichtturm III",
        category="base",
        elements=[Element.LIGHT],
        tier=3,
        cost=450,
        range_px=225.0,
        damage=480.0,
        attack_cooldown=0.45,
        targets="both",
        attack_type="instant_beam",
        projectile_speed=0.0,
        description="Göttliche Lichtlanze mit extremem Einzelschaden und Reichweite.",
        sound_effect="light_beam",
        upgrade_to=None,
    ),

    # --- DARKNESS ---
    "darkness_1": TowerDefinition(
        id="darkness_1",
        name="Dunkelheitsturm I",
        category="base",
        elements=[Element.DARKNESS],
        tier=1,
        cost=75,
        range_px=135.0,
        damage=110.0,
        attack_cooldown=1.05,
        targets="both",
        attack_type="projectile",
        projectile_speed=460.0,
        description="Schwarze Seelenkugel mit verheerendem Einzelschaden. Stark gegen Wasser.",
        sound_effect="dark_pulse",
        upgrade_to="darkness_2",
    ),
    "darkness_2": TowerDefinition(
        id="darkness_2",
        name="Dunkelheitsturm II",
        category="base",
        elements=[Element.DARKNESS],
        tier=2,
        cost=180,
        range_px=145.0,
        damage=290.0,
        attack_cooldown=0.95,
        targets="both",
        attack_type="projectile",
        projectile_speed=480.0,
        description="Konzentrierte Schattenenergie, die Seelen zerfetzt.",
        sound_effect="dark_pulse",
        upgrade_to="darkness_3",
    ),
    "darkness_3": TowerDefinition(
        id="darkness_3",
        name="Dunkelheitsturm III",
        category="base",
        elements=[Element.DARKNESS],
        tier=3,
        cost=450,
        range_px=160.0,
        damage=740.0,
        attack_cooldown=0.85,
        targets="both",
        attack_type="projectile",
        projectile_speed=510.0,
        description="Herrscher des Abgrunds mit apokalyptischem Direktschaden.",
        sound_effect="dark_pulse",
        upgrade_to=None,
    ),

    # --- WATER ---
    "water_1": TowerDefinition(
        id="water_1",
        name="Wasserturm I",
        category="base",
        elements=[Element.WATER],
        tier=1,
        cost=75,
        range_px=140.0,
        damage=55.0,
        attack_cooldown=0.85,
        targets="ground",
        attack_type="splash",
        projectile_speed=420.0,
        ability=TowerAbility(slow_factor=0.25, slow_duration=2.5, splash_radius=45.0),
        description="Flutenwelle, die Bodengegner im Bereich trifft und um 25% verlangsamt. Stark gegen Feuer.",
        sound_effect="water_splash",
        upgrade_to="water_2",
    ),
    "water_2": TowerDefinition(
        id="water_2",
        name="Wasserturm II",
        category="base",
        elements=[Element.WATER],
        tier=2,
        cost=180,
        range_px=155.0,
        damage=145.0,
        attack_cooldown=0.78,
        targets="ground",
        attack_type="splash",
        projectile_speed=440.0,
        ability=TowerAbility(slow_factor=0.35, slow_duration=3.0, splash_radius=55.0),
        description="Reißende Strömung mit 35% Verlangsamung und vergrößertem Spritzradius.",
        sound_effect="water_splash",
        upgrade_to="water_3",
    ),
    "water_3": TowerDefinition(
        id="water_3",
        name="Wasserturm III",
        category="base",
        elements=[Element.WATER],
        tier=3,
        cost=450,
        range_px=170.0,
        damage=380.0,
        attack_cooldown=0.70,
        targets="ground",
        attack_type="splash",
        projectile_speed=460.0,
        ability=TowerAbility(slow_factor=0.45, slow_duration=3.5, splash_radius=68.0),
        description="Gewaltiger Mahlstrom, der ganze Horden lähmt und ertränkt.",
        sound_effect="water_splash",
        upgrade_to=None,
    ),

    # --- FIRE ---
    "fire_1": TowerDefinition(
        id="fire_1",
        name="Feuerturm I",
        category="base",
        elements=[Element.FIRE],
        tier=1,
        cost=75,
        range_px=130.0,
        damage=70.0,
        attack_cooldown=0.80,
        targets="both",
        attack_type="splash",
        projectile_speed=450.0,
        ability=TowerAbility(splash_radius=40.0, burn_dps=15.0, burn_duration=2.5),
        description="Feuerball mit Explosionsradius und anhaltendem Brandschaden. Stark gegen Natur.",
        sound_effect="fire_blast",
        upgrade_to="fire_2",
    ),
    "fire_2": TowerDefinition(
        id="fire_2",
        name="Feuerturm II",
        category="base",
        elements=[Element.FIRE],
        tier=2,
        cost=180,
        range_px=140.0,
        damage=185.0,
        attack_cooldown=0.72,
        targets="both",
        attack_type="splash",
        projectile_speed=480.0,
        ability=TowerAbility(splash_radius=50.0, burn_dps=40.0, burn_duration=3.0),
        description="Höllenfeuer mit brennenden Rückständen.",
        sound_effect="fire_blast",
        upgrade_to="fire_3",
    ),
    "fire_3": TowerDefinition(
        id="fire_3",
        name="Feuerturm III",
        category="base",
        elements=[Element.FIRE],
        tier=3,
        cost=450,
        range_px=155.0,
        damage=470.0,
        attack_cooldown=0.65,
        targets="both",
        attack_type="splash",
        projectile_speed=500.0,
        ability=TowerAbility(splash_radius=60.0, burn_dps=100.0, burn_duration=3.5),
        description="Infernalische Feuersbrunst, die alles zu Asche verbrennt.",
        sound_effect="fire_blast",
        upgrade_to=None,
    ),

    # --- NATURE ---
    "nature_1": TowerDefinition(
        id="nature_1",
        name="Naturturm I",
        category="base",
        elements=[Element.NATURE],
        tier=1,
        cost=75,
        range_px=145.0,
        damage=45.0,
        attack_cooldown=0.65,
        targets="ground",
        attack_type="projectile",
        projectile_speed=480.0,
        ability=TowerAbility(poison_dps=25.0, poison_duration=4.0),
        description="Giftige Dornenranken, die Ziele vergiften. Stark gegen Erde.",
        sound_effect="nature_shot",
        upgrade_to="nature_2",
    ),
    "nature_2": TowerDefinition(
        id="nature_2",
        name="Naturturm II",
        category="base",
        elements=[Element.NATURE],
        tier=2,
        cost=180,
        range_px=160.0,
        damage=120.0,
        attack_cooldown=0.58,
        targets="ground",
        attack_type="projectile",
        projectile_speed=500.0,
        ability=TowerAbility(poison_dps=65.0, poison_duration=4.5),
        description="Tödliche Sporen mit giftiger Zersetzung über Zeit.",
        sound_effect="nature_shot",
        upgrade_to="nature_3",
    ),
    "nature_3": TowerDefinition(
        id="nature_3",
        name="Naturturm III",
        category="base",
        elements=[Element.NATURE],
        tier=3,
        cost=450,
        range_px=175.0,
        damage=310.0,
        attack_cooldown=0.50,
        targets="ground",
        attack_type="projectile",
        projectile_speed=530.0,
        ability=TowerAbility(poison_dps=160.0, poison_duration=5.0),
        description="Urzeitlicher Weltenbaum mit extrem aggressivem Toxin.",
        sound_effect="nature_shot",
        upgrade_to=None,
    ),

    # --- EARTH ---
    "earth_1": TowerDefinition(
        id="earth_1",
        name="Erdturm I",
        category="base",
        elements=[Element.EARTH],
        tier=1,
        cost=75,
        range_px=120.0,
        damage=85.0,
        attack_cooldown=1.20,
        targets="ground",
        attack_type="splash",
        projectile_speed=360.0,
        ability=TowerAbility(splash_radius=55.0, stun_duration=0.3),
        description="Wuchtiger Felsbrocken, der Erschütterungen auslöst und kurz betäubt. Stark gegen Licht.",
        sound_effect="earth_slam",
        upgrade_to="earth_2",
    ),
    "earth_2": TowerDefinition(
        id="earth_2",
        name="Erdturm II",
        category="base",
        elements=[Element.EARTH],
        tier=2,
        cost=180,
        range_px=130.0,
        damage=225.0,
        attack_cooldown=1.10,
        targets="ground",
        attack_type="splash",
        projectile_speed=380.0,
        ability=TowerAbility(splash_radius=65.0, stun_duration=0.4),
        description="Massives Erdbeben, das den Boden erzittern lässt.",
        sound_effect="earth_slam",
        upgrade_to="earth_3",
    ),
    "earth_3": TowerDefinition(
        id="earth_3",
        name="Erdturm III",
        category="base",
        elements=[Element.EARTH],
        tier=3,
        cost=450,
        range_px=145.0,
        damage=580.0,
        attack_cooldown=1.00,
        targets="ground",
        attack_type="splash",
        projectile_speed=400.0,
        ability=TowerAbility(splash_radius=78.0, stun_duration=0.55),
        description="Titanturm der Tektonik mit massiver Erschütterung und Betäubung.",
        sound_effect="earth_slam",
        upgrade_to=None,
    ),
}


# ==========================================
# 3. THE 15 DUAL-ELEMENT TOWERS
# ==========================================
# All 15 pairs from {Light, Darkness, Water, Fire, Nature, Earth}
DUAL_TOWERS: Dict[str, TowerDefinition] = {
    # 1. Light + Darkness: Trickery Tower
    "trickery": TowerDefinition(
        id="trickery",
        name="Täuschungsturm (Trickery)",
        category="dual",
        elements=[Element.LIGHT, Element.DARKNESS],
        tier=1,
        cost=200,
        range_px=160.0,
        damage=210.0,
        attack_cooldown=0.60,
        targets="both",
        attack_type="instant_beam",
        projectile_speed=0.0,
        description="Licht & Dunkelheit. Erzeugt Trugbilder und Phantom-Kritische Treffer mit hohem DPS.",
        sound_effect="light_beam",
    ),

    # 2. Light + Water: Ice Tower
    "ice": TowerDefinition(
        id="ice",
        name="Eisturm (Ice)",
        category="dual",
        elements=[Element.LIGHT, Element.WATER],
        tier=1,
        cost=200,
        range_px=150.0,
        damage=130.0,
        attack_cooldown=0.75,
        targets="both",
        attack_type="splash",
        projectile_speed=440.0,
        ability=TowerAbility(slow_factor=0.50, slow_duration=3.5, splash_radius=50.0),
        description="Licht & Wasser. Friert Feinde im Radius ein und verlangsamt sie massiv um 50%.",
        sound_effect="ice_freeze",
    ),

    # 3. Light + Fire: Electricity Tower
    "electricity": TowerDefinition(
        id="electricity",
        name="Elektrizitätsturm (Electricity)",
        category="dual",
        elements=[Element.LIGHT, Element.FIRE],
        tier=1,
        cost=200,
        range_px=170.0,
        damage=160.0,
        attack_cooldown=0.70,
        targets="both",
        attack_type="chain",
        projectile_speed=0.0,
        ability=TowerAbility(chain_bounces=4, chain_decay=0.85),
        description="Licht & Feuer. Entlädt Kettenblitze, die bis zu 4 nahe Feinde überspringen.",
        sound_effect="electric_zap",
    ),

    # 4. Light + Nature: Sun Tower
    "sun": TowerDefinition(
        id="sun",
        name="Sonnenturm (Sun)",
        category="dual",
        elements=[Element.LIGHT, Element.NATURE],
        tier=1,
        cost=200,
        range_px=190.0,
        damage=190.0,
        attack_cooldown=0.65,
        targets="both",
        attack_type="instant_beam",
        projectile_speed=0.0,
        ability=TowerAbility(burn_dps=45.0, burn_duration=3.0),
        description="Licht & Natur. Fokussierter Solarstrahl mit extremer Reichweite und Brandeffekt.",
        sound_effect="light_beam",
    ),

    # 5. Light + Earth: Quark / Gold Tower
    "quark": TowerDefinition(
        id="quark",
        name="Quarkturm (Gold / Quark)",
        category="dual",
        elements=[Element.LIGHT, Element.EARTH],
        tier=1,
        cost=200,
        range_px=140.0,
        damage=240.0,
        attack_cooldown=0.90,
        targets="ground",
        attack_type="projectile",
        projectile_speed=520.0,
        ability=TowerAbility(gold_bounty_bonus=3),
        description="Licht & Erde. Subatomare Impulse; bringt +3 Extragold für jeden getöteten Gegner.",
        sound_effect="gold_interest",
    ),

    # 6. Darkness + Water: Vapor Tower
    "vapor": TowerDefinition(
        id="vapor",
        name="Dunstritzturm (Vapor)",
        category="dual",
        elements=[Element.DARKNESS, Element.WATER],
        tier=1,
        cost=200,
        range_px=145.0,
        damage=125.0,
        attack_cooldown=0.65,
        targets="both",
        attack_type="splash",
        projectile_speed=430.0,
        ability=TowerAbility(splash_radius=60.0, slow_factor=0.30, slow_duration=2.5),
        description="Dunkelheit & Wasser. Giftiger Miasma-Nebel, der Feinde verlangsamt und erstickt.",
        sound_effect="water_splash",
    ),

    # 7. Darkness + Fire: Doom Tower
    "doom": TowerDefinition(
        id="doom",
        name="Verdammnisturm (Doom)",
        category="dual",
        elements=[Element.DARKNESS, Element.FIRE],
        tier=1,
        cost=200,
        range_px=150.0,
        damage=320.0,
        attack_cooldown=1.30,
        targets="both",
        attack_type="projectile",
        projectile_speed=460.0,
        ability=TowerAbility(splash_radius=45.0, burn_dps=60.0, burn_duration=3.0),
        description="Dunkelheit & Feuer. Verflucht das Ziel mit gewaltigem Einzelschaden und Todesfeuer.",
        sound_effect="dark_pulse",
    ),

    # 8. Darkness + Nature: Poison Tower
    "poison": TowerDefinition(
        id="poison",
        name="Giftturm (Poison)",
        category="dual",
        elements=[Element.DARKNESS, Element.NATURE],
        tier=1,
        cost=200,
        range_px=155.0,
        damage=110.0,
        attack_cooldown=0.70,
        targets="ground",
        attack_type="projectile",
        projectile_speed=480.0,
        ability=TowerAbility(poison_dps=95.0, poison_duration=5.0),
        description="Dunkelheit & Natur. Hochgiftiges Sekret, das Gegner über 5 Sekunden verätzt.",
        sound_effect="nature_shot",
    ),

    # 9. Darkness + Earth: Iron / Blacksmith Tower
    "iron": TowerDefinition(
        id="iron",
        name="Eisenturm (Blacksmith / Iron)",
        category="dual",
        elements=[Element.DARKNESS, Element.EARTH],
        tier=1,
        cost=200,
        range_px=130.0,
        damage=260.0,
        attack_cooldown=1.15,
        targets="ground",
        attack_type="splash",
        projectile_speed=400.0,
        ability=TowerAbility(splash_radius=50.0, armor_sunder=0.35, sunder_duration=4.0),
        description="Dunkelheit & Erde. Zerschlägt Rüstungen; getroffene Feinde erleiden 35% mehr Schaden.",
        sound_effect="earth_slam",
    ),

    # 10. Water + Fire: Steam Tower
    "steam": TowerDefinition(
        id="steam",
        name="Dampfturm (Steam)",
        category="dual",
        elements=[Element.WATER, Element.FIRE],
        tier=1,
        cost=200,
        range_px=140.0,
        damage=85.0,
        attack_cooldown=0.35,
        targets="both",
        attack_type="projectile",
        projectile_speed=520.0,
        description="Wasser & Feuer. Feuert kontinuierlich unter Hochdruck stehende Dampfgeschosse ab.",
        sound_effect="water_splash",
    ),

    # 11. Water + Nature: Geyser Tower
    "geyser": TowerDefinition(
        id="geyser",
        name="Geysirturm (Geyser)",
        category="dual",
        elements=[Element.WATER, Element.NATURE],
        tier=1,
        cost=200,
        range_px=145.0,
        damage=140.0,
        attack_cooldown=0.80,
        targets="ground",
        attack_type="splash",
        projectile_speed=440.0,
        ability=TowerAbility(splash_radius=60.0, slow_factor=0.30, slow_duration=3.0),
        description="Wasser & Natur. Schleudert kochende Wasserfontänen mit Flächenspritzer empor.",
        sound_effect="water_splash",
    ),

    # 12. Water + Earth: Mud Tower
    "mud": TowerDefinition(
        id="mud",
        name="Schlammturm (Mud)",
        category="dual",
        elements=[Element.WATER, Element.EARTH],
        tier=1,
        cost=200,
        range_px=135.0,
        damage=160.0,
        attack_cooldown=0.90,
        targets="ground",
        attack_type="splash",
        projectile_speed=390.0,
        ability=TowerAbility(slow_factor=0.45, slow_duration=3.0, splash_radius=55.0),
        description="Wasser & Erde. Zäher Schlamm hemmt die Schrittgeschwindigkeit um 45%.",
        sound_effect="earth_slam",
    ),

    # 13. Fire + Nature: Incineration Tower
    "incineration": TowerDefinition(
        id="incineration",
        name="Verbrennungsturm (Incineration)",
        category="dual",
        elements=[Element.FIRE, Element.NATURE],
        tier=1,
        cost=200,
        range_px=140.0,
        damage=150.0,
        attack_cooldown=0.75,
        targets="ground",
        attack_type="splash",
        projectile_speed=460.0,
        ability=TowerAbility(splash_radius=50.0, burn_dps=70.0, burn_duration=3.5),
        description="Feuer & Natur. Entzündet brennenden Waldboden, der Feinde röstet.",
        sound_effect="fire_blast",
    ),

    # 14. Fire + Earth: Magma Tower
    "magma": TowerDefinition(
        id="magma",
        name="Magmaturm (Magma)",
        category="dual",
        elements=[Element.FIRE, Element.EARTH],
        tier=1,
        cost=200,
        range_px=130.0,
        damage=280.0,
        attack_cooldown=1.20,
        targets="ground",
        attack_type="splash",
        projectile_speed=380.0,
        ability=TowerAbility(splash_radius=65.0, burn_dps=50.0, burn_duration=3.0),
        description="Feuer & Erde. Schießt glühendes Lavagestein mit gewaltigem Flächenkrater.",
        sound_effect="earth_slam",
    ),

    # 15. Nature + Earth: Roots Tower
    "roots": TowerDefinition(
        id="roots",
        name="Wurzelturm (Moss / Roots)",
        category="dual",
        elements=[Element.NATURE, Element.EARTH],
        tier=1,
        cost=200,
        range_px=140.0,
        damage=175.0,
        attack_cooldown=0.95,
        targets="ground",
        attack_type="splash",
        projectile_speed=410.0,
        ability=TowerAbility(splash_radius=50.0, slow_factor=0.40, slow_duration=3.0, stun_duration=0.25),
        description="Natur & Erde. Ranken schnüren Beine ein; verlangsamt um 40% und wurzelt kurz.",
        sound_effect="nature_shot",
    ),
}


# ==========================================
# 4. THE 20 TRIPLE-ELEMENT TOWERS
# ==========================================
# All 20 triplets from {Light, Darkness, Water, Fire, Nature, Earth}
TRIPLE_TOWERS: Dict[str, TowerDefinition] = {
    # 1. Light + Darkness + Water: Oblivion
    "oblivion": TowerDefinition(
        id="oblivion",
        name="Vergessenheitsturm (Oblivion)",
        category="triple",
        elements=[Element.LIGHT, Element.DARKNESS, Element.WATER],
        tier=1,
        cost=500,
        range_px=160.0,
        damage=380.0,
        attack_cooldown=0.75,
        targets="both",
        attack_type="splash",
        projectile_speed=460.0,
        ability=TowerAbility(splash_radius=60.0, slow_factor=0.35, slow_duration=3.0),
        description="Licht + Dunkelheit + Wasser. Gravitationsstrudel, der Lebenskraft absorbiert.",
        sound_effect="dark_pulse",
    ),

    # 2. Light + Darkness + Fire: Pure / Laser
    "laser": TowerDefinition(
        id="laser",
        name="Reinheitsturm / Laser (Pure)",
        category="triple",
        elements=[Element.LIGHT, Element.DARKNESS, Element.FIRE],
        tier=1,
        cost=500,
        range_px=190.0,
        damage=460.0,
        attack_cooldown=0.50,
        targets="both",
        attack_type="instant_beam",
        projectile_speed=0.0,
        description="Licht + Dunkelheit + Feuer. Hochenergetischer Schneidlaser mit brutalem Einzelschaden.",
        sound_effect="laser",
    ),

    # 3. Light + Darkness + Nature: Life
    "life": TowerDefinition(
        id="life",
        name="Lebensträger (Life)",
        category="triple",
        elements=[Element.LIGHT, Element.DARKNESS, Element.NATURE],
        tier=1,
        cost=500,
        range_px=165.0,
        damage=320.0,
        attack_cooldown=0.70,
        targets="both",
        attack_type="projectile",
        projectile_speed=520.0,
        ability=TowerAbility(poison_dps=120.0, poison_duration=4.0),
        description="Licht + Dunkelheit + Natur. Läuternde Lebensenergie, die dunkle Schrecken tilgt.",
        sound_effect="light_beam",
    ),

    # 4. Light + Darkness + Earth: Astral / Eclipse
    "eclipse": TowerDefinition(
        id="eclipse",
        name="Finsternisturm (Eclipse)",
        category="triple",
        elements=[Element.LIGHT, Element.DARKNESS, Element.EARTH],
        tier=1,
        cost=500,
        range_px=170.0,
        damage=450.0,
        attack_cooldown=0.90,
        targets="both",
        attack_type="splash",
        projectile_speed=480.0,
        ability=TowerAbility(splash_radius=65.0, stun_duration=0.35),
        description="Licht + Dunkelheit + Erde. Kosmische Schockwellen zwischen Mond und Sonne.",
        sound_effect="earth_slam",
    ),

    # 5. Light + Water + Fire: Prisma
    "prisma": TowerDefinition(
        id="prisma",
        name="Prismaturm (Prisma)",
        category="triple",
        elements=[Element.LIGHT, Element.WATER, Element.FIRE],
        tier=1,
        cost=500,
        range_px=180.0,
        damage=310.0,
        attack_cooldown=0.60,
        targets="both",
        attack_type="chain",
        projectile_speed=0.0,
        ability=TowerAbility(chain_bounces=5, chain_decay=0.88),
        description="Licht + Wasser + Feuer. Bricht Licht in Regentropfen und feuert Regenbogen-Blitze.",
        sound_effect="electric_zap",
    ),

    # 6. Light + Water + Nature: Wellspring
    "wellspring": TowerDefinition(
        id="wellspring",
        name="Quellturm (Wellspring)",
        category="triple",
        elements=[Element.LIGHT, Element.WATER, Element.NATURE],
        tier=1,
        cost=500,
        range_px=160.0,
        damage=280.0,
        attack_cooldown=0.65,
        targets="both",
        attack_type="splash",
        projectile_speed=460.0,
        ability=TowerAbility(splash_radius=55.0, slow_factor=0.35, slow_duration=3.0),
        description="Licht + Wasser + Natur. Erfrischende Heilquelle, die Kaskaden heiligen Wassers sprudelt.",
        sound_effect="water_splash",
    ),

    # 7. Light + Water + Earth: Polar
    "polar": TowerDefinition(
        id="polar",
        name="Polarturm (Polar)",
        category="triple",
        elements=[Element.LIGHT, Element.WATER, Element.EARTH],
        tier=1,
        cost=500,
        range_px=155.0,
        damage=340.0,
        attack_cooldown=0.85,
        targets="both",
        attack_type="splash",
        projectile_speed=440.0,
        ability=TowerAbility(slow_factor=0.60, slow_duration=4.0, splash_radius=60.0),
        description="Licht + Wasser + Erde. Arktischer Schneesturm, der Feinde um unglaubliche 60% verlangsamt.",
        sound_effect="ice_freeze",
    ),

    # 8. Light + Fire + Nature: Solar Flare
    "solar_flare": TowerDefinition(
        id="solar_flare",
        name="Sonneneruption (Solar Flare)",
        category="triple",
        elements=[Element.LIGHT, Element.FIRE, Element.NATURE],
        tier=1,
        cost=500,
        range_px=175.0,
        damage=390.0,
        attack_cooldown=0.75,
        targets="both",
        attack_type="splash",
        projectile_speed=490.0,
        ability=TowerAbility(splash_radius=65.0, burn_dps=110.0, burn_duration=3.5),
        description="Licht + Feuer + Natur. Explosive Sonnenprotuberanzen mit flächendeckendem Flächenbrand.",
        sound_effect="fire_blast",
    ),

    # 9. Light + Fire + Earth: Forge
    "forge": TowerDefinition(
        id="forge",
        name="Sonnenschmiede (Forge)",
        category="triple",
        elements=[Element.LIGHT, Element.FIRE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=145.0,
        damage=520.0,
        attack_cooldown=1.10,
        targets="ground",
        attack_type="splash",
        projectile_speed=420.0,
        ability=TowerAbility(splash_radius=75.0, burn_dps=80.0, burn_duration=3.0),
        description="Licht + Feuer + Erde. Schmiedet weißglühende Sonnengeschosse mit riesigem Splitterradius.",
        sound_effect="earth_slam",
    ),

    # 10. Light + Nature + Earth: Gaia
    "gaia": TowerDefinition(
        id="gaia",
        name="Gaiaturm (Ephemeral / Gaia)",
        category="triple",
        elements=[Element.LIGHT, Element.NATURE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=165.0,
        damage=360.0,
        attack_cooldown=0.70,
        targets="both",
        attack_type="projectile",
        projectile_speed=520.0,
        ability=TowerAbility(slow_factor=0.30, slow_duration=2.5, poison_dps=85.0, poison_duration=3.0),
        description="Licht + Natur + Erde. Ruft die Urmächte der Erde an, um Feinde zu umschlingen.",
        sound_effect="nature_shot",
    ),

    # 11. Darkness + Water + Fire: Nether / Abyssal
    "abyssal": TowerDefinition(
        id="abyssal",
        name="Abgrundturm (Abyssal)",
        category="triple",
        elements=[Element.DARKNESS, Element.WATER, Element.FIRE],
        tier=1,
        cost=500,
        range_px=150.0,
        damage=370.0,
        attack_cooldown=0.80,
        targets="both",
        attack_type="splash",
        projectile_speed=460.0,
        ability=TowerAbility(splash_radius=60.0, burn_dps=90.0, burn_duration=3.0, slow_factor=0.25, slow_duration=2.5),
        description="Dunkelheit + Wasser + Feuer. Schwarzes Seefeuer, das brennt und gleichzeitig kühlt.",
        sound_effect="fire_blast",
    ),

    # 12. Darkness + Water + Nature: Plague
    "plague": TowerDefinition(
        id="plague",
        name="Pestturm (Plague)",
        category="triple",
        elements=[Element.DARKNESS, Element.WATER, Element.NATURE],
        tier=1,
        cost=500,
        range_px=155.0,
        damage=260.0,
        attack_cooldown=0.65,
        targets="both",
        attack_type="splash",
        projectile_speed=470.0,
        ability=TowerAbility(splash_radius=55.0, poison_dps=180.0, poison_duration=6.0),
        description="Dunkelheit + Wasser + Natur. Hochinfektiöse Pestseuche mit gewaltigem Gifttick.",
        sound_effect="nature_shot",
    ),

    # 13. Darkness + Water + Earth: Mire
    "mire": TowerDefinition(
        id="mire",
        name="Morastturm (Mire)",
        category="triple",
        elements=[Element.DARKNESS, Element.WATER, Element.EARTH],
        tier=1,
        cost=500,
        range_px=140.0,
        damage=330.0,
        attack_cooldown=0.90,
        targets="ground",
        attack_type="splash",
        projectile_speed=400.0,
        ability=TowerAbility(slow_factor=0.55, slow_duration=3.5, splash_radius=65.0),
        description="Dunkelheit + Wasser + Erde. Zieht Monster in dunklen Treibsand und drosselt sie um 55%.",
        sound_effect="earth_slam",
    ),

    # 14. Darkness + Fire + Nature: Corrosion
    "corrosion": TowerDefinition(
        id="corrosion",
        name="Korrosionsturm (Corrosion)",
        category="triple",
        elements=[Element.DARKNESS, Element.FIRE, Element.NATURE],
        tier=1,
        cost=500,
        range_px=150.0,
        damage=350.0,
        attack_cooldown=0.75,
        targets="both",
        attack_type="projectile",
        projectile_speed=480.0,
        ability=TowerAbility(armor_sunder=0.50, sunder_duration=4.5, burn_dps=80.0, burn_duration=3.0),
        description="Dunkelheit + Feuer + Natur. Ätzt Rüstung weg: getroffene Gegner nehmen 50% mehr Schaden!",
        sound_effect="nature_shot",
    ),

    # 15. Darkness + Fire + Earth: Meteor
    "meteor": TowerDefinition(
        id="meteor",
        name="Meteorturm (Meteor)",
        category="triple",
        elements=[Element.DARKNESS, Element.FIRE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=160.0,
        damage=680.0,
        attack_cooldown=1.40,
        targets="ground",
        attack_type="splash",
        projectile_speed=390.0,
        ability=TowerAbility(splash_radius=85.0, burn_dps=100.0, burn_duration=3.5, stun_duration=0.4),
        description="Dunkelheit + Feuer + Erde. Beschwört brennende Kometen mit kataklysmischem Krater.",
        sound_effect="earth_slam",
    ),

    # 16. Darkness + Nature + Earth: Rot
    "rot": TowerDefinition(
        id="rot",
        name="Verwesungsturm (Rot)",
        category="triple",
        elements=[Element.DARKNESS, Element.NATURE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=145.0,
        damage=310.0,
        attack_cooldown=0.80,
        targets="ground",
        attack_type="splash",
        projectile_speed=420.0,
        ability=TowerAbility(splash_radius=60.0, poison_dps=140.0, poison_duration=4.5, slow_factor=0.35, slow_duration=3.0),
        description="Dunkelheit + Natur + Erde. Zersetzende Fäulnis, die Fleisch auflöst und Monster bremst.",
        sound_effect="nature_shot",
    ),

    # 17. Water + Fire + Nature: Biohazard
    "biohazard": TowerDefinition(
        id="biohazard",
        name="Gefahrgutturm (Biohazard)",
        category="triple",
        elements=[Element.WATER, Element.FIRE, Element.NATURE],
        tier=1,
        cost=500,
        range_px=150.0,
        damage=360.0,
        attack_cooldown=0.70,
        targets="both",
        attack_type="splash",
        projectile_speed=460.0,
        ability=TowerAbility(splash_radius=60.0, poison_dps=100.0, poison_duration=3.5, burn_dps=70.0, burn_duration=3.0),
        description="Wasser + Feuer + Natur. Instabiles biochemisches Gemisch, das brennt und vergiftet.",
        sound_effect="fire_blast",
    ),

    # 18. Water + Fire + Earth: Obsidian
    "obsidian": TowerDefinition(
        id="obsidian",
        name="Obsidianturm (Obsidian)",
        category="triple",
        elements=[Element.WATER, Element.FIRE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=145.0,
        damage=490.0,
        attack_cooldown=1.05,
        targets="ground",
        attack_type="projectile",
        projectile_speed=520.0,
        ability=TowerAbility(splash_radius=50.0, armor_sunder=0.30, sunder_duration=4.0),
        description="Wasser + Feuer + Erde. Pfeilscharfe Vulkanglas-Stacheln, die Rüstungen durchschlagen.",
        sound_effect="earth_slam",
    ),

    # 19. Water + Nature + Earth: Tsunami
    "tsunami": TowerDefinition(
        id="tsunami",
        name="Tsunamiturm (Tsunami)",
        category="triple",
        elements=[Element.WATER, Element.NATURE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=155.0,
        damage=370.0,
        attack_cooldown=0.95,
        targets="ground",
        attack_type="splash",
        projectile_speed=430.0,
        ability=TowerAbility(splash_radius=75.0, slow_factor=0.50, slow_duration=3.5, knockback_dist=25.0),
        description="Wasser + Natur + Erde. Gewaltige Flutwelle, die Bodengegner im Gang zurückwirft!",
        sound_effect="water_splash",
    ),

    # 20. Fire + Nature + Earth: Juggernaut
    "juggernaut": TowerDefinition(
        id="juggernaut",
        name="Kollossturm (Juggernaut)",
        category="triple",
        elements=[Element.FIRE, Element.NATURE, Element.EARTH],
        tier=1,
        cost=500,
        range_px=140.0,
        damage=620.0,
        attack_cooldown=1.25,
        targets="ground",
        attack_type="splash",
        projectile_speed=400.0,
        ability=TowerAbility(splash_radius=80.0, burn_dps=120.0, burn_duration=3.5, stun_duration=0.5),
        description="Feuer + Natur + Erde. Urtümliche Lavakolosse mit verheerender seismischer Schockwelle.",
        sound_effect="earth_slam",
    ),
}


# Combine all towers into a single dictionary
ALL_TOWERS: Dict[str, TowerDefinition] = {
    **STARTER_TOWERS,
    **BASE_ELEMENTAL_TOWERS,
    **DUAL_TOWERS,
    **TRIPLE_TOWERS,
}


def get_tower_def(tower_id: str) -> Optional[TowerDefinition]:
    """Retrieve definition by unique ID."""
    return ALL_TOWERS.get(tower_id)


def get_available_towers(unlocked_elements: Dict[Element, int]) -> List[TowerDefinition]:
    """Return all towers that the player has unlocked based on their elemental essence counts.

    unlocked_elements maps Element -> essence level (1, 2, 3...)
    """
    available: List[TowerDefinition] = []

    for t in ALL_TOWERS.values():
        if t.category == "starter":
            # Starter towers (only tier 1 can be built directly; tier 2/3 are upgrades)
            if t.tier == 1:
                available.append(t)
        elif t.category == "base":
            # Base elemental towers require at least t.tier essences in that element
            elem = t.elements[0]
            if unlocked_elements.get(elem, 0) >= t.tier:
                if t.tier == 1:
                    available.append(t)
        elif t.category in ("dual", "triple"):
            # Combinations require at least 1 essence of EACH component element
            has_all = all(unlocked_elements.get(req_elem, 0) >= 1 for req_elem in t.elements)
            if has_all:
                available.append(t)

    return available
