"""Creeps, elemental armor, traits, status effects, and movement logic."""

import math
from typing import Dict, List, Optional, Tuple
from py_warcraft_td.config import CELL_SIZE, GOAL_CELL, SPAWN_CELL
from py_warcraft_td.elements import Element, get_element_color, get_element_multiplier
from py_warcraft_td.pathfinding import GridCoord, PixelCoord, grid_to_pixel


class Creep:
    """Invading enemy unit in Element TD."""

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

        # Visual dimensions
        self.radius = 12.0 if not is_flying else 14.0
        if modifier == "boss":
            self.radius = 18.0
        elif modifier == "swarm":
            self.radius = 8.0

        # Position and Navigation
        self.path: List[GridCoord] = path or []
        self.path_index: int = 0
        spawn_px = grid_to_pixel(SPAWN_CELL)
        self.x: float = spawn_px[0]
        self.y: float = spawn_px[1]

        # Flying target
        goal_px = grid_to_pixel(GOAL_CELL)
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

    @property
    def current_grid_cell(self) -> GridCoord:
        """Approximate current cell coordinates."""
        col = int(round((self.x - 24.0 - CELL_SIZE / 2.0) / CELL_SIZE))
        row = int(round((self.y - 80.0 - CELL_SIZE / 2.0) / CELL_SIZE))
        return (max(0, col), max(0, row))

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
        # Move back one or two waypoints
        self.path_index = max(0, self.path_index - 1)
        target_cell = self.path[self.path_index]
        target_px = grid_to_pixel(target_cell)
        self.x = (self.x + target_px[0]) / 2.0
        self.y = (self.y + target_px[1]) / 2.0

    def take_damage(self, raw_damage: float, attack_elem: Element) -> Tuple[float, float]:
        """Apply damage based on element multiplier and active status effects.

        Returns:
            (actual_damage_dealt, multiplier)
        """
        mult = get_element_multiplier(attack_elem, self.armor_element)

        damage = raw_damage * mult

        # Apply Armor Sunder modifier
        if self.sunder_timer > 0:
            damage *= (1.0 + self.sunder_factor)

        # Apply Shielded trait
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

        # 1. Stun check
        if self.stun_timer > 0.0:
            self.stun_timer -= dt
            # Still take DoT while stunned
        else:
            # 2. Movement
            current_speed = self.base_speed
            if self.slow_timer > 0.0:
                current_speed *= self.slow_factor
                self.slow_timer -= dt
                if self.slow_timer <= 0.0:
                    self.slow_factor = 1.0

            if self.is_flying:
                # Direct flight from current pos towards goal
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
                # Ground movement along waypoints
                if self.path and self.path_index < len(self.path):
                    target_cell = self.path[self.path_index]
                    target_px = grid_to_pixel(target_cell)
                    dx = target_px[0] - self.x
                    dy = target_px[1] - self.y
                    dist = math.hypot(dx, dy)
                    step = current_speed * dt

                    if dist <= step or dist < 3.0:
                        self.x = target_px[0]
                        self.y = target_px[1]
                        self.path_index += 1
                        if self.path_index >= len(self.path):
                            # Reached final waypoint (goal)
                            self.has_leaked = True
                    else:
                        self.x += (dx / dist) * step
                        self.y += (dy / dist) * step
                        self.total_distance_traveled += step
                else:
                    # No remaining waypoints
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
            regen_amount = self.max_hp * 0.03 * dt  # 3% per second
            self.hp = min(self.max_hp, self.hp + regen_amount)

    def respawn_at_start(self, initial_path: List[GridCoord]) -> None:
        """Reset leaked creep to start with its current remaining HP."""
        spawn_px = grid_to_pixel(SPAWN_CELL)
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
