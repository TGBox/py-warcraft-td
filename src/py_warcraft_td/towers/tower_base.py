"""Tower entity class managing targeting, cooldowns, firing, and statistics."""

import math
from typing import Callable, List, Optional, Tuple
import pygame
from py_warcraft_td.audio import AudioManager
from py_warcraft_td.config import CELL_SIZE, LayoutConfig, TOWER_SELL_RATIO
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import Element, get_element_color
from py_warcraft_td.particles import VisualEffectsManager
from py_warcraft_td.pathfinding import GridCoord, grid_to_pixel
from py_warcraft_td.projectiles import ChainLightningEffect, InstantBeam, Projectile
from py_warcraft_td.sprites import SpriteRenderer
from py_warcraft_td.towers.tower_catalog import TowerDefinition, get_tower_def


class Tower:
    """An instantiated tower on the game grid with procedural sprite rendering."""

    def __init__(
        self,
        col: int,
        row: int,
        tower_def: TowerDefinition,
        layout: Optional[LayoutConfig] = None,
    ):
        self.col = col
        self.row = row
        self.layout = layout

        if layout:
            pixel_pos = layout.grid_to_pixel((col, row))
            self.cell_size = layout.cell_size
        else:
            pixel_pos = grid_to_pixel((col, row))
            self.cell_size = CELL_SIZE

        self.x = pixel_pos[0]
        self.y = pixel_pos[1]

        self.def_id = tower_def.id
        self.definition = tower_def
        self.cooldown_timer = 0.0

        # Investment & Stats
        self.total_invested = tower_def.cost
        self.kills = 0
        self.damage_dealt = 0.0

        # Targeting strategy: "first" (furthest along path), "strongest", "closest"
        self.targeting_mode = "first"

    @property
    def grid_coord(self) -> GridCoord:
        return (self.col, self.row)

    @property
    def sell_value(self) -> int:
        return max(5, int(self.total_invested * TOWER_SELL_RATIO))

    def can_upgrade(self) -> bool:
        return self.definition.upgrade_to is not None

    def upgrade(self, new_def: TowerDefinition) -> None:
        """Upgrade this tower to a higher tier."""
        self.definition = new_def
        self.def_id = new_def.id
        self.total_invested += new_def.cost
        self.cooldown_timer = 0.0

    def find_target(self, creeps: List[Creep]) -> Optional[Creep]:
        """Find the best target in attack range based on targeting mode and air/ground restrictions."""
        candidates: List[Tuple[float, Creep]] = []
        range_sq = self.definition.range_px ** 2

        for c in creeps:
            if c.is_dead or c.has_leaked:
                continue

            if c.is_flying and self.definition.targets == "ground":
                continue
            if not c.is_flying and self.definition.targets == "air":
                continue

            dist_sq = (c.x - self.x) ** 2 + (c.y - self.y) ** 2
            if dist_sq <= range_sq:
                candidates.append((dist_sq, c))

        if not candidates:
            return None

        if self.targeting_mode == "first":
            candidates.sort(key=lambda item: item[1].total_distance_traveled, reverse=True)
            return candidates[0][1]
        elif self.targeting_mode == "strongest":
            candidates.sort(key=lambda item: item[1].hp, reverse=True)
            return candidates[0][1]
        else: # "closest"
            candidates.sort(key=lambda item: item[0])
            return candidates[0][1]

    def update(
        self,
        dt: float,
        creeps: List[Creep],
        projectiles: List[Projectile],
        beams: List[InstantBeam],
        chain_lightnings: List[ChainLightningEffect],
        vfx: VisualEffectsManager,
        audio: AudioManager,
        on_kill_callback: Callable[[Creep, int], None],
    ) -> None:
        """Update cooldown and perform attack if ready."""
        if self.cooldown_timer > 0.0:
            self.cooldown_timer -= dt

        if self.cooldown_timer <= 0.0:
            target = self.find_target(creeps)
            if target:
                self._attack(
                    target, creeps, projectiles, beams, chain_lightnings, vfx, audio, on_kill_callback
                )
                self.cooldown_timer = self.definition.attack_cooldown

    def _attack(
        self,
        target: Creep,
        all_creeps: List[Creep],
        projectiles: List[Projectile],
        beams: List[InstantBeam],
        chain_lightnings: List[ChainLightningEffect],
        vfx: VisualEffectsManager,
        audio: AudioManager,
        on_kill_callback: Callable[[Creep, int], None],
    ) -> None:
        """Execute tower attack based on its attack type."""
        atk_type = self.definition.attack_type
        elem = self.definition.elements[0] if self.definition.elements else Element.NONE
        color, _ = get_element_color(elem)

        def wrapped_kill(creep: Creep, bonus_gold: int) -> None:
            self.kills += 1
            on_kill_callback(creep, bonus_gold)

        audio.play(self.definition.sound_effect, volume=0.45)

        if atk_type == "instant_beam":
            beams.append(InstantBeam(self.x, self.y, target.x, target.y, color))
            dmg, mult = target.take_damage(self.definition.damage, elem)
            self.damage_dealt += dmg

            txt_color = (255, 230, 80) if mult == 2.0 else ((160, 160, 170) if mult == 0.5 else color)
            text_str = f"{int(dmg)}!" if mult == 2.0 else f"{int(dmg)}"
            vfx.add_floating_text(text_str, target.x, target.y, txt_color, size=15 if mult == 2.0 else 13)
            vfx.add_sparks(target.x, target.y, color, count=6, speed=70.0)

            ability = self.definition.ability
            if ability.burn_dps > 0:
                target.apply_burn(ability.burn_dps, ability.burn_duration)
            if ability.slow_factor > 0:
                target.apply_slow(ability.slow_factor, ability.slow_duration)

            if target.is_dead:
                wrapped_kill(target, ability.gold_bounty_bonus)

        elif atk_type == "chain":
            ability = self.definition.ability
            max_bounces = ability.chain_bounces or 4
            chain_targets: List[Creep] = [target]
            chain_points: List[Tuple[float, float]] = [(self.x, self.y), (target.x, target.y)]

            curr_target = target
            dmg, mult = curr_target.take_damage(self.definition.damage, elem)
            self.damage_dealt += dmg
            if curr_target.is_dead:
                wrapped_kill(curr_target, ability.gold_bounty_bonus)

            current_dmg = self.definition.damage * ability.chain_decay
            bounce_range = 140.0

            for _ in range(max_bounces - 1):
                next_target = None
                best_dist = bounce_range
                for c in all_creeps:
                    if c in chain_targets or c.is_dead or c.has_leaked:
                        continue
                    d = math.hypot(c.x - curr_target.x, c.y - curr_target.y)
                    if d < best_dist:
                        best_dist = d
                        next_target = c

                if next_target:
                    chain_targets.append(next_target)
                    chain_points.append((next_target.x, next_target.y))
                    d_dmg, _ = next_target.take_damage(current_dmg, elem)
                    self.damage_dealt += d_dmg
                    if next_target.is_dead:
                        wrapped_kill(next_target, ability.gold_bounty_bonus)
                    curr_target = next_target
                    current_dmg *= ability.chain_decay
                else:
                    break

            chain_lightnings.append(ChainLightningEffect(chain_points, color=color))

        else:
            proj = Projectile(self.x, self.y, target, self.definition, on_kill_callback=wrapped_kill)
            projectiles.append(proj)

    def draw(self, surface: pygame.Surface, is_selected: bool = False) -> None:
        """Render the tower using its procedural sprite."""
        s = self.cell_size
        sprite = SpriteRenderer.get_tower_sprite(self.definition, s, is_selected=is_selected)
        surface.blit(sprite, (int(self.x - s / 2.0), int(self.y - s / 2.0)))
