"""User interface, HUD rendering, modal dialogs, and interactive widgets."""

import math
from typing import Callable, Dict, List, Optional, Tuple
import pygame
from py_warcraft_td.config import (
    BG_DARK,
    BG_GRID_A,
    BG_GRID_B,
    BG_PANEL,
    BG_PANEL_ALT,
    BG_PANEL_BORDER,
    GRID_LINE_COLOR,
    LayoutConfig,
    TEXT_COLOR,
    TEXT_GOLD,
    TEXT_GREEN,
    TEXT_MUTED,
    TEXT_RED,
)
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import (
    ELEMENT_CIRCLE,
    ELEMENT_NAMES_DE,
    Element,
    get_armor_resistance,
    get_armor_weakness,
    get_element_color,
)
from py_warcraft_td.guardians import GuardianManager
from py_warcraft_td.icons import IconRenderer
from py_warcraft_td.pathfinding import GridCoord
from py_warcraft_td.sprites import SpriteRenderer
from py_warcraft_td.towers.tower_base import Tower
from py_warcraft_td.towers.tower_catalog import (
    BASE_ELEMENTAL_TOWERS,
    DUAL_TOWERS,
    STARTER_TOWERS,
    TRIPLE_TOWERS,
    TowerDefinition,
    get_tower_def,
)
from py_warcraft_td.waves import WaveConfig


