"""Creeps, elemental armor, traits, status effects, and movement logic."""

import math
from typing import Dict, List, Optional, Tuple
import pygame
from py_warcraft_td.config import CELL_SIZE, GOAL_CELL, LayoutConfig, SPAWN_CELL
from py_warcraft_td.elements import Element, get_element_color, get_element_multiplier
from py_warcraft_td.pathfinding import GridCoord, PixelCoord, grid_to_pixel
from py_warcraft_td.sprites import SpriteRenderer


class Creep:
    """Invading enemy unit in Element TD with procedural sprite rendering."""

    def __init__(
        self,
        creep_id: int,
        name: str,
        wave_num: int,
        max_hp: float,
        speed: float,
        armor_element: Element,
        gold_reward: int,
        is_flying: bool = False,
        modifier: str = "normal",  # "normal", "fast", "tank", "swarm", "boss", "shielded", "regen"
        path: Optional[List[GridCoord]] = None,
        layout: Optional[LayoutConfig] = None,
    ):
        self.id = creep_id
        self.name = name
        self.wave_num = wave_num
        self.max_hp = max_hp
        self.hp = max_hp
        self.base_speed = speed
        self.armor_element = armor_element
        self.gold_reward = gold_reward
        self.is_flying = is_flying
        self.modifier = modifier
        self.layout = layout

        # Visual dimensions scaled to layout
        c_size = layout.cell_size if layout else CELL_SIZE
        scale = c_size / 36.0

        self.radius = 13.0 * scale
        if modifier == "boss":
            self.radius = 22.0 * scale
        elif modifier == "swarm":
            self.radius = 9.0 * scale
        elif is_flying:
            self.radius = 16.0 * scale
        elif modifier == "tank":
            self.radius = 17.0 * scale

        # Position and Navigation
        self.path: List[GridCoord] = path or []
        self.path_index: int = 0

        sp_cell = layout.spawn_cell if layout else SPAWN_CELL
        gl_cell = layout.goal_cell if layout else GOAL_CELL

        spawn_px = layout.grid_to_pixel(sp_cell) if layout else grid_to_pixel(sp_cell)
        self.x: float = spawn_px[0]
        self.y: float = spawn_px[1]

        # Flying target
        goal_px = layout.grid_to_pixel(gl_cell) if layout else grid_to_pixel(gl_cell)
        self.goal_x: float = goal_px[0]
        self.goal_y: float = goal_px[1]

        # Status Effects
        self.slow_timer: float = 0.0
        self.slow_factor: float = 1.0  # 1.0 = normal, 0.5 = 50% slow

        self.burn_timer: float = 0.0
        self.burn_dps: float = 0.0

        self.poison_timer: float = 0.0
        self.poison_dps: float = 0.0

        self.sunder_timer: float = 0.0
        self.sunder_factor: float = 0.0  # e.g. 0.35 = +35% damage taken

        self.stun_timer: float = 0.0

        # Creep State
        self.is_dead: bool = False
        self.has_leaked: bool = False
        self.total_distance_traveled: float = 0.0
        self.anim_tick: int = 0

    @property
    def current_grid_cell(self) -> GridCoord:
        """Approximate current cell coordinates."""
        if self.layout:
            grid_pos = self.layout.pixel_to_grid((self.x, self.y))
            if grid_pos:
                return grid_pos
            col = int(round((self.x - self.layout.grid_offset_x - self.layout.cell_size / 2.0) / self.layout.cell_size))
            row = int(round((self.y - self.layout.grid_offset_y - self.layout.cell_size / 2.0) / self.layout.cell_size))
            return (max(0, col), max(0, row))

        col = int(round((self.x - 24.0 - CELL_SIZE / 2.0) / CELL_SIZE))
        row = int(round((self.y - 80.0 - CELL_SIZE / 2.0) / CELL_SIZE))
        return (max(0, col), max(0, row))

    def _coord_to_pixel(self, coord: GridCoord) -> PixelCoord:
        if self.layout:
            return self.layout.grid_to_pixel(coord)
        return grid_to_pixel(coord)

    def update_path(self, new_path: List[GridCoord]) -> None:
        """Update waypoint path for ground creep after maze modifications."""
        if self.is_flying:
            return
        if not new_path:
            return
        self.path = new_path
        self.path_index = 0

    def apply_slow(self, factor: float, duration: float) -> None:
        """Apply movement slow (factor e.g. 0.35 = 35% speed reduction)."""
        speed_mult = 1.0 - factor
        if speed_mult < self.slow_factor or self.slow_timer <= 0:
            self.slow_factor = max(0.20, speed_mult)  # Cap max slow at 80%
            self.slow_timer = max(self.slow_timer, duration)

    def apply_burn(self, dps: float, duration: float) -> None:
        """Apply fire burning damage over time."""
        self.burn_dps = max(self.burn_dps, dps)
        self.burn_timer = max(self.burn_timer, duration)

    def apply_poison(self, dps: float, duration: float) -> None:
        """Apply poison damage over time."""
        self.poison_dps = max(self.poison_dps, dps)
        self.poison_timer = max(self.poison_timer, duration)

    def apply_sunder(self, extra_damage_factor: float, duration: float) -> None:
        """Apply armor sunder making target take extra damage."""
        self.sunder_factor = max(self.sunder_factor, extra_damage_factor)
        self.sunder_timer = max(self.sunder_timer, duration)

    def apply_stun(self, duration: float) -> None:
        """Stun the creep, freezing its movement."""
        self.stun_timer = max(self.stun_timer, duration)

    def knockback(self, distance_px: float) -> None:
        """Push ground creep backwards along its path."""
        if self.is_flying or self.path_index <= 0:
            return
        self.path_index = max(0, self.path_index - 1)
        target_cell = self.path[self.path_index]
        target_px = self._coord_to_pixel(target_cell)
        self.x = (self.x + target_px[0]) / 2.0
        self.y = (self.y + target_px[1]) / 2.0

    def take_damage(self, raw_damage: float, attack_elem: Element) -> Tuple[float, float]:
        """Apply damage based on element multiplier and active status effects."""
        mult = get_element_multiplier(attack_elem, self.armor_element)
        damage = raw_damage * mult

        if self.sunder_timer > 0:
            damage *= (1.0 + self.sunder_factor)

        if self.modifier == "shielded":
            damage *= 0.75

        self.hp -= damage
        if self.hp <= 0.0:
            self.hp = 0.0
            self.is_dead = True

        return (damage, mult)

    def update(self, dt: float) -> None:
        """Update movement, timers, regeneration, and DoT effects."""
        if self.is_dead or self.has_leaked:
            return

        self.anim_tick += 1

        # 1. Stun check
        if self.stun_timer > 0.0:
            self.stun_timer -= dt
        else:
            # 2. Movement
            current_speed = self.base_speed
            if self.slow_timer > 0.0:
                current_speed *= self.slow_factor
                self.slow_timer -= dt
                if self.slow_timer <= 0.0:
                    self.slow_factor = 1.0

            if self.is_flying:
                dx = self.goal_x - self.x
                dy = self.goal_y - self.y
                dist = math.hypot(dx, dy)
                step = current_speed * dt
                if dist <= step or dist < 4.0:
                    self.x = self.goal_x
                    self.y = self.goal_y
                    self.has_leaked = True
                else:
                    self.x += (dx / dist) * step
                    self.y += (dy / dist) * step
                    self.total_distance_traveled += step
            else:
                if self.path and self.path_index < len(self.path):
                    target_cell = self.path[self.path_index]
                    target_px = self._coord_to_pixel(target_cell)
                    dx = target_px[0] - self.x
                    dy = target_px[1] - self.y
                    dist = math.hypot(dx, dy)
                    step = current_speed * dt

                    if dist <= step or dist < 4.0:
                        self.x = target_px[0]
                        self.y = target_px[1]
                        self.path_index += 1
                        if self.path_index >= len(self.path):
                            self.has_leaked = True
                    else:
                        self.x += (dx / dist) * step
                        self.y += (dy / dist) * step
                        self.total_distance_traveled += step
                else:
                    self.has_leaked = True

        # 3. Status effect timers & DoT
        if self.burn_timer > 0.0:
            burn_damage = self.burn_dps * dt
            self.hp -= burn_damage
            self.burn_timer -= dt
            if self.hp <= 0.0:
                self.hp = 0.0
                self.is_dead = True

        if self.poison_timer > 0.0:
            poison_damage = self.poison_dps * dt
            self.hp -= poison_damage
            self.poison_timer -= dt
            if self.hp <= 0.0:
                self.hp = 0.0
                self.is_dead = True

        if self.sunder_timer > 0.0:
            self.sunder_timer -= dt
            if self.sunder_timer <= 0.0:
                self.sunder_factor = 0.0

        # 4. Regen trait
        if self.modifier == "regen" and not self.is_dead:
            regen_amount = self.max_hp * 0.03 * dt
            self.hp = min(self.max_hp, self.hp + regen_amount)

    def respawn_at_start(self, initial_path: List[GridCoord]) -> None:
        """Reset leaked creep to start with its current remaining HP."""
        sp_cell = self.layout.spawn_cell if self.layout else SPAWN_CELL
        spawn_px = self._coord_to_pixel(sp_cell)
        self.x = spawn_px[0]
        self.y = spawn_px[1]
        self.path = initial_path
        self.path_index = 0
        self.has_leaked = False
        self.slow_timer = 0.0
        self.slow_factor = 1.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0
        self.sunder_timer = 0.0
        self.stun_timer = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        """Render the creep using its procedural sprite and dynamic healthbar."""
        if self.is_dead or self.has_leaked:
            return

        cx, cy = int(self.x), int(self.y)
        sprite_size = int(self.radius * 2.4)
        # Even size
        if sprite_size % 2 != 0:
            sprite_size += 1

        sprite = SpriteRenderer.get_creep_sprite(
            self.armor_element, self.modifier, self.is_flying, sprite_size, self.anim_tick // 10
        )
        surface.blit(sprite, (cx - sprite_size // 2, cy - sprite_size // 2))

        # Status effect aura
        if self.slow_timer > 0:
            pygame.draw.circle(surface, (100, 200, 255), (cx, cy), int(self.radius + 3), width=1)
        if self.burn_timer > 0:
            pygame.draw.circle(surface, (255, 120, 30), (cx, cy), int(self.radius + 4), width=1)
        if self.poison_timer > 0:
            pygame.draw.circle(surface, (80, 230, 90), (cx, cy), int(self.radius + 3), width=1)

        # Health bar
        hp_w = max(20, int(self.radius * 2.2))
        hp_h = 4
        hp_x = cx - hp_w // 2
        hp_y = cy - int(self.radius) - 9

        hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        pygame.draw.rect(surface, (30, 20, 20), (hp_x, hp_y, hp_w, hp_h), border_radius=1)
        bar_color = (60, 220, 90) if hp_ratio > 0.5 else ((240, 200, 50) if hp_ratio > 0.25 else (240, 50, 50))
        pygame.draw.rect(surface, bar_color, (hp_x, hp_y, int(hp_w * hp_ratio), hp_h), border_radius=1)
        pygame.draw.rect(surface, (10, 10, 15), (hp_x, hp_y, hp_w, hp_h), width=1, border_radius=1)
