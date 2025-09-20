# Sprite utilities and placeholder generation for Prismalia.
#
# This module centralises image loading, caching and placeholder rendering for
# the prototype. It keeps the runtime free from expensive disk reads while
# ensuring that every requested sprite yields a pleasant looking surface even
# when authored art is missing. All surfaces respect the 64×32 tile footprint
# used throughout Prismalia's isometric renderer.
"""Sprite utilities and placeholder generation for Prismalia.

This module centralises image loading, caching and placeholder rendering for the
prototype. It keeps the runtime free from expensive disk reads while ensuring
that every requested sprite yields a pleasant looking surface even when authored
art is missing. All surfaces respect the 64×32 tile footprint used throughout
Prismalia's isometric renderer.
"""Sprite helpers that load authored art when available.

This module centralises the loading, scaling, and simple composition of the
artwork bundled with the prototype. When a requested sprite cannot be found the
functions gracefully fall back to procedural placeholders so the game remains
fully playable. Surfaces are cached so that expensive scaling operations only
run once per unique sprite request.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple


"""Generate simple placeholder sprites for the MVP."""


from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Tuple

from typing import Dict, Tuple


import pygame

from .constants import TILE_HEIGHT, TILE_WIDTH

ASSETS_ROOT = Path(__file__).resolve().parents[2] / "assets"

# Fallback colours roughly matching the theme of the authored art so the
# placeholders blend nicely with the rest of the prototype.
TERRAIN_COLORS: Dict[str, Tuple[int, int, int]] = {
    "grass": (92, 158, 96),
    "dirt": (146, 112, 76),
    "rock": (125, 125, 132),
    "sand": (196, 178, 118),
    "water": (76, 128, 210),
    "wood_block": (150, 96, 60),
    "stone_block": (102, 102, 116),
    "campfire": (222, 128, 48),
}

RESOURCE_COLORS: Dict[str, Tuple[int, int, int]] = {
    "tree": (68, 120, 70),
    "rock": (108, 108, 126),
    "bush": (110, 168, 92),
}