class UIManager:
    """Renders the top HUD, sidebar build panels, modal dialogs, and tooltips using vector icons."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.SysFont("Segoe UI", 12)
        self.font_regular = pygame.font.SysFont("Segoe UI", 14)
        self.font_bold = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_large = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)

        # Tab navigation for tower sidebar: "starter", "base", "dual", "triple"
        self.active_tab: str = "starter"

        # UI Clickable regions (registered dynamically every frame)
        self.clickable_regions: List[Tuple[pygame.Rect, Callable[[], None]]] = []

    def clear_clickables(self) -> None:
        self.clickable_regions.clear()

    def add_clickable(self, rect: pygame.Rect, callback: Callable[[], None]) -> None:
        self.clickable_regions.append((rect, callback))

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Execute callback if click hits a registered region. Returns True if handled."""
        for rect, cb in self.clickable_regions:
            if rect.collidepoint(mouse_pos):
                cb()
                return True
        return False

    def draw_top_bar(
        self,
        layout: LayoutConfig,
        gold: int,
        lives: int,
        current_wave: int,
        max_waves: int,
        next_wave_cfg: Optional[WaveConfig],
        interest_timer: float,
        interest_interval: float,
        interest_rate: float,
        game_speed: float,
        is_paused: bool,
        is_fullscreen: bool,
        is_eraser_mode: bool,
        guardian_tokens: int,
        on_speed_toggle: Callable[[], None],
        on_pause_toggle: Callable[[], None],
        on_fullscreen_toggle: Callable[[], None],
        on_eraser_toggle: Callable[[], None],
        on_summon_click: Callable[[], None],
        active_creeps_count: int = 0,
        on_exit_click: Optional[Callable[[], None]] = None,
    ) -> None:
        """Render the top resource bar and stats using procedural vector icons."""
        sw = layout.screen_width
        bar_rect = pygame.Rect(0, 0, sw, layout.top_bar_height)
        pygame.draw.rect(self.screen, BG_PANEL, bar_rect)
        pygame.draw.line(self.screen, BG_PANEL_BORDER, (0, layout.top_bar_height), (sw, layout.top_bar_height), 2)

        # 1. Gold with Icon
        gold_icon = IconRenderer.get_icon("gold", 24)
        self.screen.blit(gold_icon, (24, 20))
        gold_text = self.font_large.render(f"{gold} Gold", True, TEXT_GOLD)
        self.screen.blit(gold_text, (54, 18))

        # 2. Lives with Icon
        heart_icon = IconRenderer.get_icon("heart", 22)
        self.screen.blit(heart_icon, (185, 21))
        lives_color = TEXT_GREEN if lives > 20 else (TEXT_GOLD if lives > 10 else TEXT_RED)
        lives_text = self.font_large.render(f"{lives} Leben", True, lives_color)
        self.screen.blit(lives_text, (214, 18))

        # 3. Wave Indicator
        wave_str = f"Welle {current_wave} / {max_waves}" if current_wave <= max_waves else "Alle Wellen besiegt!"
        wave_text = self.font_large.render(wave_str, True, TEXT_COLOR)
        self.screen.blit(wave_text, (335, 18))

        # 4. Next wave preview
        if next_wave_cfg:
            elem_name = ELEMENT_NAMES_DE.get(next_wave_cfg.armor_element, "Normal")
            color, _ = get_element_color(next_wave_cfg.armor_element)
            elem_ico = IconRenderer.get_element_icon(next_wave_cfg.armor_element, 16)
            self.screen.blit(elem_ico, (335, 44))

            fly_str = " (Fliegend)" if next_wave_cfg.is_flying else ""
            preview_str = f"{next_wave_cfg.name} [{elem_name}]{fly_str} x{next_wave_cfg.creep_count}"
            prev_surf = self.font_regular.render(preview_str, True, color)
            self.screen.blit(prev_surf, (357, 43))

        # 4b. Active Creep Counter on Field (Always shows living enemy units)
        creep_cnt_x = 505
        monster_icon = IconRenderer.get_icon("monster", 22)
        self.screen.blit(monster_icon, (creep_cnt_x, 21))
        cnt_color = TEXT_RED if active_creeps_count > 30 else (TEXT_GOLD if active_creeps_count > 15 else TEXT_COLOR)
        cnt_text = self.font_large.render(f"{active_creeps_count} Einheiten", True, cnt_color)
        self.screen.blit(cnt_text, (creep_cnt_x + 30, 18))
        cnt_sub = self.font_small.render("aktiv auf Karte", True, TEXT_MUTED)
        self.screen.blit(cnt_sub, (creep_cnt_x + 32, 44))

        # 5. Interest Timer Bar
        bar_w = 150
        bar_h = 16
        bar_x = 690 if sw >= 1800 else 660
        bar_y = 22
        time_left = max(0.0, interest_interval - interest_timer)
        progress = max(0.0, min(1.0, 1.0 - (time_left / interest_interval)))

        pygame.draw.rect(self.screen, BG_PANEL_ALT, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(self.screen, TEXT_GOLD, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=4)

        interest_yield = int(gold * interest_rate)
        interest_lbl = self.font_small.render(
            f"Zinsen ({interest_rate*100:.1f}%): +{interest_yield}g ({time_left:.1f}s)", True, TEXT_COLOR
        )
        self.screen.blit(interest_lbl, (bar_x, bar_y + 20))

        # 6. Guardian Summon Altar Button
        altar_x = bar_x + bar_w + 25
        altar_y = 14
        altar_rect = pygame.Rect(altar_x, altar_y, 165, 42)

        swords_icon = IconRenderer.get_icon("swords", 22)
        if guardian_tokens > 0:
            pygame.draw.rect(self.screen, (60, 45, 10), altar_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 230, 80), altar_rect, width=2, border_radius=6)
            btn_txt = self.font_bold.render(f"Wächter ({guardian_tokens})", True, TEXT_GOLD)
        else:
            pygame.draw.rect(self.screen, BG_PANEL_ALT, altar_rect, border_radius=6)
            pygame.draw.rect(self.screen, BG_PANEL_BORDER, altar_rect, width=1, border_radius=6)
            btn_txt = self.font_regular.render("Wächter-Altar", True, TEXT_MUTED)

        self.screen.blit(swords_icon, (altar_rect.x + 8, altar_rect.y + 10))
        self.screen.blit(btn_txt, (altar_rect.x + 34, altar_rect.y + 11))
        self.add_clickable(altar_rect, on_summon_click)

        # 7. Eraser / Demolish Mode Button & Control Buttons
        ctrl_x = sw - 540
        eraser_rect = pygame.Rect(ctrl_x, 14, 115, 42)
        if is_eraser_mode:
            pygame.draw.rect(self.screen, (70, 25, 30), eraser_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 80, 100), eraser_rect, width=2, border_radius=6)
            erase_txt = self.font_bold.render("Löschen [X]", True, (255, 130, 150))
        else:
            pygame.draw.rect(self.screen, BG_PANEL_ALT, eraser_rect, border_radius=6)
            pygame.draw.rect(self.screen, BG_PANEL_BORDER, eraser_rect, width=1, border_radius=6)
            erase_txt = self.font_bold.render("Löschen [X]", True, TEXT_MUTED)

        eraser_ico = IconRenderer.get_icon("eraser", 20)
        self.screen.blit(eraser_ico, (eraser_rect.x + 8, eraser_rect.y + 11))
        self.screen.blit(erase_txt, (eraser_rect.x + 30, eraser_rect.y + 11))
        self.add_clickable(eraser_rect, on_eraser_toggle)

        # 8. Speed, Pause, and Fullscreen Controls
        speed_rect = pygame.Rect(ctrl_x + 123, 14, 75, 42)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, speed_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, speed_rect, width=1, border_radius=6)
        spd_ico = IconRenderer.get_icon("fast_forward", 18)
        self.screen.blit(spd_ico, (speed_rect.x + 8, speed_rect.y + 12))
        spd_surf = self.font_bold.render(f"{int(game_speed)}x", True, TEXT_COLOR)
        self.screen.blit(spd_surf, (speed_rect.x + 30, speed_rect.y + 11))
        self.add_clickable(speed_rect, on_speed_toggle)

        pause_rect = pygame.Rect(ctrl_x + 206, 14, 90, 42)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, pause_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, pause_rect, width=1, border_radius=6)
        p_ico = IconRenderer.get_icon("play" if is_paused else "pause", 18)
        self.screen.blit(p_ico, (pause_rect.x + 8, pause_rect.y + 12))
        p_surf = self.font_bold.render("Weiter" if is_paused else "Pause", True, TEXT_COLOR)
        self.screen.blit(p_surf, (pause_rect.x + 30, pause_rect.y + 11))
        self.add_clickable(pause_rect, on_pause_toggle)

        # Fullscreen Toggle Button (F11)
        fs_rect = pygame.Rect(ctrl_x + 304, 14, 100, 42)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, fs_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, fs_rect, width=1, border_radius=6)
        fs_lbl = self.font_bold.render("[F11] Voll" if not is_fullscreen else "[F11] Fen.", True, (190, 210, 240))
        self.screen.blit(fs_lbl, (fs_rect.centerx - fs_lbl.get_width() // 2, fs_rect.centery - fs_lbl.get_height() // 2))
        self.add_clickable(fs_rect, on_fullscreen_toggle)

        # 9. Exit / Game End Button (Doorway icon)
        if on_exit_click:
            exit_rect = pygame.Rect(ctrl_x + 412, 14, 115, 42)
            pygame.draw.rect(self.screen, (45, 20, 24), exit_rect, border_radius=6)
            pygame.draw.rect(self.screen, (190, 60, 70), exit_rect, width=1, border_radius=6)
            exit_ico = IconRenderer.get_icon("exit", 18)
            self.screen.blit(exit_ico, (exit_rect.x + 8, exit_rect.y + 12))
            exit_txt = self.font_bold.render("Beenden", True, (255, 140, 150))
            self.screen.blit(exit_txt, (exit_rect.x + 32, exit_rect.y + 11))
            self.add_clickable(exit_rect, on_exit_click)

    def draw_grid_background(
        self,
        layout: LayoutConfig,
        spawn_coord: GridCoord,
        goal_coord: GridCoord,
        active_path: Optional[List[GridCoord]],
    ) -> None:
        """Render the tactical grid and paths respecting LayoutConfig."""
        cols = layout.grid_cols
        rows = layout.grid_rows
        cs = layout.cell_size
        ox = layout.grid_offset_x
        oy = layout.grid_offset_y

        for r in range(rows):
            for c in range(cols):
                cx = ox + c * cs
                cy = oy + r * cs
                rect = pygame.Rect(cx, cy, cs, cs)

                bg_color = BG_GRID_A if (r + c) % 2 == 0 else BG_GRID_B
                pygame.draw.rect(self.screen, bg_color, rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, width=1)

        # Portals
        sp_px = layout.grid_to_pixel(spawn_coord)
        gl_px = layout.grid_to_pixel(goal_coord)

        # Spawn Portal (Emerald with rune)
        pygame.draw.circle(self.screen, (40, 180, 80), (int(sp_px[0]), int(sp_px[1])), int(cs / 2.0 - 2))
        sp_label = self.font_small.render("START", True, (255, 255, 255))
        self.screen.blit(sp_label, (int(sp_px[0] - sp_label.get_width() / 2), int(sp_px[1] - sp_label.get_height() / 2)))

        # Goal Portal (Crimson with rune)
        pygame.draw.circle(self.screen, (220, 60, 60), (int(gl_px[0]), int(gl_px[1])), int(cs / 2.0 - 2))
        gl_label = self.font_small.render("ZIEL", True, (255, 255, 255))
        self.screen.blit(gl_label, (int(gl_px[0] - gl_label.get_width() / 2), int(gl_px[1] - gl_label.get_height() / 2)))

        # Dynamic Route Line
        if active_path and len(active_path) > 1:
            points = [layout.grid_to_pixel(c) for c in active_path]
            pygame.draw.lines(self.screen, (60, 110, 175), False, points, 2)

    def draw_placement_preview(
        self,
        layout: LayoutConfig,
        grid_coord: GridCoord,
        tower_def: TowerDefinition,
        is_valid: bool,
    ) -> None:
        """Render build preview rectangle and attack range circle under cursor."""
        col, row = grid_coord
        cs = layout.cell_size
        cx = layout.grid_offset_x + col * cs
        cy = layout.grid_offset_y + row * cs
        center_x = cx + cs / 2.0
        center_y = cy + cs / 2.0

        color = (80, 230, 100) if is_valid else (240, 60, 60)

        # Range circle
        range_surf = pygame.Surface((layout.screen_width, layout.screen_height), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (*color, 45), (int(center_x), int(center_y)), int(tower_def.range_px))
        pygame.draw.circle(range_surf, (*color, 180), (int(center_x), int(center_y)), int(tower_def.range_px), width=1)
        self.screen.blit(range_surf, (0, 0))

        # Cell box
        pygame.draw.rect(self.screen, color, (cx, cy, cs, cs), width=2)

    def draw_eraser_preview(
        self,
        layout: LayoutConfig,
        grid_coord: GridCoord,
        hovered_tower: Optional[Tower],
    ) -> None:
        """Render eraser brush rectangle and refund tooltip over hovered cell."""
        col, row = grid_coord
        cs = layout.cell_size
        cx = layout.grid_offset_x + col * cs
        cy = layout.grid_offset_y + row * cs

        if hovered_tower:
            # Highlight tower cell with glowing red demolish outline
            pygame.draw.rect(self.screen, (255, 60, 80), (cx, cy, cs, cs), width=3)
            # Floating refund label
            refund_str = f"+{hovered_tower.sell_value}g"
            txt_surf = self.font_bold.render(refund_str, True, (255, 220, 80))
            tag_rect = pygame.Rect(cx + cs // 2 - txt_surf.get_width() // 2 - 4, cy - 22, txt_surf.get_width() + 8, 20)
            pygame.draw.rect(self.screen, (35, 15, 20), tag_rect, border_radius=4)
            pygame.draw.rect(self.screen, (240, 70, 90), tag_rect, width=1, border_radius=4)
            self.screen.blit(txt_surf, (tag_rect.x + 4, tag_rect.y + 1))
        else:
            # Subtle eraser cell cursor
            pygame.draw.rect(self.screen, (240, 100, 120), (cx, cy, cs, cs), width=1)

    def draw_sidebar(
        self,
        layout: LayoutConfig,
        gold: int,
        unlocked_elements: Dict[Element, int],
        selected_build_def: Optional[TowerDefinition],
        selected_placed_tower: Optional[Tower],
        on_select_build_def: Callable[[TowerDefinition], None],
        on_upgrade_tower: Callable[[Tower], None],
        on_sell_tower: Callable[[Tower], None],
        is_eraser_mode: bool = False,
        selected_creep: Optional[Creep] = None,
        on_deselect_creep: Optional[Callable[[], None]] = None,
    ) -> None:
        """Render right sidebar with responsive multi-column layout."""
        panel_rect = pygame.Rect(layout.sidebar_x, layout.sidebar_y, layout.sidebar_width, layout.sidebar_height)
        pygame.draw.rect(self.screen, BG_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, panel_rect, width=2, border_radius=8)

        if is_eraser_mode:
            # Active eraser banner
            banner_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + 10, panel_rect.width - 20, 36)
            pygame.draw.rect(self.screen, (65, 20, 28), banner_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 80, 100), banner_rect, width=1, border_radius=6)
            e_ico = IconRenderer.get_icon("eraser", 20)
            self.screen.blit(e_ico, (banner_rect.x + 10, banner_rect.y + 8))
            e_msg = self.font_bold.render("LÖSCHEN-MODUS: Türme anklicken/überstreichen zum Abreißen [X]", True, (255, 140, 160))
            self.screen.blit(e_msg, (banner_rect.x + 38, banner_rect.y + 9))

        if selected_creep and not is_eraser_mode:
            self._draw_creep_inspector(panel_rect, selected_creep, on_deselect_creep)
            return

        if selected_placed_tower and not is_eraser_mode:
            self._draw_tower_inspector(
                panel_rect, selected_placed_tower, gold, unlocked_elements, on_upgrade_tower, on_sell_tower
            )
            return

        # Tabs
        tab_w = (layout.sidebar_width - 20) // 4
        tab_h = 34
        tabs = [
            ("starter", "Starter"),
            ("base", "Basis"),
            ("dual", "Dual (15)"),
            ("triple", "Triple (20)"),
        ]

        tabs_y = panel_rect.y + (54 if is_eraser_mode else 10)
        for i, (tab_id, tab_label) in enumerate(tabs):
            tx = panel_rect.x + 10 + i * tab_w
            ty = tabs_y
            t_rect = pygame.Rect(tx, ty, tab_w - 2, tab_h)

            is_active = self.active_tab == tab_id
            bg_col = BG_PANEL_ALT if is_active else BG_PANEL
            border_col = (255, 230, 80) if is_active else BG_PANEL_BORDER

            pygame.draw.rect(self.screen, bg_col, t_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_col, t_rect, width=1, border_radius=4)

            lbl = self.font_bold.render(tab_label, True, TEXT_GOLD if is_active else TEXT_MUTED)
            self.screen.blit(lbl, (t_rect.centerx - lbl.get_width() // 2, t_rect.centery - lbl.get_height() // 2))

            def make_tab_cb(tid: str):
                return lambda: self._set_tab(tid)
            self.add_clickable(t_rect, make_tab_cb(tab_id))

        content_y = tabs_y + 44
        self._draw_tower_list(
            panel_rect, content_y, gold, unlocked_elements, selected_build_def, on_select_build_def
        )

    def _set_tab(self, tab_id: str) -> None:
        self.active_tab = tab_id

    def _draw_tower_list(
        self,
        panel_rect: pygame.Rect,
        start_y: int,
        gold: int,
        unlocked_elements: Dict[Element, int],
        selected_build_def: Optional[TowerDefinition],
        on_select_build_def: Callable[[TowerDefinition], None],
    ) -> None:
        """Render tower list supporting 1 column (1080p) or 2 columns (Ultrawide)."""
        towers_to_show: List[TowerDefinition] = []
        if self.active_tab == "starter":
            towers_to_show = [t for t in STARTER_TOWERS.values() if t.tier == 1]
        elif self.active_tab == "base":
            towers_to_show = [t for t in BASE_ELEMENTAL_TOWERS.values() if t.tier == 1]
        elif self.active_tab == "dual":
            towers_to_show = list(DUAL_TOWERS.values())
        elif self.active_tab == "triple":
            towers_to_show = list(TRIPLE_TOWERS.values())

        # Determine column count based on available sidebar width
        num_cols = 2 if panel_rect.width >= 720 else 1
        card_h = 56
        card_w = (panel_rect.width - 24 - (num_cols - 1) * 12) // num_cols

        for i, tdef in enumerate(towers_to_show):
            c_idx = i % num_cols
            r_idx = i // num_cols

            cx = panel_rect.x + 12 + c_idx * (card_w + 12)
            cy = start_y + r_idx * (card_h + 8)

            if cy + card_h > panel_rect.bottom - 10:
                break

            card_rect = pygame.Rect(cx, cy, card_w, card_h)

            is_unlocked = True
            if tdef.category == "base":
                elem = tdef.elements[0]
                is_unlocked = unlocked_elements.get(elem, 0) >= 1
            elif tdef.category in ("dual", "triple"):
                is_unlocked = all(unlocked_elements.get(e, 0) >= 1 for e in tdef.elements)

            can_afford = gold >= tdef.cost
            is_selected = selected_build_def and selected_build_def.id == tdef.id

            bg_col = (42, 54, 76) if is_selected else (BG_PANEL_ALT if is_unlocked else (20, 24, 30))
            border_col = (255, 230, 80) if is_selected else ((80, 110, 150) if is_unlocked else (45, 50, 60))

            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_col, card_rect, width=1, border_radius=6)

            # Element Badges
            badge_x = card_rect.x + 8
            if tdef.elements:
                for elem in tdef.elements:
                    e_icon = IconRenderer.get_element_icon(elem, 18)
                    self.screen.blit(e_icon, (badge_x, card_rect.y + 7))
                    badge_x += 20
            else:
                none_icon = IconRenderer.get_icon("elem_none", 18)
                self.screen.blit(none_icon, (badge_x, card_rect.y + 7))
                badge_x += 20

            # Name
            name_x = badge_x + 4
            name_col = TEXT_COLOR if is_unlocked else TEXT_MUTED
            name_surf = self.font_bold.render(tdef.name, True, name_col)
            self.screen.blit(name_surf, (name_x, card_rect.y + 7))

            # Gold Cost with Icon
            cost_col = TEXT_GOLD if can_afford else TEXT_RED
            coin_icon = IconRenderer.get_icon("gold", 16)
            cost_surf = self.font_bold.render(f"{tdef.cost}g", True, cost_col)
            coin_x = card_rect.right - cost_surf.get_width() - 24
            self.screen.blit(coin_icon, (coin_x, card_rect.y + 9))
            self.screen.blit(cost_surf, (coin_x + 18, card_rect.y + 7))

            # Subtitle
            if is_unlocked:
                target_str = "Boden & Luft" if tdef.targets == "both" else ("Nur Luft" if tdef.targets == "air" else "Nur Boden")
                dps = tdef.damage / tdef.attack_cooldown
                stat_str = f"Schaden: {int(tdef.damage)} | DPS: {int(dps)} | {target_str}"
                sub_surf = self.font_small.render(stat_str, True, TEXT_MUTED)
                self.screen.blit(sub_surf, (card_rect.x + 8, card_rect.y + 32))
            else:
                lock_icon = IconRenderer.get_icon("lock", 14)
                self.screen.blit(lock_icon, (card_rect.x + 8, card_rect.y + 33))
                req_names = " + ".join([ELEMENT_NAMES_DE.get(e, "") for e in tdef.elements])
                sub_surf = self.font_small.render(f"Benötigt: {req_names}", True, (220, 110, 110))
                self.screen.blit(sub_surf, (card_rect.x + 26, card_rect.y + 32))

            if is_unlocked:
                def make_select_cb(td: TowerDefinition):
                    return lambda: on_select_build_def(td)
                self.add_clickable(card_rect, make_select_cb(tdef))

    def _draw_tower_inspector(
        self,
        panel_rect: pygame.Rect,
        tower: Tower,
        gold: int,
        unlocked_elements: Dict[Element, int],
        on_upgrade_tower: Callable[[Tower], None],
        on_sell_tower: Callable[[Tower], None],
    ) -> None:
        """Render detailed inspector card for a placed tower."""
        tdef = tower.definition

        title = self.font_large.render(tdef.name, True, TEXT_GOLD)
        self.screen.blit(title, (panel_rect.x + 18, panel_rect.y + 18))

        desc_surf = self.font_regular.render(tdef.description, True, TEXT_COLOR)
        self.screen.blit(desc_surf, (panel_rect.x + 18, panel_rect.y + 54))

        stats_y = panel_rect.y + 96
        dps = tdef.damage / tdef.attack_cooldown
        stats = [
            ("Kategorie", tdef.category.upper()),
            ("Elemente", " + ".join([ELEMENT_NAMES_DE.get(e, "") for e in tdef.elements]) if tdef.elements else "Keine"),
            ("Schaden", f"{int(tdef.damage)}"),
            ("Feuerrate", f"{tdef.attack_cooldown:.2f}s (DPS: {int(dps)})"),
            ("Reichweite", f"{int(tdef.range_px)} px"),
            ("Ziele", "Boden & Luft" if tdef.targets == "both" else ("Nur Luft" if tdef.targets == "air" else "Nur Boden")),
            ("Kills", f"{tower.kills}"),
            ("Schaden gesamt", f"{int(tower.damage_dealt)}"),
        ]

        for i, (label, val) in enumerate(stats):
            row_y = stats_y + i * 26
            l_surf = self.font_regular.render(label, True, TEXT_MUTED)
            v_surf = self.font_bold.render(val, True, TEXT_COLOR)
            self.screen.blit(l_surf, (panel_rect.x + 18, row_y))
            self.screen.blit(v_surf, (panel_rect.right - v_surf.get_width() - 24, row_y))

        # Upgrade Button with vector upgrade arrow
        btn_y = panel_rect.bottom - 75
        if tdef.upgrade_to:
            next_def = get_tower_def(tdef.upgrade_to)
            if next_def:
                can_afford = gold >= next_def.cost
                upg_rect = pygame.Rect(panel_rect.x + 18, btn_y, 200, 48)
                upg_col = BG_PANEL_ALT if can_afford else (30, 20, 20)
                pygame.draw.rect(self.screen, upg_col, upg_rect, border_radius=6)
                pygame.draw.rect(self.screen, TEXT_GOLD if can_afford else (80, 50, 50), upg_rect, width=1, border_radius=6)

                upg_ico = IconRenderer.get_icon("upgrade", 20)
                self.screen.blit(upg_ico, (upg_rect.x + 12, upg_rect.y + 14))

                btn_lbl = self.font_bold.render(f"Upgrade ({next_def.cost}g)", True, TEXT_GOLD if can_afford else TEXT_MUTED)
                self.screen.blit(btn_lbl, (upg_rect.x + 38, upg_rect.y + 14))

                if can_afford:
                    self.add_clickable(upg_rect, lambda: on_upgrade_tower(tower))

        # Sell Button with vector gold coin
        sell_rect = pygame.Rect(panel_rect.right - 210, btn_y, 190, 48)
        pygame.draw.rect(self.screen, (55, 25, 25), sell_rect, border_radius=6)
        pygame.draw.rect(self.screen, (220, 80, 80), sell_rect, width=1, border_radius=6)

        coin_ico = IconRenderer.get_icon("gold", 20)
        self.screen.blit(coin_ico, (sell_rect.x + 12, sell_rect.y + 14))
        sell_lbl = self.font_bold.render(f"Verkauf (+{tower.sell_value}g)", True, (255, 130, 130))
        self.screen.blit(sell_lbl, (sell_rect.x + 36, sell_rect.y + 14))
        self.add_clickable(sell_rect, lambda: on_sell_tower(tower))

    def _draw_creep_inspector(
        self,
        panel_rect: pygame.Rect,
        creep: Creep,
        on_deselect: Optional[Callable[[], None]] = None,
    ) -> None:
        """Render detailed inspector card for a selected enemy unit."""
        # 1. Header: Name & Close [X] button
        title = self.font_large.render(creep.name, True, TEXT_GOLD)
        self.screen.blit(title, (panel_rect.x + 18, panel_rect.y + 18))

        close_rect = pygame.Rect(panel_rect.right - 38, panel_rect.y + 14, 26, 26)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, close_rect, border_radius=4)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, close_rect, width=1, border_radius=4)
        close_lbl = self.font_bold.render("X", True, TEXT_MUTED)
        self.screen.blit(
            close_lbl, (close_rect.centerx - close_lbl.get_width() // 2, close_rect.centery - close_lbl.get_height() // 2)
        )
        if on_deselect:
            self.add_clickable(close_rect, on_deselect)

        # 2. Type badge / Subtitle
        m_type = "Fliegend" if creep.is_flying else "Boden"
        mod_name = {
            "normal": "Standard",
            "fast": "Schnell",
            "tank": "Gepanzert (Tank)",
            "swarm": "Schwarm",
            "boss": "BOSS",
            "shielded": "Geschützt",
            "regen": "Regeneration",
        }.get(creep.modifier, creep.modifier.capitalize())
        sub_str = f"Typ: {mod_name} | {m_type} | Welle {creep.wave_num}"
        sub_col = (255, 110, 110) if creep.modifier == "boss" else TEXT_MUTED
        sub_surf = self.font_regular.render(sub_str, True, sub_col)
        self.screen.blit(sub_surf, (panel_rect.x + 18, panel_rect.y + 50))

        # 3. Unit Sprite Preview Box
        sprite_box = pygame.Rect(panel_rect.x + 18, panel_rect.y + 78, 64, 64)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, sprite_box, border_radius=8)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, sprite_box, width=1, border_radius=8)

        creep_sprite = SpriteRenderer.get_creep_sprite(
            creep.armor_element, creep.modifier, creep.is_flying, size=52, anim_frame=creep.anim_tick
        )
        self.screen.blit(
            creep_sprite,
            (sprite_box.centerx - creep_sprite.get_width() // 2, sprite_box.centery - creep_sprite.get_height() // 2),
        )

        # 4. Numeric Health Bar (Directly adjacent to sprite box)
        hp_bar_x = panel_rect.x + 92
        hp_bar_y = panel_rect.y + 78
        hp_bar_w = panel_rect.width - 110
        hp_bar_h = 28

        hp_ratio = max(0.0, min(1.0, creep.hp / creep.max_hp if creep.max_hp > 0 else 0.0))
        pygame.draw.rect(self.screen, (35, 15, 15), (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=6)
        fill_w = int(hp_bar_w * hp_ratio)
        if fill_w > 0:
            hp_col = TEXT_GREEN if hp_ratio > 0.5 else (TEXT_GOLD if hp_ratio > 0.25 else TEXT_RED)
            pygame.draw.rect(self.screen, hp_col, (hp_bar_x, hp_bar_y, fill_w, hp_bar_h), border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), width=1, border_radius=6)

        # Exact numeric HP display
        hp_text_str = f"{int(creep.hp):,} / {int(creep.max_hp):,} HP ({hp_ratio * 100:.1f}%)"
        hp_text = self.font_bold.render(hp_text_str, True, (255, 255, 255))
        self.screen.blit(hp_text, (hp_bar_x + hp_bar_w // 2 - hp_text.get_width() // 2, hp_bar_y + 5))

        # Sub-bar details
        dist_surf = self.font_small.render(
            f"Kopfgeld: {creep.gold_reward}g | Distanz: {int(creep.total_distance_traveled)}px", True, TEXT_MUTED
        )
        self.screen.blit(dist_surf, (hp_bar_x, hp_bar_y + 36))

        # 5. Elemental Armor, Weakness & Resistance Section
        elem_y = panel_rect.y + 154
        elem_box = pygame.Rect(panel_rect.x + 18, elem_y, panel_rect.width - 36, 102)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, elem_box, border_radius=8)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, elem_box, width=1, border_radius=8)

        # Armor element
        arm_name = ELEMENT_NAMES_DE.get(creep.armor_element, "Normal")
        arm_col, _ = get_element_color(creep.armor_element)
        arm_ico = IconRenderer.get_element_icon(creep.armor_element, 18)
        self.screen.blit(arm_ico, (elem_box.x + 12, elem_box.y + 10))
        arm_lbl = self.font_bold.render(f"Rüstungstyp: {arm_name}", True, arm_col)
        self.screen.blit(arm_lbl, (elem_box.x + 36, elem_box.y + 9))

        # Schwäche (Weakness): Attacking element that deals 200% damage
        weak_elem = get_armor_weakness(creep.armor_element)
        if weak_elem and weak_elem != Element.NONE:
            weak_name = ELEMENT_NAMES_DE.get(weak_elem, weak_elem.value)
            w_ico = IconRenderer.get_element_icon(weak_elem, 18)
            self.screen.blit(w_ico, (elem_box.x + 12, elem_box.y + 40))
            w_txt = self.font_bold.render(f"Schwäche: {weak_name} (200% Schaden!)", True, (255, 110, 110))
            self.screen.blit(w_txt, (elem_box.x + 36, elem_box.y + 39))
        else:
            w_txt = self.font_regular.render("Schwäche: Keine (Neutral)", True, TEXT_MUTED)
            self.screen.blit(w_txt, (elem_box.x + 12, elem_box.y + 39))

        # Resistenz (Resistance): Attacking element that deals 50% damage
        res_elem = get_armor_resistance(creep.armor_element)
        if res_elem and res_elem != Element.NONE:
            res_name = ELEMENT_NAMES_DE.get(res_elem, res_elem.value)
            r_ico = IconRenderer.get_element_icon(res_elem, 18)
            self.screen.blit(r_ico, (elem_box.x + 12, elem_box.y + 70))
            r_txt = self.font_regular.render(f"Resistent gegen: {res_name} (50% Schaden)", True, (130, 200, 130))
            self.screen.blit(r_txt, (elem_box.x + 36, elem_box.y + 69))
        else:
            r_txt = self.font_regular.render("Resistenz: Keine", True, TEXT_MUTED)
            self.screen.blit(r_txt, (elem_box.x + 12, elem_box.y + 69))

        # 6. Detailed Unit Stats Table
        stats_y = elem_y + 116
        cur_speed = creep.base_speed * creep.slow_factor if creep.stun_timer <= 0 else 0.0
        stats = [
            ("Basis-Geschwindigkeit", f"{int(creep.base_speed)} px/s"),
            ("Aktuelle Geschw.", f"{int(cur_speed)} px/s" + (" (Verlangsamt)" if creep.slow_factor < 1.0 else "")),
            ("Gold-Belohnung", f"{creep.gold_reward} Gold"),
            ("Status", "Betäubt!" if creep.stun_timer > 0 else ("Aktiv" if not creep.is_dead else "Besiegt")),
        ]

        for i, (label, val) in enumerate(stats):
            row_y = stats_y + i * 26
            l_surf = self.font_regular.render(label, True, TEXT_MUTED)
            v_surf = self.font_bold.render(val, True, TEXT_COLOR)
            self.screen.blit(l_surf, (panel_rect.x + 18, row_y))
            self.screen.blit(v_surf, (panel_rect.right - v_surf.get_width() - 24, row_y))

        # 7. Active Status Effects Box
        eff_y = stats_y + len(stats) * 26 + 12
        effects_title = self.font_bold.render("Aktive Statuseffekte:", True, TEXT_GOLD)
        self.screen.blit(effects_title, (panel_rect.x + 18, eff_y))

        eff_rows = []
        if creep.slow_timer > 0:
            eff_rows.append(f"Verlangsamt: -{int((1.0 - creep.slow_factor) * 100)}% ({creep.slow_timer:.1f}s)")
        if creep.burn_timer > 0:
            eff_rows.append(f"Verbrennung: {int(creep.burn_dps)} DPS ({creep.burn_timer:.1f}s)")
        if creep.poison_timer > 0:
            eff_rows.append(f"Vergiftung: {int(creep.poison_dps)} DPS ({creep.poison_timer:.1f}s)")
        if creep.sunder_timer > 0:
            eff_rows.append(f"Rüstungsbruch: +{int(creep.sunder_factor * 100)}% Schaden ({creep.sunder_timer:.1f}s)")
        if creep.stun_timer > 0:
            eff_rows.append(f"Betäubt: Handlungsunfähig ({creep.stun_timer:.1f}s)")

        if not eff_rows:
            none_surf = self.font_regular.render("Keine negativen Statuseffekte aktiv.", True, TEXT_MUTED)
            self.screen.blit(none_surf, (panel_rect.x + 18, eff_y + 26))
        else:
            for idx, eff in enumerate(eff_rows):
                e_surf = self.font_regular.render(f"• {eff}", True, (240, 200, 100))
                self.screen.blit(e_surf, (panel_rect.x + 18, eff_y + 26 + idx * 22))

        # 8. Bottom Deselect Button
        btn_y = panel_rect.bottom - 60
        back_rect = pygame.Rect(panel_rect.x + 18, btn_y, panel_rect.width - 36, 44)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, back_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, back_rect, width=1, border_radius=6)
        b_txt = self.font_bold.render("Auswahl aufheben (Bau-Menü)", True, TEXT_COLOR)
        self.screen.blit(b_txt, (back_rect.centerx - b_txt.get_width() // 2, back_rect.centery - b_txt.get_height() // 2))
        if on_deselect:
            self.add_clickable(back_rect, on_deselect)

    def draw_summon_altar_modal(
        self,
        layout: LayoutConfig,
        guardian_mgr: GuardianManager,
        wave_num: int,
        on_summon_element: Callable[[Element], None],
        on_choose_interest: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        """Render the Elemental Guardian Summoning Modal with vector badges."""
        overlay = pygame.Surface((layout.screen_width, layout.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))

        mw, mh = 820, 540
        mx = (layout.screen_width - mw) // 2
        my = (layout.screen_height - mh) // 2
        modal_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(self.screen, BG_PANEL, modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 60), modal_rect, width=2, border_radius=12)

        # Title
        title = self.font_title.render("BESCHWÖRUNGS-ALTAR DER ELEMENTE", True, TEXT_GOLD)
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, modal_rect.y + 20))

        sub_msg = f"Verfügbare Beschwörungen: {guardian_mgr.available_tokens} | Besiege den Wächter für +1 Essenz!"
        sub_surf = self.font_regular.render(sub_msg, True, TEXT_COLOR)
        self.screen.blit(sub_surf, (modal_rect.centerx - sub_surf.get_width() // 2, modal_rect.y + 60))

        card_w, card_h = 235, 145
        start_x = modal_rect.x + 35
        start_y = modal_rect.y + 95

        for i, elem in enumerate(ELEMENT_CIRCLE):
            c_idx = i % 3
            r_idx = i // 3
            cx = start_x + c_idx * (card_w + 20)
            cy = start_y + r_idx * (card_h + 15)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)

            curr_level = guardian_mgr.essences.get(elem, 0)
            color, _ = get_element_color(elem)

            pygame.draw.rect(self.screen, BG_PANEL_ALT, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, color, card_rect, width=2, border_radius=8)

            elem_ico = IconRenderer.get_element_icon(elem, 22)
            self.screen.blit(elem_ico, (card_rect.x + 12, card_rect.y + 10))

            elem_name = ELEMENT_NAMES_DE.get(elem, "")
            header = self.font_bold.render(elem_name, True, color)
            self.screen.blit(header, (card_rect.x + 40, card_rect.y + 11))

            level_str = f"Aktuelle Essenz: Stufe {curr_level}"
            lvl_surf = self.font_small.render(level_str, True, TEXT_MUTED)
            self.screen.blit(lvl_surf, (card_rect.x + 12, card_rect.y + 38))

            btn_rect = pygame.Rect(card_rect.x + 12, card_rect.y + 78, card_w - 24, 40)
            can_act = guardian_mgr.available_tokens > 0

            pygame.draw.rect(self.screen, (35, 55, 35) if can_act else (30, 30, 35), btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (80, 200, 100) if can_act else (60, 60, 70), btn_rect, width=1, border_radius=6)

            sw_ico = IconRenderer.get_icon("swords", 18)
            self.screen.blit(sw_ico, (btn_rect.x + 10, btn_rect.y + 11))

            btn_txt = self.font_bold.render("Herausfordern", True, TEXT_GREEN if can_act else TEXT_MUTED)
            self.screen.blit(btn_txt, (btn_rect.x + 36, btn_rect.y + 10))

            if can_act:
                def make_summon_cb(el: Element):
                    return lambda: on_summon_element(el)
                self.add_clickable(btn_rect, make_summon_cb(elem))

        # Interest Upgrade Option
        int_rect = pygame.Rect(modal_rect.x + 35, modal_rect.bottom - 95, 500, 50)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, int_rect, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD, int_rect, width=1, border_radius=6)

        coin_ico = IconRenderer.get_icon("gold", 22)
        self.screen.blit(coin_ico, (int_rect.x + 14, int_rect.y + 14))

        int_text = self.font_bold.render("Alternative: Zinsrate dauerhaft um +0.5% erhöhen", True, TEXT_GOLD)
        self.screen.blit(int_text, (int_rect.x + 44, int_rect.y + 14))

        if guardian_mgr.available_tokens > 0:
            self.add_clickable(int_rect, on_choose_interest)

        # Close Button
        close_rect = pygame.Rect(modal_rect.right - 180, modal_rect.bottom - 95, 145, 50)
        pygame.draw.rect(self.screen, (60, 25, 25), close_rect, border_radius=6)
        pygame.draw.rect(self.screen, (220, 80, 80), close_rect, width=1, border_radius=6)

        cross_ico = IconRenderer.get_icon("close", 18)
        self.screen.blit(cross_ico, (close_rect.x + 16, close_rect.y + 16))
        close_lbl = self.font_bold.render("Schließen", True, (255, 200, 200))
        self.screen.blit(close_lbl, (close_rect.x + 42, close_rect.y + 14))
        self.add_clickable(close_rect, on_close)

    def draw_element_circle_helper(self, layout: LayoutConfig) -> None:
        """Render the element advantage circle with clean vector icons."""
        bar_y = layout.screen_height - layout.bottom_bar_height - 12
        ox = layout.grid_offset_x

        # Render panel
        total_w = 780
        bg_rect = pygame.Rect(ox, bar_y, total_w, 36)
        pygame.draw.rect(self.screen, BG_PANEL, bg_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, bg_rect, width=1, border_radius=6)

        lbl = self.font_bold.render("Vorteilskreis (200% Schaden):", True, TEXT_GOLD)
        self.screen.blit(lbl, (ox + 12, bar_y + 8))

        curr_x = ox + 12 + lbl.get_width() + 14
        for i, elem in enumerate(ELEMENT_CIRCLE):
            ico = IconRenderer.get_element_icon(elem, 18)
            self.screen.blit(ico, (curr_x, bar_y + 9))
            curr_x += 22

            name_str = ELEMENT_NAMES_DE.get(elem, "")
            name_surf = self.font_bold.render(name_str, True, (220, 230, 245))
            self.screen.blit(name_surf, (curr_x, bar_y + 8))
            curr_x += name_surf.get_width() + 6

            if i < len(ELEMENT_CIRCLE) - 1:
                arr = self.font_bold.render(">", True, TEXT_MUTED)
                self.screen.blit(arr, (curr_x, bar_y + 8))
                curr_x += arr.get_width() + 6
            else:
                arr = self.font_bold.render("> Licht", True, TEXT_MUTED)
                self.screen.blit(arr, (curr_x, bar_y + 8))
