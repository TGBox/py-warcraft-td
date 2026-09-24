"""Main Game Engine and state machine for py-warcraft-td (Element TD).

Supports 1920x1080, 2560x1080 (21:9 Ultrawide), Fullscreen toggling with F11,
and procedural sprite & vector icon rendering.
"""

import math
import sys
from typing import Dict, List, Optional, Set, Tuple
import pygame
from py_warcraft_td.audio import AudioManager
from py_warcraft_td.config import (
    BG_DARK,
    BG_PANEL,
    BG_PANEL_ALT,
    BG_PANEL_BORDER,
    DEFAULT_HEIGHT,
    DEFAULT_INTEREST_RATE,
    DEFAULT_WIDTH,
    DIFFICULTY_SETTINGS,
    FPS,
    INTEREST_INTERVAL,
    LayoutConfig,
    STARTING_LIVES,
    TEXT_COLOR,
    TEXT_GOLD,
    TEXT_GREEN,
    TEXT_MUTED,
    TEXT_RED,
    create_layout_config,
)
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import Element, ELEMENT_NAMES_DE, get_element_color
from py_warcraft_td.guardians import GuardianManager
from py_warcraft_td.icons import IconRenderer
from py_warcraft_td.particles import VisualEffectsManager
from py_warcraft_td.pathfinding import GridCoord, PathFinder, pixel_to_grid
from py_warcraft_td.projectiles import ChainLightningEffect, InstantBeam, Projectile
from py_warcraft_td.towers.tower_base import Tower
from py_warcraft_td.towers.tower_catalog import TowerDefinition, get_tower_def
from py_warcraft_td.ui import UIManager
from py_warcraft_td.waves import WaveConfig, generate_wave_schedule