ENTITY_COLORS: Dict[str, Tuple[int, int, int]] = {
    "player": (78, 172, 226),
    "animal": (232, 194, 98),

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


class SpriteCache:
    "Central cache for tile, resource and entity sprites."
    """Central cache for tile, resource and entity sprites."""

    def __init__(self) -> None:
        self._tile_surfaces: Dict[str, pygame.Surface] = {}
        self._resource_surfaces: Dict[str, pygame.Surface] = {}
        self._entity_surfaces: Dict[str, pygame.Surface] = {}

        self._raw_tiles: Dict[str, Optional[pygame.Surface]] = {}
        self._raw_resources: Dict[str, Optional[pygame.Surface]] = {}
        self._raw_entities: Dict[str, Optional[pygame.Surface]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def tile(self, key: str) -> pygame.Surface:
        surface = self._tile_surfaces.get(key)
        if surface is not None:
            return surface

        asset = self._load_tile_asset(key)
        if asset is None:
            surface = self._make_tile_placeholder(key)
        else:
            surface = asset
        self._tile_surfaces[key] = surface
        return surface

    def resource(self, key: str) -> pygame.Surface:
        surface = self._resource_surfaces.get(key)
        if surface is not None:
            return surface

        asset = self._load_resource_asset(key)
        if asset is None:
            base_surface = self._make_resource_placeholder(key)
        else:
            target_size = (int(TILE_WIDTH * 0.9), int(TILE_HEIGHT * 2.2))
            base_surface = self._scale(asset, target_size)
        surface = self._with_shadow(base_surface, shadow_alpha=70)
        self._resource_surfaces[key] = surface
        return surface

    def entity(self, key: str) -> pygame.Surface:
        surface = self._entity_surfaces.get(key)
        if surface is not None:
            return surface

        asset = self._load_entity_asset(key)
        if asset is None:
            base_surface = self._make_entity_placeholder(key)
        else:
            base_surface = asset
        surface = self._with_shadow(base_surface, shadow_alpha=90)
        self._entity_surfaces[key] = surface
        return surface

    # ------------------------------------------------------------------
    # Asset loading helpers
    # ------------------------------------------------------------------
    def _load_tile_asset(self, key: str) -> Optional[pygame.Surface]:
        if key in self._raw_tiles:
            return self._raw_tiles[key]

        tile_path = ASSETS_ROOT / "tiles" / f"{key}.png"
        surface = self._load_image(tile_path)
        if surface is not None:
            surface = self._scale(surface, (TILE_WIDTH, TILE_HEIGHT))
        else:
            object_path = ASSETS_ROOT / "objects" / f"{key}.png"
            surface = self._load_image(object_path)
            if surface is not None:
                surface = self._scale(surface, (TILE_WIDTH, TILE_HEIGHT))
        self._raw_tiles[key] = surface
        return surface

    def _load_resource_asset(self, key: str) -> Optional[pygame.Surface]:
        if key in self._raw_resources:
            return self._raw_resources[key]

        direct_path = ASSETS_ROOT / "objects" / f"{key}.png"
        surface = self._load_image(direct_path)
        if surface is not None:
            self._raw_resources[key] = surface
            return surface

        if key not in RESOURCE_ATLAS_COORDS:
            self._raw_resources[key] = None
            return None

        atlas = self._load_image(RESOURCE_ATLAS)
        if atlas is None:
            self._raw_resources[key] = None
            return None

        cols = 4
        rows = 4
        cell_width = atlas.get_width() // cols
        cell_height = atlas.get_height() // rows
        col, row = RESOURCE_ATLAS_COORDS[key]
        rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
        try:
            surface = atlas.subsurface(rect).copy()
        except ValueError:
            surface = None
        self._raw_resources[key] = surface
        return surface

    def _load_entity_asset(self, key: str) -> Optional[pygame.Surface]:
        if key in self._raw_entities:
            return self._raw_entities[key]

        idle_path = ASSETS_ROOT / key / "idle.png"
        sheet = self._load_image(idle_path)
        if sheet is None:
            self._raw_entities[key] = None
            return None

        width, height = sheet.get_size()
        frame_surface: Optional[pygame.Surface] = None
        for candidate in (height, height // 2, height // 3, width):
            if candidate <= 0 or width % candidate != 0:
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
        surface = self._scale(frame_surface, (target_width, target_height))
        self._raw_entities[key] = surface
        return surface

    # ------------------------------------------------------------------
    # Placeholder helpers
    # ------------------------------------------------------------------
    def _ensure_font(self) -> None:
        if not pygame.font.get_init():
            pygame.font.init()

    def _draw_label(self, surface: pygame.Surface, text: str) -> None:
        self._ensure_font()
        font = pygame.font.Font(None, 14)
        label = font.render(text, True, (20, 20, 20))
        rect = label.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(label, rect)

    def _make_tile_placeholder(self, key: str) -> pygame.Surface:
        base_color = TERRAIN_COLORS.get(key, (200, 200, 200))
        top_highlight = tuple(min(255, int(c * 1.2)) for c in base_color)
        bottom_shadow = tuple(max(0, int(c * 0.6)) for c in base_color)

        surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
        points = [
            (TILE_WIDTH // 2, 0),
            (TILE_WIDTH, TILE_HEIGHT // 2),
            (TILE_WIDTH // 2, TILE_HEIGHT),
            (0, TILE_HEIGHT // 2),
        ]
        pygame.draw.polygon(surface, base_color, points)
        # Add a subtle highlight and shadow for more depth.
        highlight = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(
            highlight,
            top_highlight,
            [points[0], points[1], (TILE_WIDTH // 2, TILE_HEIGHT // 2)],
        )
        shadow = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(
            shadow,
            bottom_shadow,
            [(TILE_WIDTH // 2, TILE_HEIGHT // 2), points[2], points[3]],
        )
        surface.blit(highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(shadow, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.polygon(surface, (20, 20, 20), points, 1)
        return surface

    def _make_resource_placeholder(self, key: str) -> pygame.Surface:
        base_color = RESOURCE_COLORS.get(key, (200, 120, 140))
        highlight = tuple(min(255, int(c * 1.25)) for c in base_color)
        width = int(TILE_WIDTH * 0.9)
        height = int(TILE_HEIGHT * 2.2)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        ellipse_rect = pygame.Rect(0, height // 3, width, height * 2 // 3)
        pygame.draw.ellipse(surface, base_color, ellipse_rect)
        highlight_rect = ellipse_rect.inflate(-width // 3, -height // 3)
        pygame.draw.ellipse(surface, highlight, highlight_rect)
        pygame.draw.ellipse(surface, (0, 0, 0), ellipse_rect, 2)
        self._draw_label(surface, key)
        return surface

    def _make_entity_placeholder(self, key: str) -> pygame.Surface:
        base_color = ENTITY_COLORS.get(key, (188, 188, 188))
        highlight = tuple(min(255, int(c * 1.25)) for c in base_color)
        width = int(TILE_WIDTH * 0.9)
        height = int(TILE_HEIGHT * 3)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        body_rect = pygame.Rect(0, height // 4, width, height * 3 // 4)
        pygame.draw.rect(surface, base_color, body_rect, border_radius=8)
        inset = body_rect.inflate(-width // 5, -height // 5)
        pygame.draw.rect(surface, highlight, inset, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), body_rect, 2, border_radius=8)
        self._draw_label(surface, key)
        return surface

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _load_image(self, path: Path) -> Optional[pygame.Surface]:
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

    def _scale(self, surface: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
        if surface.get_size() == size:
            return surface
        return pygame.transform.smoothscale(surface, size)

    def _with_shadow(self, sprite: pygame.Surface, shadow_alpha: int = 80) -> pygame.Surface:
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


_CACHE = SpriteCache()


def make_tile_surface(key: str) -> pygame.Surface:
    "Return a surface representing a terrain tile."
    """Return a surface representing a terrain tile."""

    return _CACHE.tile(key)


def make_resource_surface(key: str) -> pygame.Surface:
    "Return a surface representing a resource with a baked shadow."
    """Return a surface representing a resource with a baked shadow."""

    return _CACHE.resource(key)


def make_entity_surface(key: str) -> pygame.Surface:
    "Return a surface representing an entity with a stronger shadow."
    """Return a surface representing an entity with a stronger shadow."""

    return _CACHE.entity(key)


__all__ = [
    "make_tile_surface",
    "make_resource_surface",
    "make_entity_surface",
]


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


def _load_tile_asset(key: str) -> Optional[pygame.Surface]:
    cached = _TILE_ASSET_CACHE.get(key)
    if key in _TILE_ASSET_CACHE:
        return cached

    tile_path = ASSETS_ROOT / "tiles" / f"{key}.png"
    surface = _load_image(tile_path)
    if surface is not None:
        scaled = _scale(surface, (TILE_WIDTH, TILE_HEIGHT))
        _TILE_ASSET_CACHE[key] = scaled
        return scaled
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
        scaled = _scale(surface, (TILE_WIDTH, TILE_HEIGHT))
        _TILE_ASSET_CACHE[key] = scaled
        return scaled
    _TILE_ASSET_CACHE[key] = None
    return None


def _load_resource_asset(key: str) -> Optional[pygame.Surface]:
    cached = _RESOURCE_ASSET_CACHE.get(key)
    if key in _RESOURCE_ASSET_CACHE:
        return cached

        return _scale(surface, (TILE_WIDTH, TILE_HEIGHT))
    return None


@lru_cache(maxsize=None)
def _load_resource_asset(key: str) -> Optional[pygame.Surface]:
    # Direct object sprite takes priority if present
    direct_path = ASSETS_ROOT / "objects" / f"{key}.png"
    surface = _load_image(direct_path)
    if surface is not None:
        _RESOURCE_ASSET_CACHE[key] = surface
        return surface

    if key not in RESOURCE_ATLAS_COORDS:
        _RESOURCE_ASSET_CACHE[key] = None
        return surface

    if key not in RESOURCE_ATLAS_COORDS:
        return None

    atlas = _load_image(RESOURCE_ATLAS)
    if atlas is None:
        _RESOURCE_ASSET_CACHE[key] = None

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
        _RESOURCE_ASSET_CACHE[key] = None
        return None
    _RESOURCE_ASSET_CACHE[key] = sub
    return sub


def _load_entity_asset(kind: str) -> Optional[pygame.Surface]:
    cached = _ENTITY_ASSET_CACHE.get(kind)
    if kind in _ENTITY_ASSET_CACHE:
        return cached

    idle_path = ASSETS_ROOT / kind / "idle.png"
    sheet = _load_image(idle_path)
    if sheet is None:
        _ENTITY_ASSET_CACHE[kind] = None
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
    scaled = _scale(frame_surface, (target_width, target_height))
    _ENTITY_ASSET_CACHE[kind] = scaled
    return scaled
    return _scale(frame_surface, (target_width, target_height))


def _draw_placeholder_label(surface: pygame.Surface, text: str) -> None:
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.Font(None, 14)
    label = font.render(text, True, (20, 20, 20))
    rect = label.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(label, rect)


def _generate_tile_placeholder(key: str) -> pygame.Surface:


@lru_cache(maxsize=None)
def make_tile_surface(key: str) -> pygame.Surface:

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


_TILE_ASSET_CACHE: Dict[str, Optional[pygame.Surface]] = {}
_RESOURCE_ASSET_CACHE: Dict[str, Optional[pygame.Surface]] = {}
_ENTITY_ASSET_CACHE: Dict[str, Optional[pygame.Surface]] = {}

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

@lru_cache(maxsize=None)
def make_tile_surface(key: str) -> pygame.Surface:
    surface = _load_tile_asset(key)
    if surface is not None:
        return surface
    return _generate_tile_placeholder(key)


@lru_cache(maxsize=None)
def make_resource_surface(key: str) -> pygame.Surface:
    surface = _load_resource_asset(key)
    if surface is None:
        surface = _generate_resource_placeholder(key)
    else:
        target = (int(TILE_WIDTH * 0.9), int(TILE_HEIGHT * 2.2))
        surface = _scale(surface, target)
    return _with_shadow(surface, shadow_alpha=70)
@lru_cache(maxsize=None)
def make_resource_surface(key: str) -> pygame.Surface:
    color = RESOURCE_COLORS.get(key, (200, 80, 120))
    surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (TILE_WIDTH // 2, TILE_HEIGHT // 2), TILE_HEIGHT // 2)
    pygame.draw.circle(surface, (0, 0, 0), (TILE_WIDTH // 2, TILE_HEIGHT // 2), TILE_HEIGHT // 2, 2)
    return surface


@lru_cache(maxsize=None)
def make_entity_surface(key: str) -> pygame.Surface:
    surface = _load_entity_asset(key)
    if surface is None:
        surface = _generate_entity_placeholder(key)
    return _with_shadow(surface, shadow_alpha=90)
    color = ENTITY_COLORS.get(key, (180, 180, 180))
    width = TILE_WIDTH // 2
    height = int(TILE_HEIGHT * 1.5)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, color, (0, height // 3, width, height // 1.3))
    pygame.draw.ellipse(surface, (0, 0, 0), (0, height // 3, width, height // 1.3), 2)
    return surface
