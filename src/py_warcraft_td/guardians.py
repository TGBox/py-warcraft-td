"""Elemental Guardian summoning altar and boss battle logic."""

from typing import Dict, List, Optional, Tuple
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import Element, ELEMENT_NAMES_DE, get_element_color
from py_warcraft_td.pathfinding import GridCoord


class GuardianManager:
    """Manages summoning tokens, elemental essence inventory, and guardian bosses."""

    def __init__(self):
        # Essences collected per element: {Element.LIGHT: 1, ...}
        self.essences: Dict[Element, int] = {
            Element.LIGHT: 0,
            Element.DARKNESS: 0,
            Element.WATER: 0,
            Element.FIRE: 0,
            Element.NATURE: 0,
            Element.EARTH: 0,
        }
        self.available_tokens: int = 0
        self.total_guardians_defeated: int = 0
        self.interest_bonus: float = 0.0  # Extra interest accumulated by taking interest instead of element

    def add_token(self) -> None:
        """Award a guardian summoning token (granted every 5 waves)."""
        self.available_tokens += 1

    def can_summon(self) -> bool:
        return self.available_tokens > 0

    def summon_guardian(
        self,
        elem: Element,
        wave_num: int,
        path: List[GridCoord],
    ) -> Optional[Creep]:
        """Spend a token and create an Elemental Guardian Boss."""
        if self.available_tokens <= 0:
            return None

        self.available_tokens -= 1
        elem_name = ELEMENT_NAMES_DE.get(elem, "Element")

        # Guardian HP scales with current wave progression
        tier = self.essences.get(elem, 0) + 1
        guardian_hp = 350.0 * (1.14 ** (wave_num - 1)) * (1.0 + tier * 0.25)

        boss_creep = Creep(
            creep_id=-int(wave_num * 100 + tier), # negative ID identifies guardian
            name=f"Wächter: {elem_name} (Stufe {tier})",
            wave_num=wave_num,
            max_hp=guardian_hp,
            speed=50.0,
            armor_element=elem,
            gold_reward=40 + wave_num * 5,
            is_flying=False,
            modifier="boss",
            path=path,
        )
        return boss_creep

    def choose_interest_upgrade(self) -> float:
        """Spend a token to increase interest rate permanently by +0.5%."""
        if self.available_tokens <= 0:
            return 0.0
        self.available_tokens -= 1
        self.interest_bonus += 0.005
        return 0.005

    def on_guardian_killed(self, elem: Element) -> Tuple[int, str]:
        """Grant essence for defeated guardian."""
        self.essences[elem] = self.essences.get(elem, 0) + 1
        self.total_guardians_defeated += 1
        new_tier = self.essences[elem]
        elem_name = ELEMENT_NAMES_DE.get(elem, "Element")
        msg = f"{elem_name}-Essenz Stufe {new_tier} erlangt!"
        return (new_tier, msg)