class Game:
    """Core game controller managing simulation loop, resolution scaling, and entities."""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fullscreen: bool = False,
        headless: bool = False,
    ):
        pygame.init()
        pygame.display.set_caption("Element TD - Warcraft III Python Adaptation")

        self.headless = headless
        self.is_fullscreen = fullscreen
        self.current_width = width
        self.current_height = height

        # Create Layout Metrics
        self.layout = create_layout_config(width, height)

        if headless:
            self.screen = pygame.Surface((self.current_width, self.current_height))
        else:
            flags = pygame.FULLSCREEN if self.is_fullscreen else 0
            self.screen = pygame.display.set_mode((self.current_width, self.current_height), flags)

        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "START_MENU"  # START_MENU, PLAYING, VICTORY, GAME_OVER

        # Audio, VFX, and UI
        self.audio = AudioManager()
        self.vfx = VisualEffectsManager()
        self.ui = UIManager(self.screen)
        self.pathfinder = PathFinder(self.layout.grid_cols, self.layout.grid_rows)

        # Game Setup
        self.difficulty_name = "Normal"
        self.mode_total_waves = 60

        # Runtime State
        self.gold = 120
        self.lives = STARTING_LIVES
        self.game_speed = 1.0
        self.is_paused = False
        self.interest_rate = DEFAULT_INTEREST_RATE
        self.interest_timer = 0.0
        self.total_kills = 0
        self.total_gold_earned = 0

        # Entities
        self.towers: Dict[GridCoord, Tower] = {}
        self.creeps: List[Creep] = []
        self.projectiles: List[Projectile] = []
        self.beams: List[InstantBeam] = []
        self.chain_lightnings: List[ChainLightningEffect] = []

        # Guardian Altar
        self.guardians = GuardianManager()
        self.show_guardian_modal = False

        # Waves
        self.wave_schedule: List[WaveConfig] = []
        self.current_wave_index = 0
        self.creeps_spawned_in_wave = 0
        self.wave_spawn_timer = 0.0
        self.wave_intermission_timer = 3.5
        self.is_wave_in_progress = False

        # Selection and Eraser state
        self.selected_build_def: Optional[TowerDefinition] = None
        self.selected_placed_tower: Optional[Tower] = None
        self.is_eraser_mode: bool = False
        self.cached_ground_path: Optional[List[GridCoord]] = None

    def toggle_eraser_mode(self) -> None:
        """Toggle fast demolish/eraser mode for erasing towers."""
        self.is_eraser_mode = not self.is_eraser_mode
        if self.is_eraser_mode:
            self.selected_build_def = None
            self.selected_placed_tower = None
            self.audio.play("ui_click", volume=0.4)
            self.vfx.add_floating_text(
                "Löschen-Modus aktiv!", self.layout.screen_width // 2, 85, (255, 110, 130)
            )

    def toggle_fullscreen(self) -> None:
        """Toggle between Fullscreen and Windowed mode."""
        if self.headless:
            return

        self.is_fullscreen = not self.is_fullscreen
        flags = pygame.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pygame.display.set_mode((self.current_width, self.current_height), flags)
        self.ui.screen = self.screen

    def set_resolution(self, width: int, height: int) -> None:
        """Switch game resolution (e.g. 1920x1080 or 2560x1080) and adapt layout."""
        self.current_width = width
        self.current_height = height
        self.layout = create_layout_config(width, height)
        self.pathfinder = PathFinder(self.layout.grid_cols, self.layout.grid_rows)

        if not self.headless:
            flags = pygame.FULLSCREEN if self.is_fullscreen else 0
            self.screen = pygame.display.set_mode((width, height), flags)
            self.ui.screen = self.screen
        else:
            self.screen = pygame.Surface((width, height))
            self.ui.screen = self.screen

        # Recompute paths for active towers
        self.recalculate_paths()

    def start_game(self, mode_waves: int, difficulty: str) -> None:
        """Initialize and start a game session."""
        self.mode_total_waves = mode_waves
        self.difficulty_name = difficulty
        diff = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Normal"])

        self.gold = diff["starting_gold"]
        self.lives = diff["lives"]
        self.interest_rate = DEFAULT_INTEREST_RATE
        self.interest_timer = 0.0
        self.total_kills = 0
        self.total_gold_earned = self.gold

        self.towers.clear()
        self.creeps.clear()
        self.projectiles.clear()
        self.beams.clear()
        self.chain_lightnings.clear()

        self.guardians = GuardianManager()
        self.wave_schedule = generate_wave_schedule(
            total_waves=mode_waves, difficulty_mult=diff["hp_mult"]
        )
        self.current_wave_index = 0
        self.creeps_spawned_in_wave = 0
        self.wave_spawn_timer = 0.0
        self.wave_intermission_timer = 4.0
        self.is_wave_in_progress = False

        self.selected_build_def = None
        self.selected_placed_tower = None
        self.cached_ground_path = self.pathfinder.astar(self.layout.spawn_cell, self.layout.goal_cell, set())
        self.game_state = "PLAYING"

    def recalculate_paths(self) -> None:
        """Recompute A* paths for all ground creeps and spawn route."""
        occupied = set(self.towers.keys())
        self.cached_ground_path = self.pathfinder.astar(self.layout.spawn_cell, self.layout.goal_cell, occupied)

        for c in self.creeps:
            if not c.is_flying and not c.is_dead and not c.has_leaked:
                c_path = self.pathfinder.astar(c.current_grid_cell, self.layout.goal_cell, occupied)
                if c_path:
                    c.update_path(c_path)

    def on_creep_killed(self, creep: Creep, bonus_gold: int = 0) -> None:
        """Handle creep death: award gold, VFX, and audio."""
        award = creep.gold_reward + bonus_gold
        self.gold += award
        self.total_gold_earned += award
        self.total_kills += 1

        self.audio.play("creep_death", volume=0.35)
        self.vfx.add_floating_text(f"+{award}g", creep.x, creep.y - 12, TEXT_GOLD, size=15)
        self.vfx.add_sparks(creep.x, creep.y, (255, 220, 60), count=12)

        if creep.id < 0:
            tier, msg = self.guardians.on_guardian_killed(creep.armor_element)
            self.audio.play("victory", volume=0.6)
            self.vfx.add_floating_text(msg, creep.x, creep.y - 30, (255, 230, 80), size=18, lifetime=1.5)

    def handle_events(self) -> None:
        """Process Pygame user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused
                elif event.key == pygame.K_1:
                    self.game_speed = 1.0
                elif event.key == pygame.K_2:
                    self.game_speed = 2.0
                elif event.key == pygame.K_3:
                    self.game_speed = 4.0
                elif event.key == pygame.K_x or event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    self.toggle_eraser_mode()
                elif event.key == pygame.K_ESCAPE:
                    if self.show_guardian_modal:
                        self.show_guardian_modal = False
                    elif self.is_eraser_mode:
                        self.is_eraser_mode = False
                    elif self.selected_build_def:
                        self.selected_build_def = None
                    elif self.selected_placed_tower:
                        self.selected_placed_tower = None
                elif event.key == pygame.K_u:
                    if self.selected_placed_tower:
                        self._try_upgrade_tower(self.selected_placed_tower)
                elif event.key == pygame.K_s:
                    if self.selected_placed_tower:
                        self._try_sell_tower(self.selected_placed_tower)

            if event.type == pygame.MOUSEMOTION:
                # Drag eraser: if left mouse button is held down in eraser mode
                if event.buttons[0] == 1 and self.is_eraser_mode and self.game_state == "PLAYING" and not self.show_guardian_modal:
                    grid_coord = self.layout.pixel_to_grid(event.pos)
                    if grid_coord and grid_coord in self.towers:
                        self._try_sell_tower(self.towers[grid_coord])

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if self.ui.handle_click(mouse_pos):
                    self.audio.play("ui_click", volume=0.3)
                    continue

                if self.game_state == "PLAYING" and not self.show_guardian_modal:
                    grid_coord = self.layout.pixel_to_grid(mouse_pos)
                    if grid_coord:
                        if self.is_eraser_mode:
                            # Immediate demolition without confirmation
                            if grid_coord in self.towers:
                                self._try_sell_tower(self.towers[grid_coord])
                        elif self.selected_build_def:
                            self._try_place_tower(grid_coord, self.selected_build_def)
                        else:
                            if grid_coord in self.towers:
                                self.selected_placed_tower = self.towers[grid_coord]
                                self.audio.play("ui_click", volume=0.3)
                            else:
                                self.selected_placed_tower = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.selected_build_def = None
                self.selected_placed_tower = None
                self.is_eraser_mode = False

    def _try_place_tower(self, coord: GridCoord, tower_def: TowerDefinition) -> None:
        """Validate and place a tower on the grid."""
        if self.gold < tower_def.cost:
            self.vfx.add_floating_text("Nicht genug Gold!", pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], TEXT_RED)
            return

        col, row = coord
        occupied = set(self.towers.keys())
        active_ground_creeps = [
            c.current_grid_cell for c in self.creeps if not c.is_flying and not c.is_dead and not c.has_leaked
        ]

        if not self.pathfinder.can_place_tower(
            col, row, self.layout.spawn_cell, self.layout.goal_cell, occupied, active_ground_creeps
        ):
            self.vfx.add_floating_text("Weg blockiert!", pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], TEXT_RED)
            return

        self.gold -= tower_def.cost
        new_tower = Tower(col, row, tower_def, layout=self.layout)
        self.towers[coord] = new_tower
        self.recalculate_paths()

        self.audio.play("arrow_shot", volume=0.4)
        self.vfx.add_sparks(new_tower.x, new_tower.y, (120, 220, 255), count=14)

    def _try_upgrade_tower(self, tower: Tower) -> None:
        """Upgrade placed tower to higher tier."""
        if not tower.can_upgrade():
            return
        next_id = tower.definition.upgrade_to
        if not next_id:
            return
        next_def = get_tower_def(next_id)
        if not next_def:
            return

        if self.gold < next_def.cost:
            self.vfx.add_floating_text("Nicht genug Gold!", tower.x, tower.y, TEXT_RED)
            return

        self.gold -= next_def.cost
        tower.upgrade(next_def)
        self.audio.play("gold_interest", volume=0.4)
        self.vfx.add_sparks(tower.x, tower.y, (255, 230, 80), count=16)

    def _try_sell_tower(self, tower: Tower) -> None:
        """Sell tower and refund gold."""
        refund = tower.sell_value
        self.gold += refund
        coord = tower.grid_coord
        if coord in self.towers:
            del self.towers[coord]
        self.recalculate_paths()

        if self.selected_placed_tower == tower:
            self.selected_placed_tower = None

        self.audio.play("gold_interest", volume=0.45)
        self.vfx.add_floating_text(f"+{refund}g (Verkauft)", tower.x, tower.y, TEXT_GOLD)
        self.vfx.add_sparks(tower.x, tower.y, (240, 80, 80), count=10)

    def update(self, dt: float) -> None:
        """Update game simulation by dt seconds."""
        if self.game_state != "PLAYING" or self.is_paused:
            return

        effective_dt = dt * self.game_speed

        # 1. Update Interest Economy
        self.interest_timer += effective_dt
        if self.interest_timer >= INTEREST_INTERVAL:
            self.interest_timer -= INTEREST_INTERVAL
            rate = self.interest_rate + self.guardians.interest_bonus
            yield_gold = int(self.gold * rate)
            if yield_gold > 0:
                self.gold += yield_gold
                self.total_gold_earned += yield_gold
                self.audio.play("gold_interest", volume=0.55)
                self.vfx.add_floating_text(
                    f"+{yield_gold}g Zinsen!", self.layout.screen_width // 2, 85, TEXT_GOLD, size=16, lifetime=1.2
                )

        # 2. Wave Progression & Spawning
        self._update_waves(effective_dt)

        # 3. Creeps Movement, DoT & Leaks
        for creep in self.creeps:
            creep.update(effective_dt)
            if creep.has_leaked:
                self.lives -= 1 if creep.modifier != "boss" else 3
                self.audio.play("life_lost", volume=0.5)
                self.vfx.add_floating_text("-1 Leben!", creep.x, creep.y - 10, TEXT_RED, size=16)

                if self.lives <= 0:
                    self.lives = 0
                    self.game_state = "GAME_OVER"
                    self.audio.play("game_over", volume=0.6)
                    return

                if self.cached_ground_path:
                    creep.respawn_at_start(self.cached_ground_path)

        # 4. Towers Update & Combat
        for tower in self.towers.values():
            tower.update(
                effective_dt,
                self.creeps,
                self.projectiles,
                self.beams,
                self.chain_lightnings,
                self.vfx,
                self.audio,
                self.on_creep_killed,
            )

        # 5. Projectiles Update
        for p in self.projectiles:
            p.update(effective_dt, self.creeps, self.vfx)
        self.projectiles = [p for p in self.projectiles if not p.is_done]

        # 6. Beams & Chains Update
        for b in self.beams:
            b.update(effective_dt)
        self.beams = [b for b in self.beams if not b.is_done]

        for cl in self.chain_lightnings:
            cl.update(effective_dt)
        self.chain_lightnings = [cl for cl in self.chain_lightnings if not cl.is_done]

        # 7. Remove dead creeps
        self.creeps = [c for c in self.creeps if not c.is_dead]

        # 8. Particles & VFX
        self.vfx.update(effective_dt)

    def _update_waves(self, dt: float) -> None:
        """Spawn creeps for the current wave and transition between waves."""
        if self.current_wave_index >= len(self.wave_schedule):
            if not self.creeps:
                self.game_state = "VICTORY"
                self.audio.play("victory", volume=0.7)
            return

        current_cfg = self.wave_schedule[self.current_wave_index]

        if not self.is_wave_in_progress:
            self.wave_intermission_timer -= dt
            if self.wave_intermission_timer <= 0.0:
                self.is_wave_in_progress = True
                self.creeps_spawned_in_wave = 0
                self.wave_spawn_timer = 0.0

                if current_cfg.wave_num % 5 == 0:
                    self.guardians.add_token()
                    self.audio.play("guardian_summon", volume=0.55)
                    self.vfx.add_floating_text(
                        "Neuer Wächter-Token verfügbar!",
                        self.layout.screen_width // 2,
                        110,
                        TEXT_GOLD,
                        size=18,
                        lifetime=2.0,
                    )
        else:
            if self.creeps_spawned_in_wave < current_cfg.creep_count:
                self.wave_spawn_timer -= dt
                if self.wave_spawn_timer <= 0.0:
                    self.wave_spawn_timer = current_cfg.spawn_interval
                    self._spawn_creep(current_cfg)
                    self.creeps_spawned_in_wave += 1
            else:
                if not self.creeps:
                    self.is_wave_in_progress = False
                    self.current_wave_index += 1
                    self.wave_intermission_timer = 3.5

    def _spawn_creep(self, cfg: WaveConfig) -> None:
        """Instantiate and spawn a single creep."""
        path = self.cached_ground_path if not cfg.is_flying else None
        creep = Creep(
            creep_id=self.current_wave_index * 1000 + self.creeps_spawned_in_wave,
            name=cfg.name,
            wave_num=cfg.wave_num,
            max_hp=cfg.base_hp,
            speed=cfg.speed,
            armor_element=cfg.armor_element,
            gold_reward=cfg.gold_reward,
            is_flying=cfg.is_flying,
            modifier=cfg.modifier,
            path=path,
            layout=self.layout,
        )
        self.creeps.append(creep)

    def draw(self) -> None:
        """Render the complete game frame."""
        self.screen.fill(BG_DARK)
        self.ui.clear_clickables()

        if self.game_state == "START_MENU":
            self._draw_start_menu()
        elif self.game_state == "PLAYING":
            self._draw_playing_screen()
        elif self.game_state == "VICTORY":
            self._draw_end_screen(is_victory=True)
        elif self.game_state == "GAME_OVER":
            self._draw_end_screen(is_victory=False)

        if not self.headless:
            pygame.display.flip()

    def _draw_playing_screen(self) -> None:
        """Render active gameplay screen."""
        # 1. Grid
        self.ui.draw_grid_background(
            self.layout, self.layout.spawn_cell, self.layout.goal_cell, self.cached_ground_path
        )

        # 2. Towers
        for tower in self.towers.values():
            is_sel = self.selected_placed_tower == tower
            tower.draw(self.screen, is_selected=is_sel)

        # 3. Creeps (with procedural sprites)
        for c in self.creeps:
            c.draw(self.screen)

        # 4. Projectiles, Beams, Lightning
        for p in self.projectiles:
            p.draw(self.screen)
        for b in self.beams:
            b.draw(self.screen)
        for cl in self.chain_lightnings:
            cl.draw(self.screen)

        # 5. VFX Particles & Floating Texts
        self.vfx.draw(self.screen)

        # 6. Placement or Eraser preview under cursor
        mouse_pos = pygame.mouse.get_pos()
        grid_coord = self.layout.pixel_to_grid(mouse_pos)
        if grid_coord:
            if self.is_eraser_mode:
                hovered_t = self.towers.get(grid_coord)
                self.ui.draw_eraser_preview(self.layout, grid_coord, hovered_t)
            elif self.selected_build_def:
                occupied = set(self.towers.keys())
                active_creeps_cells = [
                    c.current_grid_cell for c in self.creeps if not c.is_flying and not c.is_dead and not c.has_leaked
                ]
                can_build = (self.gold >= self.selected_build_def.cost) and self.pathfinder.can_place_tower(
                    grid_coord[0], grid_coord[1], self.layout.spawn_cell, self.layout.goal_cell, occupied, active_creeps_cells
                )
                self.ui.draw_placement_preview(self.layout, grid_coord, self.selected_build_def, can_build)

        # 7. Element Circle helper
        self.ui.draw_element_circle_helper(self.layout)

        # 8. Top Resource Bar
        next_cfg = self.wave_schedule[self.current_wave_index] if self.current_wave_index < len(self.wave_schedule) else None
        current_wave_num = self.current_wave_index + 1 if self.current_wave_index < len(self.wave_schedule) else len(self.wave_schedule)

        def toggle_speed():
            self.game_speed = 2.0 if self.game_speed == 1.0 else (4.0 if self.game_speed == 2.0 else 1.0)

        def toggle_pause():
            self.is_paused = not self.is_paused

        def open_summon():
            self.show_guardian_modal = True

        self.ui.draw_top_bar(
            self.layout,
            self.gold,
            self.lives,
            current_wave_num,
            self.mode_total_waves,
            next_cfg,
            self.interest_timer,
            INTEREST_INTERVAL,
            self.interest_rate + self.guardians.interest_bonus,
            self.game_speed,
            self.is_paused,
            self.is_fullscreen,
            self.is_eraser_mode,
            self.guardians.available_tokens,
            toggle_speed,
            toggle_pause,
            self.toggle_fullscreen,
            self.toggle_eraser_mode,
            open_summon,
        )

        # 9. Sidebar Build & Inspector
        def on_select_build(tdef: TowerDefinition):
            self.selected_build_def = tdef
            self.selected_placed_tower = None
            self.is_eraser_mode = False

        self.ui.draw_sidebar(
            self.layout,
            self.gold,
            self.guardians.essences,
            self.selected_build_def,
            self.selected_placed_tower,
            on_select_build,
            self._try_upgrade_tower,
            self._try_sell_tower,
            is_eraser_mode=self.is_eraser_mode,
        )

        # 10. Guardian Summon Altar Modal
        if self.show_guardian_modal:
            def on_summon_el(elem: Element):
                if self.cached_ground_path:
                    boss = self.guardians.summon_guardian(elem, current_wave_num, self.cached_ground_path)
                    if boss:
                        boss.layout = self.layout
                        self.creeps.append(boss)
                        self.audio.play("guardian_summon", volume=0.6)
                        self.show_guardian_modal = False

            def on_choose_int():
                added = self.guardians.choose_interest_upgrade()
                if added > 0:
                    self.audio.play("gold_interest", volume=0.6)
                    self.vfx.add_floating_text(
                        "+0.5% Zinsen dauerhaft!", self.layout.screen_width // 2, self.layout.screen_height // 2, TEXT_GOLD, size=20
                    )
                    self.show_guardian_modal = False

            def on_close_modal():
                self.show_guardian_modal = False

            self.ui.draw_summon_altar_modal(
                self.layout,
                self.guardians,
                current_wave_num,
                on_summon_el,
                on_choose_int,
                on_close_modal,
            )

    def _draw_start_menu(self) -> None:
        """Render interactive Start & Configuration screen with resolution choices."""
        sw = self.layout.screen_width
        sh = self.layout.screen_height

        title = self.ui.font_title.render("ELEMENT TOWER DEFENSE", True, TEXT_GOLD)
        self.screen.blit(title, (sw // 2 - title.get_width() // 2, 70))

        sub = self.ui.font_large.render("Warcraft III Python Adaptation", True, TEXT_COLOR)
        self.screen.blit(sub, (sw // 2 - sub.get_width() // 2, 115))

        box_w = 640
        box_h = 490
        box_rect = pygame.Rect(sw // 2 - box_w // 2, 170, box_w, box_h)
        pygame.draw.rect(self.screen, BG_PANEL, box_rect, border_radius=12)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, box_rect, width=2, border_radius=12)

        # 1. Mode: Quick vs Full
        m_lbl = self.ui.font_bold.render("Spielmodus:", True, TEXT_MUTED)
        self.screen.blit(m_lbl, (box_rect.x + 30, box_rect.y + 20))

        btn_quick = pygame.Rect(box_rect.x + 30, box_rect.y + 45, 275, 42)
        is_q = self.mode_total_waves == 20
        pygame.draw.rect(self.screen, BG_PANEL_ALT if is_q else (20, 25, 35), btn_quick, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD if is_q else BG_PANEL_BORDER, btn_quick, width=2 if is_q else 1, border_radius=6)
        q_txt = self.ui.font_bold.render("Schnell (20 Wellen)", True, TEXT_GOLD if is_q else TEXT_COLOR)
        self.screen.blit(q_txt, (btn_quick.centerx - q_txt.get_width() // 2, btn_quick.centery - q_txt.get_height() // 2))
        self.ui.add_clickable(btn_quick, lambda: self._set_mode(20))

        btn_full = pygame.Rect(box_rect.x + 335, box_rect.y + 45, 275, 42)
        is_f = self.mode_total_waves == 60
        pygame.draw.rect(self.screen, BG_PANEL_ALT if is_f else (20, 25, 35), btn_full, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD if is_f else BG_PANEL_BORDER, btn_full, width=2 if is_f else 1, border_radius=6)
        f_txt = self.ui.font_bold.render("Vollständig (60 Wellen)", True, TEXT_GOLD if is_f else TEXT_COLOR)
        self.screen.blit(f_txt, (btn_full.centerx - f_txt.get_width() // 2, btn_full.centery - f_txt.get_height() // 2))
        self.ui.add_clickable(btn_full, lambda: self._set_mode(60))

        # 2. Difficulty
        d_lbl = self.ui.font_bold.render("Schwierigkeitsgrad:", True, TEXT_MUTED)
        self.screen.blit(d_lbl, (box_rect.x + 30, box_rect.y + 105))

        diff_names = ["Normal", "Hard", "Chaos"]
        btn_w = 180
        for i, dname in enumerate(diff_names):
            d_rect = pygame.Rect(box_rect.x + 30 + i * (btn_w + 20), box_rect.y + 130, btn_w, 40)
            is_d = self.difficulty_name == dname
            pygame.draw.rect(self.screen, BG_PANEL_ALT if is_d else (20, 25, 35), d_rect, border_radius=6)
            pygame.draw.rect(self.screen, TEXT_GOLD if is_d else BG_PANEL_BORDER, d_rect, width=2 if is_d else 1, border_radius=6)
            d_txt = self.ui.font_bold.render(dname, True, TEXT_GOLD if is_d else TEXT_COLOR)
            self.screen.blit(d_txt, (d_rect.centerx - d_txt.get_width() // 2, d_rect.centery - d_txt.get_height() // 2))

            def make_diff_cb(dn: str):
                return lambda: self._set_difficulty(dn)
            self.ui.add_clickable(d_rect, make_diff_cb(dname))

        # 3. Resolution Selection
        r_lbl = self.ui.font_bold.render("Auflösung & Format:", True, TEXT_MUTED)
        self.screen.blit(r_lbl, (box_rect.x + 30, box_rect.y + 190))

        # 1920x1080 Button
        r1_rect = pygame.Rect(box_rect.x + 30, box_rect.y + 215, 275, 42)
        is_r1 = self.current_width == 1920
        pygame.draw.rect(self.screen, BG_PANEL_ALT if is_r1 else (20, 25, 35), r1_rect, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD if is_r1 else BG_PANEL_BORDER, r1_rect, width=2 if is_r1 else 1, border_radius=6)
        r1_txt = self.ui.font_bold.render("1920 x 1080 (16:9 Full HD)", True, TEXT_GOLD if is_r1 else TEXT_COLOR)
        self.screen.blit(r1_txt, (r1_rect.centerx - r1_txt.get_width() // 2, r1_rect.centery - r1_txt.get_height() // 2))
        self.ui.add_clickable(r1_rect, lambda: self.set_resolution(1920, 1080))

        # 2560x1080 Button (Ultrawide)
        r2_rect = pygame.Rect(box_rect.x + 335, box_rect.y + 215, 275, 42)
        is_r2 = self.current_width == 2560
        pygame.draw.rect(self.screen, BG_PANEL_ALT if is_r2 else (20, 25, 35), r2_rect, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD if is_r2 else BG_PANEL_BORDER, r2_rect, width=2 if is_r2 else 1, border_radius=6)
        r2_txt = self.ui.font_bold.render("2560 x 1080 (21:9 Ultrawide)", True, TEXT_GOLD if is_r2 else TEXT_COLOR)
        self.screen.blit(r2_txt, (r2_rect.centerx - r2_txt.get_width() // 2, r2_rect.centery - r2_txt.get_height() // 2))
        self.ui.add_clickable(r2_rect, lambda: self.set_resolution(2560, 1080))

        # Fullscreen Checkbox/Toggle Button
        fs_btn_rect = pygame.Rect(box_rect.x + 30, box_rect.y + 275, 580, 40)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, fs_btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD if self.is_fullscreen else BG_PANEL_BORDER, fs_btn_rect, width=1, border_radius=6)
        fs_str = "Vollbildmodus: AKTIVIERT [F11 zum Wechseln]" if self.is_fullscreen else "Vollbildmodus: DEAKTIVIERT (Fenstermodus) [F11]"
        fs_col = TEXT_GOLD if self.is_fullscreen else TEXT_MUTED
        fs_surf = self.ui.font_bold.render(fs_str, True, fs_col)
        self.screen.blit(fs_surf, (fs_btn_rect.centerx - fs_surf.get_width() // 2, fs_btn_rect.centery - fs_surf.get_height() // 2))
        self.ui.add_clickable(fs_btn_rect, self.toggle_fullscreen)

        # 4. Start Button
        start_rect = pygame.Rect(box_rect.x + 50, box_rect.bottom - 75, box_rect.width - 100, 54)
        pygame.draw.rect(self.screen, (30, 85, 45), start_rect, border_radius=8)
        pygame.draw.rect(self.screen, TEXT_GREEN, start_rect, width=2, border_radius=8)
        st_txt = self.ui.font_title.render("SPIEL STARTEN", True, (255, 255, 255))
        self.screen.blit(st_txt, (start_rect.centerx - st_txt.get_width() // 2, start_rect.centery - st_txt.get_height() // 2))
        self.ui.add_clickable(start_rect, lambda: self.start_game(self.mode_total_waves, self.difficulty_name))

    def _set_mode(self, waves: int) -> None:
        self.mode_total_waves = waves

    def _set_difficulty(self, diff: str) -> None:
        self.difficulty_name = diff

    def _draw_end_screen(self, is_victory: bool) -> None:
        """Render victory or game over screen with vector trophy/skull icons."""
        sw = self.layout.screen_width
        sh = self.layout.screen_height

        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title_color = TEXT_GREEN if is_victory else TEXT_RED
        title_str = "SIEG! ALLE WELLEN ABGEWEHRT!" if is_victory else "NIEDERLAGE! DEINE LEBEN SIND ERSCHÖPFT!"
        title = self.ui.font_title.render(title_str, True, title_color)

        # Big icon
        end_ico = IconRenderer.get_icon("trophy" if is_victory else "skull", 44)
        self.screen.blit(end_ico, (sw // 2 - end_ico.get_width() // 2, 140))
        self.screen.blit(title, (sw // 2 - title.get_width() // 2, 200))

        card_rect = pygame.Rect(sw // 2 - 240, 260, 480, 220)
        pygame.draw.rect(self.screen, BG_PANEL, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, card_rect, width=2, border_radius=10)

        stats = [
            ("Erreichte Welle", f"{self.current_wave_index} / {self.mode_total_waves}"),
            ("Besiegte Monster", f"{self.total_kills}"),
            ("Gesamtes Gold verdient", f"{self.total_gold_earned}g"),
            ("Schwierigkeit", self.difficulty_name),
        ]

        for i, (k, v) in enumerate(stats):
            sy = card_rect.y + 25 + i * 38
            ks = self.ui.font_regular.render(k, True, TEXT_MUTED)
            vs = self.ui.font_bold.render(v, True, TEXT_COLOR)
            self.screen.blit(ks, (card_rect.x + 30, sy))
            self.screen.blit(vs, (card_rect.right - vs.get_width() - 30, sy))

        re_rect = pygame.Rect(sw // 2 - 150, 510, 300, 52)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, re_rect, border_radius=8)
        pygame.draw.rect(self.screen, TEXT_GOLD, re_rect, width=2, border_radius=8)
        re_lbl = self.ui.font_large.render("Hauptmenü", True, TEXT_GOLD)
        self.screen.blit(re_lbl, (re_rect.centerx - re_lbl.get_width() // 2, re_rect.centery - re_lbl.get_height() // 2))
        self.ui.add_clickable(re_rect, self._return_to_menu)

    def _return_to_menu(self) -> None:
        self.game_state = "START_MENU"

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(0.1, dt)

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
