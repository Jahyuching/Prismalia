"""Definition of the world tile map and helper queries."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import pygame

from .constants import TILE_HEIGHT, TILE_WIDTH
from .isometric import grid_to_screen
from .sprites import make_resource_surface, make_tile_surface


@dataclass
class Tile:
    terrain: str
    walkable: bool = True
    resource: Optional[str] = None
    block: Optional[str] = None


RESOURCE_TERRAIN = {
    "tree": "grass",
    "rock": "rock",
    "bush": "grass",
}


class TileMap:
    """Simple grid storing terrain information and optional resources."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = [
            [Tile("grass", True, None) for _ in range(width)] for _ in range(height)
        ]

    def generate(self, seed: int | None = None) -> None:
        if seed is None:
            seed = random.randrange(0, 2**31)

        rng = random.Random(seed)
        base_dimension = max(1, max(self.width, self.height))
        height_scale = max(8.0, base_dimension * 0.7)
        moisture_scale = max(6.0, base_dimension * 0.55)
        height_seed = seed * 977 + 101
        moisture_seed = seed * 1373 + 421

        for y in range(self.height):
            for x in range(self.width):
                height_val = self._fractal_noise_2d(
                    x,
                    y,
                    scale=height_scale,
                    seed=height_seed,
                    octaves=5,
                    persistence=0.5,
                    lacunarity=2.0,
                )
                moisture_val = self._fractal_noise_2d(
                    x,
                    y,
                    scale=moisture_scale,
                    seed=moisture_seed,
                    octaves=4,
                    persistence=0.6,
                    lacunarity=2.1,
                )
                terrain, walkable = self._terrain_from_values(height_val, moisture_val)
                resource = self._maybe_spawn_resource(
                    rng, terrain, height_val, moisture_val
                )
                self.tiles[y][x] = Tile(
                    terrain=terrain,
                    walkable=walkable,
                    resource=resource,
                )

    def _maybe_spawn_resource(
        self,
        rng: random.Random,
        terrain: str,
        height: float,
        moisture: float,
    ) -> Optional[str]:
        if terrain == "grass":
            if moisture > 0.6 and rng.random() < 0.05 + 0.25 * moisture:
                return "tree"
            if moisture > 0.45 and rng.random() < 0.08 + 0.12 * moisture:
                return "bush"
        elif terrain == "dirt":
            if moisture > 0.65 and rng.random() < 0.04 + 0.1 * (moisture - 0.65):
                return "tree"
            if 0.45 < moisture < 0.7 and rng.random() < 0.06:
                return "bush"
        elif terrain == "rock":
            rock_chance = 0.08 + max(0.0, height - 0.75) * 0.3
            if rng.random() < min(0.25, rock_chance):
                return "rock"
        return None

    @staticmethod
    def _fade(t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    @staticmethod
    def _pseudo_random(x: int, y: int, seed: int) -> float:
        n = x * 374761393 + y * 668265263 + seed * 1446648777
        n = (n ^ (n >> 13)) * 1274126177
        n = n ^ (n >> 16)
        n &= 0xFFFFFFFF
        return n / 0xFFFFFFFF

    @classmethod
    def _value_noise(cls, x: float, y: float, seed: int) -> float:
        xi = math.floor(x)
        yi = math.floor(y)
        xf = x - xi
        yf = y - yi

        top_left = cls._pseudo_random(xi, yi, seed)
        top_right = cls._pseudo_random(xi + 1, yi, seed)
        bottom_left = cls._pseudo_random(xi, yi + 1, seed)
        bottom_right = cls._pseudo_random(xi + 1, yi + 1, seed)

        u = cls._fade(xf)
        v = cls._fade(yf)

        top = cls._lerp(top_left, top_right, u)
        bottom = cls._lerp(bottom_left, bottom_right, u)
        return cls._lerp(top, bottom, v)

    @classmethod
    def _fractal_noise_2d(
        cls,
        x: float,
        y: float,
        *,
        scale: float,
        seed: int,
        octaves: int,
        persistence: float,
        lacunarity: float,
    ) -> float:
        if scale <= 0:
            raise ValueError("scale must be positive")

        amplitude = 1.0
        frequency = 1.0 / scale
        total = 0.0
        max_amplitude = 0.0

        for octave in range(octaves):
            sample_x = x * frequency
            sample_y = y * frequency
            total += cls._value_noise(sample_x, sample_y, seed + octave * 1013) * amplitude
            max_amplitude += amplitude
            amplitude *= persistence
            frequency *= lacunarity

        if max_amplitude == 0:
            return 0.0
        value = total / max_amplitude
        return max(0.0, min(1.0, value))

    @staticmethod
    def _terrain_from_values(height: float, moisture: float) -> Tuple[str, bool]:
        water_level = 0.32
        beach_level = 0.37
        hill_level = 0.68
        mountain_level = 0.82

        if height < water_level:
            return "water", False
        if height < beach_level:
            return "sand", True
        if height < hill_level:
            terrain = "grass" if moisture >= 0.45 else "dirt"
            return terrain, True
        if height < mountain_level:
            terrain = "dirt" if moisture >= 0.5 else "rock"
            return terrain, True
        return "rock", True

    def get(self, x: int, y: int) -> Tile:
        return self.tiles[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        tile = self.tiles[y][x]
        if tile.block in {"wood_block", "stone_block", "campfire"}:
            return False
        return tile.walkable

    def screen_draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        offset_x, offset_y = camera_offset
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                sprite = make_tile_surface(tile.block or tile.terrain)
                draw_x, draw_y = grid_to_screen(x, y, offset_x, offset_y)
                draw_x -= TILE_WIDTH // 2
                draw_y -= TILE_HEIGHT // 2
                surface.blit(sprite, (draw_x, draw_y))
                if tile.resource:
                    resource_sprite = make_resource_surface(tile.resource)
                    res_rect = resource_sprite.get_rect()
                    res_rect.midbottom = (draw_x + TILE_WIDTH // 2, draw_y + TILE_HEIGHT)
                    surface.blit(resource_sprite, res_rect)



                    res_x = draw_x
                    res_y = draw_y - TILE_HEIGHT // 2
                    surface.blit(resource_sprite, (res_x, res_y))

    def iter_tiles(self) -> Iterable[Tuple[int, int, Tile]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self.tiles[y][x]

    def remove_resource(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[y][x].resource = None

    def place_block(self, x: int, y: int, block: str) -> bool:
        if not self.in_bounds(x, y):
            return False
        tile = self.tiles[y][x]
        if not tile.walkable:
            return False
        tile.block = block
        tile.resource = None
        return True

    def clear_block(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[y][x].block = None
