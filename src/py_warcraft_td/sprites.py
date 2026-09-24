"""Procedural sprite generator for creeps, bosses, and towers.

Generates high-detail, resolution-independent stylized top-down sprites
with elemental layering, shading, and visual cues.
"""

import math
from typing import Dict, List, Optional, Tuple
import pygame
from py_warcraft_td.elements import Element, get_element_color
from py_warcraft_td.towers.tower_catalog import TowerDefinition


class SpriteRenderer:
    """Generates and caches rich procedural sprites for towers, creeps, and bosses."""

    _tower_cache: Dict[Tuple[str, int, bool], pygame.Surface] = {}
    _creep_cache: Dict[Tuple[str, str, bool, int, int], pygame.Surface] = {}

    # -------------------------------------------------------------
    # TOWER SPRITE GENERATION
    # -------------------------------------------------------------
    @classmethod
    def get_tower_sprite(cls, tower_def: TowerDefinition, size: int, is_selected: bool = False) -> pygame.Surface:
        key = (tower_def.id, size, is_selected)
        if key in cls._tower_cache:
            return cls._tower_cache[key]

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cls._render_tower(surf, tower_def, size, is_selected)
        cls._tower_cache[key] = surf
        return surf

    @classmethod
    def _render_tower(cls, surf: pygame.Surface, tdef: TowerDefinition, s: int, is_sel: bool) -> None:
        cx, cy = s / 2.0, s / 2.0
        tier = tdef.tier
        elem = tdef.elements[0] if tdef.elements else Element.NONE
        pri_col, sec_col = get_element_color(elem)

        # 1. Base Pedestal (Stone foundation)
        base_inset = 2
        base_rect = pygame.Rect(base_inset, base_inset, s - base_inset * 2, s - base_inset * 2)
        stone_dark = (32, 38, 50)
        stone_light = (58, 68, 88)
        stone_border = (20, 24, 32)

        # Foundation bevels
        pygame.draw.rect(surf, stone_dark, base_rect, border_radius=6)
        inner_rect = base_rect.inflate(-4, -4)
        pygame.draw.rect(surf, stone_light, inner_rect, border_radius=4)
        pygame.draw.rect(surf, stone_border, base_rect, width=1, border_radius=6)

        # 2. Elemental Runic Flooring / Inscription
        rune_rect = inner_rect.inflate(-4, -4)
        pygame.draw.rect(surf, sec_col, rune_rect, border_radius=3)
        core_rect = rune_rect.inflate(-4, -4)
        pygame.draw.rect(surf, (stone_dark[0] + 15, stone_dark[1] + 15, stone_dark[2] + 20), core_rect, border_radius=2)

        # 3. Category & Weapon Top
        cat = tdef.category
        if cat == "starter":
            if "arrow" in tdef.id:
                # Archery battlement & Crossbow
                # Wooden turret rim
                wood_col = (130, 85, 45)
                wood_light = (175, 120, 65)
                pygame.draw.circle(surf, wood_col, (cx, cy), s * 0.28)
                pygame.draw.circle(surf, wood_light, (cx, cy), s * 0.22)
                # Crossbow arms
                bow_col = (210, 220, 230)
                pygame.draw.arc(surf, bow_col, (cx - s * 0.25, cy - s * 0.25, s * 0.5, s * 0.5), -0.2, math.pi + 0.2, max(2, int(s * 0.08)))
                # Arrow bolt
                pygame.draw.line(surf, (255, 230, 150), (cx, cy + s * 0.15), (cx, cy - s * 0.35), max(2, int(s * 0.07)))
                # Arrowhead
                pygame.draw.polygon(surf, (240, 240, 255), [(cx, cy - s * 0.40), (cx - 3, cy - s * 0.28), (cx + 3, cy - s * 0.28)])
            else:
                # Heavy Iron Cannon Mortar
                iron_dark = (45, 52, 65)
                iron_light = (85, 95, 115)
                # Mortar ring
                pygame.draw.circle(surf, iron_dark, (cx, cy), s * 0.32)
                pygame.draw.circle(surf, iron_light, (cx, cy), s * 0.26)
                # Barrel hole
                pygame.draw.circle(surf, (15, 18, 22), (cx, cy), s * 0.15)
                # Rivets
                for angle in (0, math.pi/2, math.pi, 3*math.pi/2):
                    rx = cx + math.cos(angle) * (s * 0.28)
                    ry = cy + math.sin(angle) * (s * 0.28)
                    pygame.draw.circle(surf, (200, 210, 225), (rx, ry), 1.5)

        elif cat == "base":
            # Elemental spire or obelisk
            spire_r = s * 0.26
            pygame.draw.circle(surf, sec_col, (cx, cy), spire_r)
            # Floating glowing crystal core
            c_r = s * 0.18
            pygame.draw.circle(surf, pri_col, (cx, cy), c_r)
            # Specular shine
            pygame.draw.circle(surf, (255, 255, 255), (cx - c_r * 0.35, cy - c_r * 0.35), max(1.5, c_r * 0.3))

        elif cat == "dual":
            # Dual elemental composite
            sec_elem = tdef.elements[1] if len(tdef.elements) > 1 else elem
            sec_pri, _ = get_element_color(sec_elem)
            # Left half primary, right half secondary
            pygame.draw.circle(surf, sec_col, (cx, cy), s * 0.30)
            # Two intertwining energy orbs
            pygame.draw.circle(surf, pri_col, (cx - s * 0.1, cy), s * 0.14)
            pygame.draw.circle(surf, sec_pri, (cx + s * 0.1, cy), s * 0.14)
            # Core connection
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), s * 0.08)

        else: # "triple"
            # Master triple tri-force / runic trinity
            e1 = tdef.elements[0]
            e2 = tdef.elements[1] if len(tdef.elements) > 1 else e1
            e3 = tdef.elements[2] if len(tdef.elements) > 2 else e1
            c1, _ = get_element_color(e1)
            c2, _ = get_element_color(e2)
            c3, _ = get_element_color(e3)

            # Outer runic ring
            pygame.draw.circle(surf, (40, 50, 70), (cx, cy), s * 0.33)
            pygame.draw.circle(surf, (255, 235, 120), (cx, cy), s * 0.33, width=1)
            # 3 orbiting elemental gems
            r_orb = s * 0.18
            for i, c_elem in enumerate([c1, c2, c3]):
                ang = i * (2 * math.pi / 3.0) - math.pi / 2.0
                gx = cx + math.cos(ang) * r_orb
                gy = cy + math.sin(ang) * r_orb
                pygame.draw.circle(surf, c_elem, (gx, gy), s * 0.10)
                pygame.draw.circle(surf, (255, 255, 255), (gx, gy), max(1.0, s * 0.04))
            # Center nexus
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), s * 0.07)

        # 4. Tier Indicators (Gold/Diamond pips)
        for t in range(tier):
            pip_x = base_rect.left + 5 + t * 6
            pip_y = base_rect.bottom - 6
            pygame.draw.circle(surf, (255, 230, 80), (pip_x, pip_y), 2.5)
            pygame.draw.circle(surf, (20, 20, 25), (pip_x, pip_y), 2.5, width=1)

        # 5. Selection highlight
        if is_sel:
            pygame.draw.rect(surf, (255, 240, 90), base_rect, width=2, border_radius=6)

    # -------------------------------------------------------------
    # CREEP SPRITE GENERATION
    # -------------------------------------------------------------
    @classmethod
    def get_creep_sprite(
        cls,
        armor_element: Element,
        modifier: str,
        is_flying: bool,
        size: int,
        anim_frame: int = 0,
    ) -> pygame.Surface:
        key = (armor_element.value, modifier, is_flying, size, anim_frame % 4)
        if key in cls._creep_cache:
            return cls._creep_cache[key]

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cls._render_creep(surf, armor_element, modifier, is_flying, size, anim_frame)
        cls._creep_cache[key] = surf
        return surf

    @classmethod
    def _render_creep(
        cls,
        surf: pygame.Surface,
        elem: Element,
        mod: str,
        is_fly: bool,
        s: int,
        frame: int,
    ) -> None:
        cx, cy = s / 2.0, s / 2.0
        pri_col, sec_col = get_element_color(elem)

        # Subtle breathing/stepping pulse
        pulse = math.sin(frame * math.pi / 2.0) * (s * 0.04)

        if mod == "boss":
            # --- BOSS / GUARDIAN TITAN ---
            # Outer Elemental Aura
            aura_r = s * 0.44 + pulse
            pygame.draw.circle(surf, (*pri_col, 80), (cx, cy), aura_r)
            pygame.draw.circle(surf, pri_col, (cx, cy), aura_r, width=2)

            # Heavy Basalt Armor Plates
            armor_pts = [
                (cx, cy - s * 0.38),
                (cx + s * 0.34, cy - s * 0.15),
                (cx + s * 0.30, cy + s * 0.28),
                (cx, cy + s * 0.38),
                (cx - s * 0.30, cy + s * 0.28),
                (cx - s * 0.34, cy - s * 0.15),
            ]
            pygame.draw.polygon(surf, sec_col, armor_pts)
            pygame.draw.polygon(surf, (20, 24, 30), armor_pts, width=2)

            # Golden Runic Crown
            crown_pts = [
                (cx - s * 0.20, cy - s * 0.30),
                (cx - s * 0.12, cy - s * 0.48),
                (cx, cy - s * 0.36),
                (cx + s * 0.12, cy - s * 0.48),
                (cx + s * 0.20, cy - s * 0.30),
            ]
            pygame.draw.polygon(surf, (255, 215, 45), crown_pts)

            # Core Elemental Hearth
            pygame.draw.circle(surf, pri_col, (cx, cy), s * 0.16)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), s * 0.08)

            # Piercing Eyes
            eye_y = cy - s * 0.12
            pygame.draw.circle(surf, (255, 255, 100), (cx - s * 0.10, eye_y), max(1.5, s * 0.05))
            pygame.draw.circle(surf, (255, 255, 100), (cx + s * 0.10, eye_y), max(1.5, s * 0.05))

        elif is_fly:
            # --- FLYING UNITS (Gargoyles / Eagles / Dragons) ---
            # Ground drop shadow underneath
            shadow_rect = pygame.Rect(cx - s * 0.25, cy + s * 0.20, s * 0.50, s * 0.20)
            pygame.draw.ellipse(surf, (10, 12, 16, 90), shadow_rect)

            # Wing flap angle based on frame
            wing_flap = math.sin(frame * math.pi / 2.0) * (s * 0.10)
            wing_col = (pri_col[0], pri_col[1], min(255, pri_col[2] + 40))

            # Left wing
            left_wing = [
                (cx - s * 0.05, cy - s * 0.05),
                (cx - s * 0.44, cy - s * 0.25 + wing_flap),
                (cx - s * 0.38, cy + s * 0.10 + wing_flap),
                (cx - s * 0.08, cy + s * 0.15),
            ]
            pygame.draw.polygon(surf, wing_col, left_wing)
            pygame.draw.polygon(surf, sec_col, left_wing, width=1)

            # Right wing
            right_wing = [
                (cx + s * 0.05, cy - s * 0.05),
                (cx + s * 0.44, cy - s * 0.25 + wing_flap),
                (cx + s * 0.38, cy + s * 0.10 + wing_flap),
                (cx + s * 0.08, cy + s * 0.15),
            ]
            pygame.draw.polygon(surf, wing_col, right_wing)
            pygame.draw.polygon(surf, sec_col, right_wing, width=1)

            # Beast Body & Head
            pygame.draw.ellipse(surf, sec_col, (cx - s * 0.12, cy - s * 0.22, s * 0.24, s * 0.44))
            pygame.draw.circle(surf, pri_col, (cx, cy - s * 0.16), s * 0.10)
            # Glowing Eyes
            pygame.draw.circle(surf, (255, 255, 255), (cx - 2, cy - s * 0.18), 1.5)
            pygame.draw.circle(surf, (255, 255, 255), (cx + 2, cy - s * 0.18), 1.5)

        elif mod == "fast":
            # --- FAST RUNNER (Wolf / Raptor) ---
            # Sleek aerodynamic body
            body_pts = [
                (cx, cy - s * 0.35),
                (cx + s * 0.18, cy + s * 0.05),
                (cx + s * 0.10, cy + s * 0.32),
                (cx - s * 0.10, cy + s * 0.32),
                (cx - s * 0.18, cy + s * 0.05),
            ]
            pygame.draw.polygon(surf, pri_col, body_pts)
            pygame.draw.polygon(surf, sec_col, body_pts, width=1)
            # Sharp Ears / Crest
            pygame.draw.polygon(surf, sec_col, [(cx - s * 0.12, cy - s * 0.20), (cx - s * 0.18, cy - s * 0.42), (cx - s * 0.04, cy - s * 0.30)])
            pygame.draw.polygon(surf, sec_col, [(cx + s * 0.12, cy - s * 0.20), (cx + s * 0.18, cy - s * 0.42), (cx + s * 0.04, cy - s * 0.30)])
            # Speed stripe
            pygame.draw.line(surf, (255, 255, 255), (cx, cy - s * 0.25), (cx, cy + s * 0.15), max(1, int(s * 0.06)))

        elif mod == "tank":
            # --- TANK / HEAVY (Ogre / Colossus) ---
            # Massive square silhouette with boulder shoulderpads
            tank_w = s * 0.36
            tank_h = s * 0.36
            pygame.draw.rect(surf, sec_col, (cx - tank_w, cy - tank_h, tank_w * 2, tank_h * 2), border_radius=5)
            pygame.draw.rect(surf, pri_col, (cx - tank_w + 3, cy - tank_h + 3, (tank_w - 3) * 2, (tank_h - 3) * 2), border_radius=3)
            # Iron spikes / plates
            pygame.draw.line(surf, (40, 45, 55), (cx - tank_w, cy), (cx + tank_w, cy), 2)
            pygame.draw.circle(surf, (255, 255, 200), (cx - s * 0.12, cy - s * 0.10), max(2.0, s * 0.07))
            pygame.draw.circle(surf, (255, 255, 200), (cx + s * 0.12, cy - s * 0.10), max(2.0, s * 0.07))

        elif mod == "swarm":
            # --- SWARM (Insectoid / Horde) ---
            # Compact multi-legged crawler
            r_swarm = s * 0.24
            pygame.draw.circle(surf, pri_col, (cx, cy), r_swarm)
            pygame.draw.circle(surf, sec_col, (cx, cy), r_swarm, width=1)
            # 4 little legs
            leg_len = s * 0.16
            for ang in (math.pi*0.25, math.pi*0.75, math.pi*1.25, math.pi*1.75):
                lx = cx + math.cos(ang) * (r_swarm + leg_len)
                ly = cy + math.sin(ang) * (r_swarm + leg_len)
                pygame.draw.line(surf, sec_col, (cx, cy), (lx, ly), 1)

        else:
            # --- STANDARD GROUND MINION ---
            body_r = s * 0.30
            pygame.draw.circle(surf, pri_col, (cx, cy), body_r)
            pygame.draw.circle(surf, sec_col, (cx, cy), body_r, width=2)
            # Elemental Rune Core
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), max(2.0, s * 0.10))
            # Eyes
            pygame.draw.circle(surf, (20, 24, 30), (cx - s * 0.08, cy - s * 0.08), max(1.5, s * 0.06))
            pygame.draw.circle(surf, (20, 24, 30), (cx + s * 0.08, cy - s * 0.08), max(1.5, s * 0.06))
