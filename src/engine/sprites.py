"""Sprite helpers that load authored art when available.

This module centralises the loading, scaling, and simple composition of the
artwork bundled with the prototype. When a requested sprite cannot be found the
functions gracefully fall back to procedural placeholders so the game remains
fully playable. Surfaces are cached so that expensive scaling operations only
run once per unique sprite request.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

from .constants import TILE_HEIGHT, TILE_WIDTH

ASSETS_ROOT = Path(__file__).resolve().parents[2] / "assets"

TERRAIN_COLORS: Dict[str, Tuple[int, int, int]] = {
    "grass": (90, 150, 90),
    "dirt": (130, 100, 70),
    "rock": (110, 110, 110),
    "sand": (190, 170, 110),
    "water": (70, 120, 200),
    "wood_block": (140, 90, 50),
    "stone_block": (90, 90, 100),
    "campfire": (220, 120, 40),
}

RESOURCE_COLORS: Dict[str, Tuple[int, int, int]] = {
    "tree": (60, 100, 60),
    "rock": (90, 90, 110),
    "bush": (100, 150, 80),
}

ENTITY_COLORS: Dict[str, Tuple[int, int, int]] = {
    "player": (70, 160, 220),
    "animal": (230, 190, 90),
}

RESOURCE_ATLAS = ASSETS_ROOT / "objects" / "resources.png"
RESOURCE_ATLAS_COORDS: Dict[str, Tuple[int, int]] = {
    "tree": (0, 0),
    "bush": (1, 0),
    "rock": (1, 1),
}


def _load_image(path: Path) -> Optional[pygame.Surface]:
    if not path.exists():
        return None
    try:
        surface = pygame.image.load(path.as_posix())
    except pygame.error:
        return None
    if pygame.display.get_init():
        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.convert()
    else:
        try:
            surface = surface.convert_alpha()
        except pygame.error:
            pass
    return surface


def _scale(surface: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
    if surface.get_size() == size:
        return surface
    return pygame.transform.smoothscale(surface, size)


@lru_cache(maxsize=None)
def _load_tile_asset(key: str) -> Optional[pygame.Surface]:
    tile_path = ASSETS_ROOT / "tiles" / f"{key}.png"
    surface = _load_image(tile_path)
    if surface is not None:
        return _scale(surface, (TILE_WIDTH, TILE_HEIGHT))
    # Attempt to use an object sprite before falling back to placeholders
    object_path = ASSETS_ROOT / "objects" / f"{key}.png"
    surface = _load_image(object_path)
    if surface is not None:
        return _scale(surface, (TILE_WIDTH, TILE_HEIGHT))
    return None


@lru_cache(maxsize=None)
def _load_resource_asset(key: str) -> Optional[pygame.Surface]:
    # Direct object sprite takes priority if present
    direct_path = ASSETS_ROOT / "objects" / f"{key}.png"
    surface = _load_image(direct_path)
    if surface is not None:
        return surface

    if key not in RESOURCE_ATLAS_COORDS:
        return None

    atlas = _load_image(RESOURCE_ATLAS)
    if atlas is None:
        return None

    cols = 4
    rows = 4
    cell_width = atlas.get_width() // cols
    cell_height = atlas.get_height() // rows
    col, row = RESOURCE_ATLAS_COORDS[key]
    rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
    try:
        sub = atlas.subsurface(rect).copy()
    except ValueError:
        return None
    return sub


@lru_cache(maxsize=None)
def _load_entity_asset(kind: str) -> Optional[pygame.Surface]:
    idle_path = ASSETS_ROOT / kind / "idle.png"
    sheet = _load_image(idle_path)
    if sheet is None:
        return None
    width, height = sheet.get_size()
    # Try to infer a sensible frame width by checking several candidates
    candidates = [height, height // 2, height // 3, width]
    frame_surface = None
    for candidate in candidates:
        if candidate <= 0:
            continue
        if width % candidate != 0:
            continue
        rect = pygame.Rect(0, 0, candidate, height)
        try:
            frame_surface = sheet.subsurface(rect).copy()
        except ValueError:
            frame_surface = None
        if frame_surface is not None:
            break
    if frame_surface is None:
        frame_surface = sheet.copy()
    target_width = int(TILE_WIDTH * 0.9)
    scale_factor = target_width / frame_surface.get_width()
    target_height = max(1, int(frame_surface.get_height() * scale_factor))
    return _scale(frame_surface, (target_width, target_height))


def _draw_placeholder_label(surface: pygame.Surface, text: str) -> None:
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.Font(None, 14)
    label = font.render(text, True, (20, 20, 20))
    rect = label.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(label, rect)


def _generate_tile_placeholder(key: str) -> pygame.Surface:
    color = TERRAIN_COLORS.get(key, (200, 200, 200))
    surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
    points = [
        (TILE_WIDTH // 2, 0),
        (TILE_WIDTH, TILE_HEIGHT // 2),
        (TILE_WIDTH // 2, TILE_HEIGHT),
        (0, TILE_HEIGHT // 2),
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (20, 20, 20), points, 1)
    return surface


def _generate_resource_placeholder(key: str) -> pygame.Surface:
    base_color = RESOURCE_COLORS.get(key, (200, 80, 120))
    width = int(TILE_WIDTH * 0.9)
    height = int(TILE_HEIGHT * 2.1)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, base_color, (0, height // 3, width, height * 2 // 3))
    pygame.draw.ellipse(surface, (0, 0, 0), (0, height // 3, width, height * 2 // 3), 2)
    _draw_placeholder_label(surface, key)
    return surface


def _generate_entity_placeholder(kind: str) -> pygame.Surface:
    base_color = ENTITY_COLORS.get(kind, (180, 180, 180))
    width = int(TILE_WIDTH * 0.9)
    height = int(TILE_HEIGHT * 3)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, base_color, (0, height // 4, width, height * 3 // 4), border_radius=6)
    pygame.draw.rect(surface, (0, 0, 0), (0, height // 4, width, height * 3 // 4), 2, border_radius=6)
    _draw_placeholder_label(surface, kind)
    return surface


def _with_shadow(sprite: pygame.Surface, shadow_alpha: int = 80) -> pygame.Surface:
    shadow_height = max(4, TILE_HEIGHT // 2)
    width = max(sprite.get_width(), int(sprite.get_width() * 1.1))
    height = sprite.get_height() + shadow_height
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    shadow_surface = pygame.Surface((int(sprite.get_width() * 0.9), shadow_height), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect())
    shadow_rect = shadow_surface.get_rect(midbottom=(width // 2, height))
    surface.blit(shadow_surface, shadow_rect)
    sprite_rect = sprite.get_rect(midbottom=(width // 2, height - shadow_height // 4))
    surface.blit(sprite, sprite_rect)
    return surface


_TILE_CACHE: Dict[str, pygame.Surface] = {}
_RESOURCE_CACHE: Dict[str, pygame.Surface] = {}
_ENTITY_CACHE: Dict[str, pygame.Surface] = {}


def make_tile_surface(key: str) -> pygame.Surface:
    """Return a tile sprite, generating a placeholder when no asset exists."""

    cached = _TILE_CACHE.get(key)
    if cached is not None:
        return cached

    asset = _load_tile_asset(key)
    surface = asset if asset is not None else _generate_tile_placeholder(key)
    _TILE_CACHE[key] = surface
    return surface


def make_resource_surface(key: str) -> pygame.Surface:
    """Return a resource sprite with a baked shadow."""

    cached = _RESOURCE_CACHE.get(key)
    if cached is not None:
        return cached

    asset = _load_resource_asset(key)
    if asset is None:
        base_surface = _generate_resource_placeholder(key)
    else:
        target_size = (int(TILE_WIDTH * 0.9), int(TILE_HEIGHT * 2.2))
        base_surface = _scale(asset, target_size)

    final_surface = _with_shadow(base_surface, shadow_alpha=70)
    _RESOURCE_CACHE[key] = final_surface
    return final_surface


def make_entity_surface(key: str) -> pygame.Surface:
    """Return an entity sprite with a stronger shadow."""

    cached = _ENTITY_CACHE.get(key)
    if cached is not None:
        return cached

    asset = _load_entity_asset(key)
    base_surface = asset if asset is not None else _generate_entity_placeholder(key)
    final_surface = _with_shadow(base_surface, shadow_alpha=90)
    _ENTITY_CACHE[key] = final_surface
    return final_surface
