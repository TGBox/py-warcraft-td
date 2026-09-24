"""Procedural vector icon renderer.

Replaces missing system font emoji/unicode tofu boxes with crisp, high-contrast
procedural vector icons rendered directly onto transparent Pygame surfaces.
"""

import math
from typing import Dict, Optional, Tuple
import pygame
from py_warcraft_td.elements import Element, get_element_color


class IconRenderer:
    """Generates and caches crisp vector icons at requested pixel sizes."""

    _cache: Dict[Tuple[str, int], pygame.Surface] = {}

    @classmethod
    def get_icon(cls, name: str, size: int = 20) -> pygame.Surface:
        """Retrieve or render a cached icon surface."""
        key = (name.lower(), size)
        if key in cls._cache:
            return cls._cache[key]

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cls._render_icon(surf, name.lower(), size)
        cls._cache[key] = surf
        return surf

    @classmethod
    def _render_icon(cls, surf: pygame.Surface, name: str, s: int) -> None:
        cx, cy = s / 2.0, s / 2.0

        if name == "gold":
            # Gold coin with rim and specular glint
            r = s * 0.44
            pygame.draw.circle(surf, (180, 130, 20), (cx, cy), r)
            pygame.draw.circle(surf, (255, 215, 40), (cx, cy), r - 1.5)
            pygame.draw.circle(surf, (220, 170, 30), (cx, cy), r * 0.7, width=1)
            # Specular shine
            pygame.draw.circle(surf, (255, 255, 200), (cx - r * 0.3, cy - r * 0.3), max(1.0, r * 0.2))

        elif name == "heart":
            # Stylized ruby heart
            # Two circles on top + triangle at bottom
            r = s * 0.22
            top_y = cy - s * 0.1
            left_cx = cx - r * 0.95
            right_cx = cx + r * 0.95
            bot_y = cy + s * 0.38

            # Triangle base
            pts = [(cx - s * 0.42, top_y), (cx + s * 0.42, top_y), (cx, bot_y)]
            pygame.draw.polygon(surf, (225, 45, 65), pts)
            pygame.draw.circle(surf, (245, 60, 80), (left_cx, top_y), r)
            pygame.draw.circle(surf, (245, 60, 80), (right_cx, top_y), r)
            # Specular glint
            pygame.draw.circle(surf, (255, 180, 190), (left_cx - 1, top_y - 1), max(1.0, r * 0.35))

        elif name == "swords":
            # Crossed silver blades with golden guard
            blade_col = (220, 230, 245)
            gold_col = (240, 190, 40)
            # Blade 1 (top-left to bottom-right)
            pygame.draw.line(surf, blade_col, (s * 0.2, s * 0.2), (s * 0.75, s * 0.75), max(2, int(s * 0.1)))
            pygame.draw.line(surf, gold_col, (s * 0.65, s * 0.8), (s * 0.8, s * 0.65), max(2, int(s * 0.1)))
            # Blade 2 (top-right to bottom-left)
            pygame.draw.line(surf, blade_col, (s * 0.8, s * 0.2), (s * 0.25, s * 0.75), max(2, int(s * 0.1)))
            pygame.draw.line(surf, gold_col, (s * 0.35, s * 0.8), (s * 0.2, s * 0.65), max(2, int(s * 0.1)))

        elif name == "wings" or name == "fly":
            # Majestic spread eagle wings
            wing_col = (235, 245, 255)
            # Left wing arc
            pygame.draw.arc(surf, wing_col, (s * 0.05, s * 0.2, s * 0.45, s * 0.5), 0.2, math.pi * 0.9, max(2, int(s * 0.1)))
            # Right wing arc
            pygame.draw.arc(surf, wing_col, (s * 0.5, s * 0.2, s * 0.45, s * 0.5), 0.1 * math.pi, 0.8 * math.pi, max(2, int(s * 0.1)))
            # Feather tip
            pygame.draw.line(surf, wing_col, (s * 0.1, s * 0.25), (s * 0.48, s * 0.6), max(1, int(s * 0.08)))
            pygame.draw.line(surf, wing_col, (s * 0.9, s * 0.25), (s * 0.52, s * 0.6), max(1, int(s * 0.08)))

        elif name == "lock":
            # Brass padlock
            # Shackle
            shackle_r = s * 0.2
            pygame.draw.arc(surf, (200, 205, 215), (cx - shackle_r, cy - s * 0.42, shackle_r * 2, shackle_r * 2), 0, math.pi, max(2, int(s * 0.1)))
            # Body
            body_w = s * 0.55
            body_h = s * 0.42
            body_rect = pygame.Rect(cx - body_w / 2.0, cy - s * 0.05, body_w, body_h)
            pygame.draw.rect(surf, (215, 165, 35), body_rect, border_radius=3)
            # Keyhole
            pygame.draw.circle(surf, (30, 25, 15), (cx, cy + s * 0.1), max(1.5, s * 0.08))
            pygame.draw.line(surf, (30, 25, 15), (cx, cy + s * 0.1), (cx, cy + s * 0.22), max(1, int(s * 0.08)))

        elif name == "lightning" or name == "electric":
            # Bolt of lightning
            bolt_col = (255, 240, 70)
            pts = [
                (cx + s * 0.1, s * 0.1),
                (cx - s * 0.25, cy),
                (cx + s * 0.05, cy),
                (cx - s * 0.15, s * 0.9),
                (cx + s * 0.3, cy - s * 0.1),
                (cx + s * 0.0, cy - s * 0.1),
            ]
            pygame.draw.polygon(surf, bolt_col, pts)

        elif name == "arrow_up" or name == "upgrade":
            # Neon green upgrade chevron
            col = (90, 235, 110)
            pts = [
                (cx, s * 0.15),
                (cx + s * 0.35, s * 0.5),
                (cx + s * 0.18, s * 0.5),
                (cx + s * 0.18, s * 0.85),
                (cx - s * 0.18, s * 0.85),
                (cx - s * 0.18, s * 0.5),
                (cx - s * 0.35, s * 0.5),
            ]
            pygame.draw.polygon(surf, col, pts)

        elif name == "cross" or name == "close":
            # Red cancel X
            col = (245, 75, 75)
            w = max(2, int(s * 0.12))
            pygame.draw.line(surf, col, (s * 0.2, s * 0.2), (s * 0.8, s * 0.8), w)
            pygame.draw.line(surf, col, (s * 0.8, s * 0.2), (s * 0.2, s * 0.8), w)

        elif name == "eraser" or name == "demolish":
            # Angled eraser with rubber block and silver sleeve
            # Main eraser body (salmon pink)
            pts = [
                (s * 0.25, s * 0.70),
                (s * 0.60, s * 0.20),
                (s * 0.80, s * 0.35),
                (s * 0.45, s * 0.85),
            ]
            pygame.draw.polygon(surf, (255, 110, 130), pts)
            # Bevel/tip
            pygame.draw.polygon(surf, (240, 80, 100), [(s * 0.25, s * 0.70), (s * 0.15, s * 0.85), (s * 0.35, s * 0.92), (s * 0.45, s * 0.85)])
            # Silver metal/paper sleeve
            sleeve = [
                (s * 0.48, s * 0.37),
                (s * 0.65, s * 0.13),
                (s * 0.85, s * 0.28),
                (s * 0.68, s * 0.52),
            ]
            pygame.draw.polygon(surf, (70, 130, 220), sleeve)
            pygame.draw.polygon(surf, (220, 230, 245), sleeve, width=1)

        elif name == "play":
            # Green play triangle
            col = (80, 230, 120)
            pts = [(s * 0.25, s * 0.18), (s * 0.82, cy), (s * 0.25, s * 0.82)]
            pygame.draw.polygon(surf, col, pts)

        elif name == "pause":
            # Dual pause bars
            col = (235, 240, 250)
            w = max(2, int(s * 0.18))
            pygame.draw.rect(surf, col, (cx - s * 0.26, s * 0.2, w, s * 0.6), border_radius=1)
            pygame.draw.rect(surf, col, (cx + s * 0.08, s * 0.2, w, s * 0.6), border_radius=1)

        elif name == "fast_forward":
            # Dual forward triangles
            col = (255, 215, 60)
            pts1 = [(s * 0.15, s * 0.22), (cx, cy), (s * 0.15, s * 0.78)]
            pts2 = [(cx, s * 0.22), (s * 0.85, cy), (cx, s * 0.78)]
            pygame.draw.polygon(surf, col, pts1)
            pygame.draw.polygon(surf, col, pts2)

        elif name == "trophy":
            # Golden victory cup
            cup_col = (255, 215, 45)
            pts = [(s * 0.25, s * 0.18), (s * 0.75, s * 0.18), (s * 0.65, s * 0.58), (s * 0.35, s * 0.58)]
            pygame.draw.polygon(surf, cup_col, pts)
            # Stem and base
            pygame.draw.rect(surf, cup_col, (cx - s * 0.08, s * 0.58, s * 0.16, s * 0.18))
            pygame.draw.rect(surf, cup_col, (s * 0.25, s * 0.76, s * 0.5, s * 0.12), border_radius=2)

        elif name == "skull":
            # Death skull
            col = (235, 235, 240)
            pygame.draw.circle(surf, col, (cx, cy - s * 0.08), s * 0.32)
            pygame.draw.rect(surf, col, (cx - s * 0.2, cy + s * 0.08, s * 0.4, s * 0.22), border_radius=2)
            # Eye sockets
            pygame.draw.circle(surf, (25, 25, 30), (cx - s * 0.12, cy - s * 0.08), max(1.5, s * 0.09))
            pygame.draw.circle(surf, (25, 25, 30), (cx + s * 0.12, cy - s * 0.08), max(1.5, s * 0.09))

        elif name == "exit" or name == "quit":
            # Doorway with red exit arrow
            col = (245, 85, 95)
            # Door frame
            pygame.draw.lines(surf, (200, 210, 225), False, [(cx, s * 0.18), (s * 0.20, s * 0.18), (s * 0.20, s * 0.82), (cx, s * 0.82)], max(2, int(s * 0.1)))
            # Arrow pointing right
            pygame.draw.line(surf, col, (s * 0.32, cy), (s * 0.76, cy), max(2, int(s * 0.1)))
            pygame.draw.polygon(surf, col, [(s * 0.82, cy), (s * 0.58, cy - s * 0.18), (s * 0.58, cy + s * 0.18)])

        elif name == "monster" or name == "creep":
            # Horned minion icon
            col = (255, 105, 115)
            pygame.draw.circle(surf, col, (cx, cy), s * 0.32)
            # Horns
            pygame.draw.polygon(surf, (220, 75, 85), [(cx - s * 0.25, cy - s * 0.1), (cx - s * 0.35, cy - s * 0.38), (cx - s * 0.10, cy - s * 0.25)])
            pygame.draw.polygon(surf, (220, 75, 85), [(cx + s * 0.25, cy - s * 0.1), (cx + s * 0.35, cy - s * 0.38), (cx + s * 0.10, cy - s * 0.25)])
            # Glowing eyes
            pygame.draw.circle(surf, (255, 235, 80), (cx - s * 0.10, cy - s * 0.05), max(1.5, s * 0.08))
            pygame.draw.circle(surf, (255, 235, 80), (cx + s * 0.10, cy - s * 0.05), max(1.5, s * 0.08))

        # --- 6 ELEMENT BADGES ---
        elif name == "elem_light":
            # 8-point Radiant Star / Sun
            col = (255, 245, 120)
            r_out = s * 0.44
            r_in = s * 0.18
            pts = []
            for i in range(16):
                angle = i * (math.pi / 8.0)
                r = r_out if i % 2 == 0 else r_in
                pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.circle(surf, (255, 255, 230), (cx, cy), s * 0.18)

        elif name == "elem_darkness":
            # Shadow Crescent Void
            col = (185, 95, 255)
            pygame.draw.circle(surf, col, (cx, cy), s * 0.40)
            # Cutout inner circle to form crescent
            pygame.draw.circle(surf, (0, 0, 0, 0), (cx + s * 0.14, cy - s * 0.12), s * 0.32)

        elif name == "elem_water":
            # Teardrop / Water droplet
            col = (60, 185, 255)
            # Bottom circle + apex triangle
            bot_r = s * 0.32
            pygame.draw.circle(surf, col, (cx, cy + s * 0.12), bot_r)
            pts = [(cx - bot_r * 0.95, cy + s * 0.06), (cx + bot_r * 0.95, cy + s * 0.06), (cx, s * 0.12)]
            pygame.draw.polygon(surf, col, pts)
            # Specular curve
            pygame.draw.arc(surf, (200, 240, 255), (cx - bot_r * 0.6, cy - s * 0.08, bot_r * 1.2, bot_r * 1.2), 0.5 * math.pi, math.pi, max(1, int(s * 0.08)))

        elif name == "elem_fire":
            # Dancing Flame
            col = (255, 95, 30)
            pts = [
                (cx, s * 0.1),
                (cx + s * 0.35, s * 0.45),
                (cx + s * 0.22, s * 0.55),
                (cx + s * 0.38, s * 0.88),
                (cx - s * 0.38, s * 0.88),
                (cx - s * 0.22, s * 0.55),
                (cx - s * 0.35, s * 0.45),
            ]
            pygame.draw.polygon(surf, col, pts)
            # Inner yellow heart flame
            inner_pts = [
                (cx, s * 0.38),
                (cx + s * 0.18, s * 0.65),
                (cx + s * 0.16, s * 0.84),
                (cx - s * 0.16, s * 0.84),
                (cx - s * 0.18, s * 0.65),
            ]
            pygame.draw.polygon(surf, (255, 225, 80), inner_pts)

        elif name == "elem_nature":
            # Emerald Leaf
            col = (65, 225, 95)
            # Diagonal curved leaf
            pts = [
                (cx - s * 0.32, cy + s * 0.32),
                (cx - s * 0.15, cy - s * 0.1),
                (cx + s * 0.35, cy - s * 0.35),
                (cx + s * 0.1, cy + s * 0.15),
            ]
            pygame.draw.polygon(surf, col, pts)
            # Center vein
            pygame.draw.line(surf, (20, 140, 45), (cx - s * 0.3, cy + s * 0.3), (cx + s * 0.32, cy - s * 0.32), max(1, int(s * 0.07)))

        elif name == "elem_earth":
            # Mountain Peak / Terracotta Rock
            col = (210, 150, 80)
            pts = [(cx, s * 0.14), (cx + s * 0.42, s * 0.84), (cx - s * 0.42, s * 0.84)]
            pygame.draw.polygon(surf, col, pts)
            # Shaded facet
            facet_pts = [(cx, s * 0.14), (cx + s * 0.42, s * 0.84), (cx, s * 0.84)]
            pygame.draw.polygon(surf, (155, 100, 45), facet_pts)
            # Snow/Stone cap
            cap_pts = [(cx, s * 0.14), (cx + s * 0.14, s * 0.38), (cx - s * 0.14, s * 0.38)]
            pygame.draw.polygon(surf, (240, 230, 220), cap_pts)

        elif name == "elem_none":
            # Physical Steel Shield / Circle
            col = (180, 190, 205)
            pygame.draw.circle(surf, col, (cx, cy), s * 0.40)
            pygame.draw.circle(surf, (120, 130, 145), (cx, cy), s * 0.40, width=2)
            pygame.draw.circle(surf, (220, 230, 245), (cx - s * 0.1, cy - s * 0.1), max(1.5, s * 0.12))

        else:
            # Fallback circle dot
            pygame.draw.circle(surf, (200, 200, 200), (cx, cy), s * 0.35)

    @classmethod
    def get_element_icon(cls, elem: Element, size: int = 20) -> pygame.Surface:
        """Helper to get pre-rendered elemental icon."""
        name = f"elem_{elem.value.lower()}"
        return cls.get_icon(name, size)
