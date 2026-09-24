"""Projectiles, beams, and chain lightning attack visualizers and hit resolvers."""

import math
import random
from typing import Callable, List, Optional, Tuple
import pygame
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import Element, get_element_color
from py_warcraft_td.particles import VisualEffectsManager
from py_warcraft_td.towers.tower_catalog import TowerAbility, TowerDefinition


class Projectile:
    """A physical or magical projectile in transit towards a creep."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target: Creep,
        tower_def: TowerDefinition,
        on_kill_callback: Optional[Callable[[Creep, int], None]] = None,
    ):
        self.x = start_x
        self.y = start_y
        self.target = target
        self.tower_def = tower_def
        self.speed = tower_def.projectile_speed or 450.0
        self.on_kill_callback = on_kill_callback

        self.element = tower_def.elements[0] if tower_def.elements else Element.NONE
        self.color, self.core_color = get_element_color(self.element)
        self.is_done = False

    def update(
        self,
        dt: float,
        all_creeps: List[Creep],
        vfx: VisualEffectsManager,
    ) -> None:
        """Update projectile position towards target."""
        if self.is_done:
            return

        # Target might have died or leaked while projectile in air
        tx = self.target.x if not (self.target.is_dead or self.target.has_leaked) else self.x
        ty = self.target.y if not (self.target.is_dead or self.target.has_leaked) else self.y

        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt

        if dist <= step or dist < 8.0:
            # Hit target
            self.is_done = True
            self._on_impact(all_creeps, vfx)
        else:
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step

    def _on_impact(self, all_creeps: List[Creep], vfx: VisualEffectsManager) -> None:
        """Apply damage and status effects on target and optional splash radius."""
        ability = self.tower_def.ability
        splash_r = ability.splash_radius

        targets_to_hit: List[Creep] = []

        if splash_r > 0.0:
            # Hit all valid creeps in splash radius
            for c in all_creeps:
                if c.is_dead or c.has_leaked:
                    continue
                # Ground-only check for splash if tower only targets ground
                if c.is_flying and self.tower_def.targets == "ground":
                    continue
                d = math.hypot(c.x - self.x, c.y - self.y)
                if d <= splash_r:
                    targets_to_hit.append(c)
            # Spawn splash VFX
            vfx.add_explosion(self.x, self.y, self.color, splash_r)
        else:
            if not (self.target.is_dead or self.target.has_leaked):
                targets_to_hit.append(self.target)
            vfx.add_sparks(self.x, self.y, self.color, count=10, speed=90.0)

        for c in targets_to_hit:
            dmg, mult = c.take_damage(self.tower_def.damage, self.element)

            # Floating text feedback
            txt_color = (255, 230, 80) if mult == 2.0 else ((160, 160, 170) if mult == 0.5 else self.color)
            text_str = f"{int(dmg)}!" if mult == 2.0 else f"{int(dmg)}"
            vfx.add_floating_text(text_str, c.x, c.y, txt_color, size=15 if mult == 2.0 else 13)

            # Apply Abilities
            if ability.slow_factor > 0:
                c.apply_slow(ability.slow_factor, ability.slow_duration)
            if ability.burn_dps > 0:
                c.apply_burn(ability.burn_dps, ability.burn_duration)
            if ability.poison_dps > 0:
                c.apply_poison(ability.poison_dps, ability.poison_duration)
            if ability.armor_sunder > 0:
                c.apply_sunder(ability.armor_sunder, ability.sunder_duration)
            if ability.stun_duration > 0:
                c.apply_stun(ability.stun_duration)
            if ability.knockback_dist > 0:
                c.knockback(ability.knockback_dist)

            if c.is_dead and self.on_kill_callback:
                bonus_gold = ability.gold_bounty_bonus
                self.on_kill_callback(c, bonus_gold)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw projectile with glow."""
        if self.is_done:
            return
        px, py = int(self.x), int(self.y)
        # Outer glow
        pygame.draw.circle(surface, self.color, (px, py), 5)
        # Core bright dot
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)


class InstantBeam:
    """Visual beam from tower to target for instant attacks."""

    def __init__(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        color: Tuple[int, int, int],
        duration: float = 0.12,
        width: int = 3,
    ):
        self.start = (start_x, start_y)
        self.end = (end_x, end_y)
        self.color = color
        self.duration = duration
        self.age = 0.0
        self.width = width

    @property
    def is_done(self) -> bool:
        return self.age >= self.duration

    def update(self, dt: float) -> None:
        self.age += dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_done:
            return
        # Outer beam
        pygame.draw.line(surface, self.color, self.start, self.end, self.width + 2)
        # Inner bright core
        pygame.draw.line(surface, (255, 255, 255), self.start, self.end, max(1, self.width - 1))


class ChainLightningEffect:
    """Visual jagged chain lightning bouncing between targets."""

    def __init__(
        self,
        points: List[Tuple[float, float]],
        color: Tuple[int, int, int] = (255, 240, 100),
        duration: float = 0.18,
    ):
        self.points = points
        self.color = color
        self.duration = duration
        self.age = 0.0
        # Generate jagged segments
        self.segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        self._build_jagged_segments()

    def _build_jagged_segments(self) -> None:
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            # Midpoint with random displacement
            mx = (p1[0] + p2[0]) / 2.0 + random.uniform(-10.0, 10.0)
            my = (p1[1] + p2[1]) / 2.0 + random.uniform(-10.0, 10.0)
            self.segments.append((p1, (mx, my)))
            self.segments.append(((mx, my), p2))

    @property
    def is_done(self) -> bool:
        return self.age >= self.duration

    def update(self, dt: float) -> None:
        self.age += dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_done:
            return
        for s1, s2 in self.segments:
            pygame.draw.line(surface, self.color, s1, s2, 3)
            pygame.draw.line(surface, (255, 255, 255), s1, s2, 1)
