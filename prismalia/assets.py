"""Asset loading utilities.

This module provides a thin abstraction over pygame's image loading so that the
project can be iterated quickly without having the final art assets. Whenever a
requested asset is missing, a coloured placeholder surface is generated instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pygame

from .constants import COLOR_PLACEHOLDERS, GRID_TILE_SIZE

ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
ASSET_ROOT.mkdir(parents=True, exist_ok=True)


@dataclass
class AnimationFrame:
    """Single frame of an animation."""

    surface: pygame.Surface
    duration: float  # Duration in seconds


class Animation:
    """Simple animation helper cycling through frames sequentially."""

    def __init__(self, frames: Iterable[AnimationFrame]) -> None:
        self.frames: List[AnimationFrame] = list(frames)
        if not self.frames:
            raise ValueError("Animation requires at least one frame")
        self.time = 0.0
        self.index = 0

    def update(self, dt: float) -> None:
        self.time += dt
        current = self.frames[self.index]
        if self.time >= current.duration:
            self.time -= current.duration
            self.index = (self.index + 1) % len(self.frames)

    @property
    def current_surface(self) -> pygame.Surface:
        return self.frames[self.index].surface

    def reset(self) -> None:
        self.time = 0.0
        self.index = 0


class SpriteSheet:
    """Utility for slicing a sprite sheet arranged in a grid."""

    def __init__(self, surface: pygame.Surface, frame_width: int, frame_height: int) -> None:
        self.surface = surface
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.columns = surface.get_width() // frame_width
        self.rows = surface.get_height() // frame_height

    def iter_frames(self) -> Iterable[pygame.Surface]:
        for y in range(self.rows):
            for x in range(self.columns):
                rect = pygame.Rect(x * self.frame_width, y * self.frame_height, self.frame_width, self.frame_height)
                yield self.surface.subsurface(rect).copy()


class AssetManager:
    """Load sprites and sprite sheets from disk with placeholder fallbacks."""

    def __init__(self) -> None:
        self.cache: Dict[str, pygame.Surface] = {}

    def _load_surface(self, path: Path) -> pygame.Surface | None:
        if not path.exists():
            return None
        try:
            return pygame.image.load(path.as_posix()).convert_alpha()
        except pygame.error:
            return None

    def load_image(self, identifier: str, size: Tuple[int, int] | None = None) -> pygame.Surface:
        """Load a static image.

        Args:
            identifier: Logical name of the asset. The system looks for a PNG
                file relative to the assets directory.
            size: Optional size to scale the image to. Defaults to the requested
                size when generating a placeholder.
        """

        if identifier in self.cache:
            return self._ensure_size(self.cache[identifier], size)

        filename = identifier.replace(":", "/") + ".png"
        surface = self._load_surface(ASSET_ROOT / filename)
        if surface is None:
            surface = self._generate_placeholder(identifier, size)
        self.cache[identifier] = surface
        return self._ensure_size(surface, size)

    def load_animation(self, identifier: str, frame_size: Tuple[int, int], frame_duration: float = 0.15) -> Animation:
        """Load an animation from a sprite sheet.

        The sprite sheet is expected to be a single row of equally sized frames.
        """

        filename = identifier.replace(":", "/") + ".png"
        surface = self._load_surface(ASSET_ROOT / filename)
        if surface is None:
            placeholder = self._generate_placeholder(identifier, frame_size)
            frame = AnimationFrame(placeholder, frame_duration)
            return Animation([frame])

        sheet = SpriteSheet(surface, frame_size[0], frame_size[1])
        frames = [AnimationFrame(frame, frame_duration) for frame in sheet.iter_frames()]
        if not frames:
            frames = [AnimationFrame(self._generate_placeholder(identifier, frame_size), frame_duration)]
        return Animation(frames)

    def _generate_placeholder(self, identifier: str, size: Tuple[int, int] | None) -> pygame.Surface:
        target_size = size or GRID_TILE_SIZE
        surface = pygame.Surface(target_size, pygame.SRCALPHA)
        base_color = self._select_color(identifier)
        surface.fill((*base_color, 255))
        pygame.draw.rect(surface, (0, 0, 0, 80), surface.get_rect(), 1)
        self._draw_label(surface, identifier)
        if pygame.display.get_init():
            try:
                return surface.convert_alpha()
            except pygame.error:
                pass
        return surface

    def _ensure_size(self, surface: pygame.Surface, size: Tuple[int, int] | None) -> pygame.Surface:
        if size is None or surface.get_size() == size:
            return surface
        return pygame.transform.smoothscale(surface, size)

    def _select_color(self, identifier: str) -> Tuple[int, int, int]:
        key = identifier.split(":")[-1]
        return COLOR_PLACEHOLDERS.get(key, (180, 180, 180))

    def _draw_label(self, surface: pygame.Surface, identifier: str) -> None:
        font = pygame.font.Font(None, 14)
        text = font.render(identifier.split(":")[-1], True, (20, 20, 20))
        rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(text, rect)
