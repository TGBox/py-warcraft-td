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
    CELL_SIZE,
    GRID_COLS,
    GRID_HEIGHT,
    GRID_LINE_COLOR,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    GRID_ROWS,
    GRID_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_HEIGHT,
    SIDEBAR_WIDTH,
    SIDEBAR_X,
    SIDEBAR_Y,
    TEXT_COLOR,
    TEXT_GOLD,
    TEXT_GREEN,
    TEXT_MUTED,
    TEXT_PURPLE,
    TEXT_RED,
)
from py_warcraft_td.creeps import Creep
from py_warcraft_td.elements import (
    ELEMENT_CIRCLE,
    ELEMENT_NAMES_DE,
    ELEMENT_SYMBOLS,
    Element,
    get_element_color,
    get_element_multiplier,
)
from py_warcraft_td.guardians import GuardianManager
from py_warcraft_td.pathfinding import GridCoord, grid_to_pixel
from py_warcraft_td.towers.tower_base import Tower
from py_warcraft_td.towers.tower_catalog import (
    BASE_ELEMENTAL_TOWERS,
    DUAL_TOWERS,
    STARTER_TOWERS,
    TRIPLE_TOWERS,
    TowerDefinition,
    get_available_towers,
    get_tower_def,
)
from py_warcraft_td.waves import WaveConfig


