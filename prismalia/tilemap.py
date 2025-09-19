"""Tile map generation and rendering."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Set, Tuple
import random
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

import pygame

from .assets import AssetManager
from .constants import GRID_TILE_SIZE
from .isoutils import tile_to_screen


@dataclass
class MapTile:
    """Represents a single tile in the world grid."""

    terrain: str
    resource: Optional[str] = None
    walkable: bool = True


TERRAIN_TO_SPRITE: Dict[str, str] = {
    "grass": "tiles:grass",
    "dirt": "tiles:dirt",
    "rock": "tiles:rock",
    "sand": "tiles:sand",
    "water": "tiles:water",
}


class TileMap:
    """Simple isometric tile map with layered noise generation."""
    """Simple isometric tile map with naive random generation."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles: List[List[MapTile]] = [
            [MapTile("grass") for _ in range(width)] for _ in range(height)
        ]
        self.seed: int = 0

    def generate(self, seed: int | None = None) -> None:
        """Generate a smoother map using layered value noise."""

        self.seed = seed if seed is not None else random.randrange(1, 1_000_000)
        rng = random.Random(self.seed)
        base_size = max(self.width, self.height)
        scale = max(4.0, base_size / 2.5)
        moisture_scale = max(4.0, base_size / 3.5)

        for y in range(self.height):
            for x in range(self.width):
                height_value = self._fractal_noise(
                    x,
                    y,
                    self.seed,
                    octaves=5,
                    persistence=0.55,
                    scale=scale,
                )
                moisture_value = self._fractal_noise(
                    x,
                    y,
                    self.seed + 9_187,
                    octaves=4,
                    persistence=0.6,
                    scale=moisture_scale,
                )
                terrain = self._pick_terrain(x, y, height_value, moisture_value)
                walkable = terrain != "water"
                if terrain == "rock" and height_value > 0.85:
                    walkable = False
                resource = self._choose_resource_for_terrain(terrain, rng)
                self.tiles[y][x] = MapTile(terrain=terrain, resource=resource, walkable=walkable)

    def _pick_terrain(self, x: int, y: int, height_value: float, moisture_value: float) -> str:
        """Decide terrain type based on sampled noise values."""

        edge_distance = min(x, y, self.width - 1 - x, self.height - 1 - y)
        max_distance = max(1.0, min(self.width, self.height) / 2.0)
        edge_factor = edge_distance / max_distance
        # Pull height down near the borders to form natural shore lines
        height_value -= max(0.0, 0.4 - edge_factor) * 0.6

        if height_value < 0.26:
            return "water"
        if height_value < 0.32:
            return "sand"
        if height_value < 0.6:
            return "grass" if moisture_value >= 0.45 else "dirt"
        if height_value < 0.78:
            return "dirt" if moisture_value < 0.35 else "grass"
        if height_value > 0.9 and moisture_value > 0.65:
            return "grass"
        return "rock"


    def generate(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        for y in range(self.height):
            for x in range(self.width):
                roll = rng.random()
                if roll < 0.65:
                    terrain = "grass"
                elif roll < 0.75:
                    terrain = "dirt"
                elif roll < 0.85:
                    terrain = "sand"
                elif roll < 0.95:
                    terrain = "rock"
                else:
                    terrain = "water"
                walkable = terrain != "water"
                resource = self._choose_resource_for_terrain(terrain, rng)
                self.tiles[y][x] = MapTile(terrain=terrain, resource=resource, walkable=walkable)

    def _choose_resource_for_terrain(self, terrain: str, rng: random.Random) -> Optional[str]:
        if terrain == "grass" and rng.random() < 0.1:
            return rng.choice(["grass", "fruit", "root"])
        if terrain == "dirt" and rng.random() < 0.15:
            return rng.choice(["root", "fiber"])
        if terrain == "rock" and rng.random() < 0.2:
            return rng.choice(["stone", "pebble", "crystal"])
        if terrain == "water" and rng.random() < 0.3:
            return "fish"
        if terrain == "sand" and rng.random() < 0.1:
            return "stick"
        return None

    def get(self, x: int, y: int) -> MapTile:
        return self.tiles[y][x]

    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x].walkable
        return False

    def is_walkable_point(self, x: float, y: float, radius: float = 0.35) -> bool:
        """Check whether a circular area centred on ``(x, y)`` intersects obstacles."""

        min_x = math.floor(x - radius)
        max_x = math.floor(x + radius)
        min_y = math.floor(y - radius)
        max_y = math.floor(y + radius)

        for tile_y in range(min_y, max_y + 1):
            for tile_x in range(min_x, max_x + 1):
                if not self.is_walkable(tile_x, tile_y):
                    return False
        return True


    def draw(self, surface: pygame.Surface, asset_manager: AssetManager, camera_offset: Tuple[float, float]) -> None:
        offset_x, offset_y = camera_offset
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                sprite_name = TERRAIN_TO_SPRITE.get(tile.terrain, "tiles:grass")
                sprite = asset_manager.load_image(sprite_name, GRID_TILE_SIZE)
                screen_x, screen_y = tile_to_screen(x, y, offset_x, offset_y)
                draw_x = screen_x - sprite.get_width() // 2
                draw_y = screen_y - GRID_TILE_SIZE[1] // 2
                surface.blit(sprite, (draw_x, draw_y))

    def iter_sorted_coordinates(self) -> Iterator[Tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y

    def find_spawn(self) -> Tuple[int, int]:
        """Return a walkable coordinate close to the map centre."""

        center_x = self.width // 2
        center_y = self.height // 2
        preferred = {"grass", "dirt", "sand"}
        fallback: Optional[Tuple[int, int]] = None

        max_radius = max(self.width, self.height)
        for radius in range(max_radius):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if max(abs(dx), abs(dy)) != radius:
                        continue
                    x = center_x + dx
                    y = center_y + dy
                    if not (0 <= x < self.width and 0 <= y < self.height):
                        continue
                    tile = self.tiles[y][x]
                    if not tile.walkable:
                        continue
                    if tile.terrain in preferred:
                        return x, y
                    if fallback is None:
                        fallback = (x, y)
        return fallback or (center_x, center_y)

    def find_walkable_near(
        self,
        start_x: int,
        start_y: int,
        max_radius: int = 6,
        exclude: Optional[Set[Tuple[int, int]]] = None,
    ) -> Tuple[int, int]:
        """Locate a nearby walkable tile, avoiding excluded coordinates."""

        excluded = exclude or set()
        for radius in range(max_radius + 1):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if max(abs(dx), abs(dy)) != radius:
                        continue
                    x = start_x + dx
                    y = start_y + dy
                    if (x, y) in excluded:
                        continue
                    if not (0 <= x < self.width and 0 <= y < self.height):
                        continue
                    if self.tiles[y][x].walkable:
                        return x, y
        return start_x, start_y

    def _fractal_noise(
        self,
        x: int,
        y: int,
        seed: int,
        *,
        octaves: int = 4,
        persistence: float = 0.5,
        scale: float = 16.0,
    ) -> float:
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        for _ in range(octaves):
            sample_x = x / max(1e-6, scale) * frequency
            sample_y = y / max(1e-6, scale) * frequency
            total += self._interpolated_noise(sample_x, sample_y, seed) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
        if max_value == 0:
            return 0.5
        normalized = total / max_value
        return max(0.0, min(1.0, normalized * 0.5 + 0.5))

    def _interpolated_noise(self, x: float, y: float, seed: int) -> float:
        integer_x = int(math.floor(x))
        fractional_x = x - integer_x
        integer_y = int(math.floor(y))
        fractional_y = y - integer_y

        v1 = self._smooth_noise(integer_x, integer_y, seed)
        v2 = self._smooth_noise(integer_x + 1, integer_y, seed)
        v3 = self._smooth_noise(integer_x, integer_y + 1, seed)
        v4 = self._smooth_noise(integer_x + 1, integer_y + 1, seed)

        i1 = self._lerp(v1, v2, fractional_x)
        i2 = self._lerp(v3, v4, fractional_x)
        return self._lerp(i1, i2, fractional_y)

    def _smooth_noise(self, x: int, y: int, seed: int) -> float:
        corners = (
            self._base_noise(x - 1, y - 1, seed)
            + self._base_noise(x + 1, y - 1, seed)
            + self._base_noise(x - 1, y + 1, seed)
            + self._base_noise(x + 1, y + 1, seed)
        ) / 16.0
        sides = (
            self._base_noise(x - 1, y, seed)
            + self._base_noise(x + 1, y, seed)
            + self._base_noise(x, y - 1, seed)
            + self._base_noise(x, y + 1, seed)
        ) / 8.0
        center = self._base_noise(x, y, seed) / 4.0
        return corners + sides + center

    def _base_noise(self, x: int, y: int, seed: int) -> float:
        n = x + y * 57 + seed * 131
        n = (n << 13) ^ n
        return 1.0 - ((n * (n * n * 15_731 + 789_221) + 1_376_312_589) & 0x7FFFFFFF) / 1_073_741_824.0

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t
