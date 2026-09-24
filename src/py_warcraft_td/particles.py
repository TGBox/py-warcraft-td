"""Particle system for elemental impacts, explosions, and floating combat text."""

import math
import random
from typing import List, Tuple
import pygame


class Particle:
    """A single visual particle."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        radius: float,
        lifetime: float,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.lifetime = lifetime
        self.age = 0.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        # Drag / friction
        self.vx *= 0.94
        self.vy *= 0.94


class FloatingText:
    """Floating combat text showing damage numbers, gold, or status effects."""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        lifetime: float = 0.85,
        vy: float = -35.0,
        font_size: int = 14,
    ):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.vy = vy
        self.font_size = font_size
        self.age = 0.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        self.age += dt


class VisualEffectsManager:
    """Manages all active particles and floating combat text."""

    def __init__(self):
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []
        self._fonts: dict[int, pygame.font.Font] = {}

    def _get_font(self, size: int) -> pygame.font.Font:
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("Arial", size, bold=True)
        return self._fonts[size]

    def add_sparks(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 8,
        speed: float = 80.0,
        radius: float = 3.0,
    ) -> None:
        """Spawn a radial burst of elemental sparks."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.4, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lifetime = random.uniform(0.2, 0.45)
            self.particles.append(Particle(x, y, vx, vy, color, radius, lifetime))

    def add_explosion(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        radius_px: float = 40.0,
    ) -> None:
        """Spawn an expanding shockwave and sparks."""
        count = int(radius_px / 3.0)
        self.add_sparks(x, y, color, count=count, speed=radius_px * 2.5, radius=4.0)
        # Add high-contrast white core sparks
        self.add_sparks(x, y, (255, 255, 255), count=6, speed=radius_px * 1.5, radius=2.5)

    def add_floating_text(
        self,
        text: str,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        size: int = 14,
        lifetime: float = 0.85,
    ) -> None:
        """Add floating text above a creep."""
        # Slight random horizontal jitter so overlapping numbers don't hide each other
        jitter_x = random.uniform(-6.0, 6.0)
        self.floating_texts.append(
            FloatingText(text, x + jitter_x, y - 8.0, color, lifetime=lifetime, font_size=size)
        )

    def update(self, dt: float) -> None:
        """Update particle and floating text lifetimes and motion."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.is_alive]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw particles and floating texts onto the surface."""
        # Draw particles
        for p in self.particles:
            prog = p.age / p.lifetime
            curr_r = max(1.0, p.radius * (1.0 - prog * 0.5))
            alpha = max(0, int(255 * (1.0 - prog)))

            # If alpha is needed, draw circle
            pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), int(curr_r))

        # Draw floating texts
        for ft in self.floating_texts:
            prog = ft.age / ft.lifetime
            alpha = max(0, int(255 * (1.0 - prog * 0.7)))
            font = self._get_font(ft.font_size)

            # Render text with a subtle dark outline for readability
            text_surf = font.render(ft.text, True, ft.color)
            shadow_surf = font.render(ft.text, True, (10, 12, 16))

            tx = int(ft.x - text_surf.get_width() / 2.0)
            ty = int(ft.y - text_surf.get_height() / 2.0)

            surface.blit(shadow_surf, (tx + 1, ty + 1))
            surface.blit(text_surf, (tx, ty))