class UIManager:
    """Renders the top HUD, sidebar build panels, modal dialogs, and tooltips."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.SysFont("Segoe UI", 12)
        self.font_regular = pygame.font.SysFont("Segoe UI", 14)
        self.font_bold = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_large = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)

        # Tab navigation for tower sidebar: "starter", "base", "dual", "triple"
        self.active_tab: str = "starter"

        # Scroll offset in tower lists
        self.sidebar_scroll: int = 0

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
        guardian_tokens: int,
        on_speed_toggle: Callable[[], None],
        on_pause_toggle: Callable[[], None],
        on_summon_click: Callable[[], None],
    ) -> None:
        """Render the top resource bar and stats."""
        bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 68)
        pygame.draw.rect(self.screen, BG_PANEL, bar_rect)
        pygame.draw.line(self.screen, BG_PANEL_BORDER, (0, 68), (SCREEN_WIDTH, 68), 2)

        # 1. Gold
        gold_text = self.font_large.render(f"💰 {gold} Gold", True, TEXT_GOLD)
        self.screen.blit(gold_text, (24, 18))

        # 2. Lives
        lives_color = TEXT_GREEN if lives > 20 else (TEXT_GOLD if lives > 10 else TEXT_RED)
        lives_text = self.font_large.render(f"❤️ {lives} Leben", True, lives_color)
        self.screen.blit(lives_text, (180, 18))

        # 3. Wave Indicator
        wave_str = f"Welle {current_wave} / {max_waves}" if current_wave <= max_waves else "Alle Wellen besiegt!"
        wave_text = self.font_large.render(wave_str, True, TEXT_COLOR)
        self.screen.blit(wave_text, (330, 18))

        # 4. Next wave preview
        if next_wave_cfg:
            elem_name = ELEMENT_NAMES_DE.get(next_wave_cfg.armor_element, "Normal")
            fly_str = " (Fliegend 🦅)" if next_wave_cfg.is_flying else ""
            color, _ = get_element_color(next_wave_cfg.armor_element)
            preview_str = f"Nächste: {next_wave_cfg.name} [{elem_name}]{fly_str} x{next_wave_cfg.creep_count}"
            prev_surf = self.font_regular.render(preview_str, True, color)
            self.screen.blit(prev_surf, (330, 44))

        # 5. Interest Timer Bar
        bar_w = 170
        bar_h = 16
        bar_x = 650
        bar_y = 22
        time_left = max(0.0, interest_interval - interest_timer)
        progress = max(0.0, min(1.0, 1.0 - (time_left / interest_interval)))

        # Background bar
        pygame.draw.rect(self.screen, BG_PANEL_ALT, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        # Filled progress
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(self.screen, TEXT_GOLD, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, (bar_x, bar_y, bar_w, bar_h), width=1, border_radius=4)

        interest_yield = int(gold * interest_rate)
        interest_lbl = self.font_small.render(f"Zinsen ({interest_rate*100:.1f}%): +{interest_yield}g ({time_left:.1f}s)", True, TEXT_COLOR)
        self.screen.blit(interest_lbl, (bar_x, bar_y + 20))

        # 6. Guardian Summon Altar Button
        altar_x = 880
        altar_y = 14
        altar_rect = pygame.Rect(altar_x, altar_y, 165, 40)

        if guardian_tokens > 0:
            # Flashing glowing border
            glow_color = (255, 230, 80)
            pygame.draw.rect(self.screen, (60, 45, 10), altar_rect, border_radius=6)
            pygame.draw.rect(self.screen, glow_color, altar_rect, width=2, border_radius=6)
            btn_txt = self.font_bold.render(f"⚔️ Wächter ({guardian_tokens})", True, TEXT_GOLD)
        else:
            pygame.draw.rect(self.screen, BG_PANEL_ALT, altar_rect, border_radius=6)
            pygame.draw.rect(self.screen, BG_PANEL_BORDER, altar_rect, width=1, border_radius=6)
            btn_txt = self.font_regular.render("⚔️ Wächter-Altar", True, TEXT_MUTED)

        self.screen.blit(btn_txt, (altar_rect.x + 14, altar_rect.y + 11))
        self.add_clickable(altar_rect, on_summon_click)

        # 7. Speed and Pause Buttons
        speed_rect = pygame.Rect(1070, 14, 75, 40)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, speed_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, speed_rect, width=1, border_radius=6)
        spd_str = f"⏩ {int(game_speed)}x" if not is_paused else "⏸️ Pause"
        spd_surf = self.font_bold.render(spd_str, True, TEXT_COLOR)
        self.screen.blit(spd_surf, (speed_rect.x + 12, speed_rect.y + 11))
        self.add_clickable(speed_rect, on_speed_toggle)

        pause_rect = pygame.Rect(1155, 14, 80, 40)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, pause_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, pause_rect, width=1, border_radius=6)
        p_str = "▶ Weiter" if is_paused else "⏸ Pause"
        p_surf = self.font_bold.render(p_str, True, TEXT_COLOR)
        self.screen.blit(p_surf, (pause_rect.x + 10, pause_rect.y + 11))
        self.add_clickable(pause_rect, on_pause_toggle)

    def draw_grid_background(
        self,
        spawn_coord: GridCoord,
        goal_coord: GridCoord,
        active_path: Optional[List[GridCoord]],
    ) -> None:
        """Render the tactical grid and paths."""
        # Draw cells
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cell_x = GRID_OFFSET_X + col * CELL_SIZE
                cell_y = GRID_OFFSET_Y + row * CELL_SIZE
                rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)

                bg_color = BG_GRID_A if (row + col) % 2 == 0 else BG_GRID_B
                pygame.draw.rect(self.screen, bg_color, rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, width=1)

        # Highlight Spawn and Goal portals
        sp_px = grid_to_pixel(spawn_coord)
        gl_px = grid_to_pixel(goal_coord)

        # Spawn: Emerald portal
        pygame.draw.circle(self.screen, (40, 180, 80), (int(sp_px[0]), int(sp_px[1])), int(CELL_SIZE / 2.0 - 2))
        sp_label = self.font_small.render("START", True, (255, 255, 255))
        self.screen.blit(sp_label, (int(sp_px[0] - sp_label.get_width() / 2), int(sp_px[1] - sp_label.get_height() / 2)))

        # Goal: Crimson portal
        pygame.draw.circle(self.screen, (220, 60, 60), (int(gl_px[0]), int(gl_px[1])), int(CELL_SIZE / 2.0 - 2))
        gl_label = self.font_small.render("ZIEL", True, (255, 255, 255))
        self.screen.blit(gl_label, (int(gl_px[0] - gl_label.get_width() / 2), int(gl_px[1] - gl_label.get_height() / 2)))

        # Draw dynamic route hint
        if active_path and len(active_path) > 1:
            points = [grid_to_pixel(c) for c in active_path]
            pygame.draw.lines(self.screen, (60, 100, 150), False, points, 2)

    def draw_creeps(self, creeps: List[Creep]) -> None:
        """Render active creeps with elemental colors, health bars, and wings for flying units."""
        for c in creeps:
            if c.is_dead or c.has_leaked:
                continue

            cx, cy = int(c.x), int(c.y)
            color, _ = get_element_color(c.armor_element)

            # Draw body
            pygame.draw.circle(self.screen, color, (cx, cy), int(c.radius))
            pygame.draw.circle(self.screen, (20, 24, 32), (cx, cy), int(c.radius), width=1)

            # Flying indicator (white wings)
            if c.is_flying:
                wing_len = int(c.radius + 5)
                pygame.draw.line(self.screen, (255, 255, 255), (cx - wing_len, cy - 3), (cx + wing_len, cy - 3), 2)

            # Boss golden outline
            if c.modifier == "boss":
                pygame.draw.circle(self.screen, (255, 220, 50), (cx, cy), int(c.radius + 2), width=2)

            # Health bar above creep
            hp_w = max(18, int(c.radius * 2.2))
            hp_h = 4
            hp_x = cx - hp_w // 2
            hp_y = cy - int(c.radius) - 7

            hp_ratio = max(0.0, min(1.0, c.hp / c.max_hp))
            pygame.draw.rect(self.screen, (40, 20, 20), (hp_x, hp_y, hp_w, hp_h))
            bar_color = (60, 220, 90) if hp_ratio > 0.5 else ((240, 200, 50) if hp_ratio > 0.25 else (240, 50, 50))
            pygame.draw.rect(self.screen, bar_color, (hp_x, hp_y, int(hp_w * hp_ratio), hp_h))

    def draw_placement_preview(
        self,
        grid_coord: GridCoord,
        tower_def: TowerDefinition,
        is_valid: bool,
    ) -> None:
        """Render build preview rectangle and attack range circle under cursor."""
        col, row = grid_coord
        cx = GRID_OFFSET_X + col * CELL_SIZE
        cy = GRID_OFFSET_Y + row * CELL_SIZE
        center_x = cx + CELL_SIZE / 2.0
        center_y = cy + CELL_SIZE / 2.0

        color = (80, 230, 100) if is_valid else (240, 60, 60)

        # Range circle
        range_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (*color, 45), (int(center_x), int(center_y)), int(tower_def.range_px))
        pygame.draw.circle(range_surf, (*color, 180), (int(center_x), int(center_y)), int(tower_def.range_px), width=1)
        self.screen.blit(range_surf, (0, 0))

        # Cell box
        pygame.draw.rect(self.screen, color, (cx, cy, CELL_SIZE, CELL_SIZE), width=2)

    def draw_sidebar(
        self,
        gold: int,
        unlocked_elements: Dict[Element, int],
        selected_build_def: Optional[TowerDefinition],
        selected_placed_tower: Optional[Tower],
        on_select_build_def: Callable[[TowerDefinition], None],
        on_upgrade_tower: Callable[[Tower], None],
        on_sell_tower: Callable[[Tower], None],
    ) -> None:
        """Render right sidebar with category tabs, towers list, and inspector card."""
        panel_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        pygame.draw.rect(self.screen, BG_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, panel_rect, width=2, border_radius=8)

        # If a placed tower is selected, show inspector card
        if selected_placed_tower:
            self._draw_tower_inspector(
                panel_rect, selected_placed_tower, gold, unlocked_elements, on_upgrade_tower, on_sell_tower
            )
            return

        # Otherwise show Build Catalog Tabs
        tab_w = (SIDEBAR_WIDTH - 20) // 4
        tab_h = 32
        tabs = [
            ("starter", "Starter"),
            ("base", "Basis"),
            ("dual", "Dual (15)"),
            ("triple", "Triple (20)"),
        ]

        for i, (tab_id, tab_label) in enumerate(tabs):
            tx = panel_rect.x + 10 + i * tab_w
            ty = panel_rect.y + 10
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

        # Render towers belonging to active tab
        content_y = panel_rect.y + 50
        self._draw_tower_list(
            panel_rect, content_y, gold, unlocked_elements, selected_build_def, on_select_build_def
        )

    def _set_tab(self, tab_id: str) -> None:
        self.active_tab = tab_id
        self.sidebar_scroll = 0

    def _draw_tower_list(
        self,
        panel_rect: pygame.Rect,
        start_y: int,
        gold: int,
        unlocked_elements: Dict[Element, int],
        selected_build_def: Optional[TowerDefinition],
        on_select_build_def: Callable[[TowerDefinition], None],
    ) -> None:
        """Render tower cards for current active tab."""
        towers_to_show: List[TowerDefinition] = []
        if self.active_tab == "starter":
            towers_to_show = [t for t in STARTER_TOWERS.values() if t.tier == 1]
        elif self.active_tab == "base":
            towers_to_show = [t for t in BASE_ELEMENTAL_TOWERS.values() if t.tier == 1]
        elif self.active_tab == "dual":
            towers_to_show = list(DUAL_TOWERS.values())
        elif self.active_tab == "triple":
            towers_to_show = list(TRIPLE_TOWERS.values())

        card_h = 52
        card_w = SIDEBAR_WIDTH - 24
        curr_y = start_y

        for tdef in towers_to_show:
            if curr_y + card_h > panel_rect.bottom - 10:
                break

            card_rect = pygame.Rect(panel_rect.x + 12, curr_y, card_w, card_h)

            # Check unlock criteria
            is_unlocked = True
            if tdef.category == "base":
                elem = tdef.elements[0]
                is_unlocked = unlocked_elements.get(elem, 0) >= 1
            elif tdef.category in ("dual", "triple"):
                is_unlocked = all(unlocked_elements.get(e, 0) >= 1 for e in tdef.elements)

            can_afford = gold >= tdef.cost
            is_selected = selected_build_def and selected_build_def.id == tdef.id

            bg_col = (40, 50, 70) if is_selected else (BG_PANEL_ALT if is_unlocked else (20, 24, 30))
            border_col = (255, 230, 80) if is_selected else ((80, 110, 150) if is_unlocked else (45, 50, 60))

            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_col, card_rect, width=1, border_radius=6)

            # Element badge icon
            if tdef.elements:
                elem_icons = " ".join([ELEMENT_SYMBOLS.get(e, "") for e in tdef.elements])
            else:
                elem_icons = "⚪"
            icon_surf = self.font_regular.render(elem_icons, True, TEXT_COLOR)
            self.screen.blit(icon_surf, (card_rect.x + 8, card_rect.y + 6))

            # Name
            name_col = TEXT_COLOR if is_unlocked else TEXT_MUTED
            name_surf = self.font_bold.render(tdef.name, True, name_col)
            self.screen.blit(name_surf, (card_rect.x + 50, card_rect.y + 6))

            # Cost
            cost_col = TEXT_GOLD if can_afford else TEXT_RED
            cost_surf = self.font_bold.render(f"💰 {tdef.cost}g", True, cost_col)
            self.screen.blit(cost_surf, (card_rect.right - cost_surf.get_width() - 8, card_rect.y + 6))

            # Subtitle (Stats & Targets)
            if is_unlocked:
                target_str = "Boden & Luft" if tdef.targets == "both" else ("Nur Luft" if tdef.targets == "air" else "Nur Boden")
                dps = tdef.damage / tdef.attack_cooldown
                stat_str = f"Schaden: {int(tdef.damage)} | DPS: {int(dps)} | {target_str}"
                sub_surf = self.font_small.render(stat_str, True, TEXT_MUTED)
            else:
                req_names = " + ".join([ELEMENT_NAMES_DE.get(e, "") for e in tdef.elements])
                sub_surf = self.font_small.render(f"🔒 Benötigt: {req_names}", True, (200, 100, 100))

            self.screen.blit(sub_surf, (card_rect.x + 50, card_rect.y + 28))

            if is_unlocked:
                def make_select_cb(td: TowerDefinition):
                    return lambda: on_select_build_def(td)
                self.add_clickable(card_rect, make_select_cb(tdef))

            curr_y += card_h + 6

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

        # Header title
        title = self.font_large.render(tdef.name, True, TEXT_GOLD)
        self.screen.blit(title, (panel_rect.x + 16, panel_rect.y + 16))

        # Description
        desc_surf = self.font_regular.render(tdef.description, True, TEXT_COLOR)
        self.screen.blit(desc_surf, (panel_rect.x + 16, panel_rect.y + 50))

        # Stats Table
        stats_y = panel_rect.y + 90
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
            row_y = stats_y + i * 24
            l_surf = self.font_regular.render(label, True, TEXT_MUTED)
            v_surf = self.font_bold.render(val, True, TEXT_COLOR)
            self.screen.blit(l_surf, (panel_rect.x + 16, row_y))
            self.screen.blit(v_surf, (panel_rect.right - v_surf.get_width() - 20, row_y))

        # Upgrade Button
        btn_y = panel_rect.bottom - 70
        if tdef.upgrade_to:
            next_def = get_tower_def(tdef.upgrade_to)
            if next_def:
                can_afford = gold >= next_def.cost
                upg_rect = pygame.Rect(panel_rect.x + 16, btn_y, 185, 45)
                upg_col = BG_PANEL_ALT if can_afford else (30, 20, 20)
                pygame.draw.rect(self.screen, upg_col, upg_rect, border_radius=6)
                pygame.draw.rect(self.screen, TEXT_GOLD if can_afford else (80, 50, 50), upg_rect, width=1, border_radius=6)

                btn_lbl = self.font_bold.render(f"⬆️ Verbessern ({next_def.cost}g)", True, TEXT_GOLD if can_afford else TEXT_MUTED)
                self.screen.blit(btn_lbl, (upg_rect.centerx - btn_lbl.get_width() // 2, upg_rect.centery - btn_lbl.get_height() // 2))

                if can_afford:
                    self.add_clickable(upg_rect, lambda: on_upgrade_tower(tower))

        # Sell Button
        sell_rect = pygame.Rect(panel_rect.right - 180, btn_y, 160, 45)
        pygame.draw.rect(self.screen, (50, 25, 25), sell_rect, border_radius=6)
        pygame.draw.rect(self.screen, (220, 80, 80), sell_rect, width=1, border_radius=6)

        sell_lbl = self.font_bold.render(f"💰 Verkaufen (+{tower.sell_value}g)", True, (255, 120, 120))
        self.screen.blit(sell_lbl, (sell_rect.centerx - sell_lbl.get_width() // 2, sell_rect.centery - sell_lbl.get_height() // 2))
        self.add_clickable(sell_rect, lambda: on_sell_tower(tower))

    def draw_summon_altar_modal(
        self,
        guardian_mgr: GuardianManager,
        wave_num: int,
        on_summon_element: Callable[[Element], None],
        on_choose_interest: Callable[[], None],
        on_close: Callable[[], None],
    ) -> None:
        """Render the Elemental Guardian Summoning Modal."""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Modal Window
        mw, mh = 780, 520
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        modal_rect = pygame.Rect(mx, my, mw, mh)

        pygame.draw.rect(self.screen, BG_PANEL, modal_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 215, 60), modal_rect, width=2, border_radius=12)

        # Title
        title = self.font_title.render("⚡ BESCHWÖRUNGS-ALTAR DER ELEMENTE ⚡", True, TEXT_GOLD)
        self.screen.blit(title, (modal_rect.centerx - title.get_width() // 2, modal_rect.y + 20))

        sub_msg = f"Verfügbare Beschwörungen: {guardian_mgr.available_tokens} | Besiege den Wächter, um das Element freizuschalten!"
        sub_surf = self.font_regular.render(sub_msg, True, TEXT_COLOR)
        self.screen.blit(sub_surf, (modal_rect.centerx - sub_surf.get_width() // 2, modal_rect.y + 60))

        # 6 Element Guardian Cards (2 rows of 3)
        card_w, card_h = 225, 140
        start_x = modal_rect.x + 35
        start_y = modal_rect.y + 95

        for i, elem in enumerate(ELEMENT_CIRCLE):
            col_idx = i % 3
            row_idx = i // 3
            cx = start_x + col_idx * (card_w + 20)
            cy = start_y + row_idx * (card_h + 15)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)

            curr_level = guardian_mgr.essences.get(elem, 0)
            color, _ = get_element_color(elem)

            pygame.draw.rect(self.screen, BG_PANEL_ALT, card_rect, border_radius=8)
            pygame.draw.rect(self.screen, color, card_rect, width=2, border_radius=8)

            # Icon & Name
            elem_name = ELEMENT_NAMES_DE.get(elem, "")
            symbol = ELEMENT_SYMBOLS.get(elem, "")
            header = self.font_bold.render(f"{symbol} {elem_name}", True, color)
            self.screen.blit(header, (card_rect.x + 12, card_rect.y + 10))

            level_str = f"Aktuelle Essenz: Stufe {curr_level}"
            lvl_surf = self.font_small.render(level_str, True, TEXT_MUTED)
            self.screen.blit(lvl_surf, (card_rect.x + 12, card_rect.y + 34))

            # Challenge Button
            btn_rect = pygame.Rect(card_rect.x + 12, card_rect.y + 75, card_w - 24, 38)
            can_act = guardian_mgr.available_tokens > 0

            pygame.draw.rect(self.screen, (35, 55, 35) if can_act else (30, 30, 35), btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (80, 200, 100) if can_act else (60, 60, 70), btn_rect, width=1, border_radius=6)

            btn_txt = self.font_bold.render("⚔️ Herausfordern", True, TEXT_GREEN if can_act else TEXT_MUTED)
            self.screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2, btn_rect.centery - btn_txt.get_height() // 2))

            if can_act:
                def make_summon_cb(el: Element):
                    return lambda: on_summon_element(el)
                self.add_clickable(btn_rect, make_summon_cb(elem))

        # Interest Upgrade Option
        int_rect = pygame.Rect(modal_rect.x + 35, modal_rect.bottom - 95, 480, 48)
        pygame.draw.rect(self.screen, BG_PANEL_ALT, int_rect, border_radius=6)
        pygame.draw.rect(self.screen, TEXT_GOLD, int_rect, width=1, border_radius=6)

        int_text = self.font_bold.render("💰 Alternative: Zinsrate dauerhaft um +0.5% erhöhen", True, TEXT_GOLD)
        self.screen.blit(int_text, (int_rect.x + 18, int_rect.y + 14))

        if guardian_mgr.available_tokens > 0:
            self.add_clickable(int_rect, on_choose_interest)

        # Close Button
        close_rect = pygame.Rect(modal_rect.right - 180, modal_rect.bottom - 95, 145, 48)
        pygame.draw.rect(self.screen, (60, 25, 25), close_rect, border_radius=6)
        pygame.draw.rect(self.screen, (220, 80, 80), close_rect, width=1, border_radius=6)
        close_lbl = self.font_bold.render("Schließen ✕", True, (255, 200, 200))
        self.screen.blit(close_lbl, (close_rect.centerx - close_lbl.get_width() // 2, close_rect.centery - close_lbl.get_height() // 2))
        self.add_clickable(close_rect, on_close)

    def draw_element_circle_helper(self) -> None:
        """Render the element advantage circle at the bottom of the grid."""
        bar_y = SCREEN_HEIGHT - 65
        circle_text = "Vorteilskreis: Licht ✨ > Dunkelheit 🌑 > Wasser 💧 > Feuer 🔥 > Natur 🌿 > Erde ⛰️ > Licht ✨ (200% Schaden)"
        surf = self.font_bold.render(circle_text, True, (220, 230, 245))
        bg_rect = pygame.Rect(GRID_OFFSET_X, bar_y, surf.get_width() + 24, 30)
        pygame.draw.rect(self.screen, BG_PANEL, bg_rect, border_radius=6)
        pygame.draw.rect(self.screen, BG_PANEL_BORDER, bg_rect, width=1, border_radius=6)
        self.screen.blit(surf, (GRID_OFFSET_X + 12, bar_y + 6))
