"""Player entity implementation."""

from __future__ import annotations

import math
from typing import Tuple

import pygame

from ..engine.constants import PLAYER_HUNGER_DECAY, PLAYER_HUNGER_REPLENISH, PLAYER_MOVE_SPEED
from ..engine.entities import Entity
from ..engine.tilemap import TileMap

from .inventory import Inventory
from .resources import FOOD_RESOURCES


class Player(Entity):
    def __init__(self, position: Tuple[float, float]) -> None:
        super().__init__("player", position)
        self.inventory = Inventory()
        self.hunger = 100.0
        self.selected_block = "wood_block"

    def update(self, keys: pygame.key.ScancodeWrapper, tilemap: TileMap, dt: float) -> None:
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1

        if move.length_squared() > 0:
            move = move.normalize()
            proposed = self.position + move * PLAYER_MOVE_SPEED * dt
            tile_x = math.floor(proposed.x)
            tile_y = math.floor(proposed.y)
            if tilemap.in_bounds(tile_x, tile_y) and tilemap.is_walkable(tile_x, tile_y):
                self.position.update(proposed)

        epsilon = 1e-3
        max_x = max(0.0, tilemap.width - epsilon)
        max_y = max(0.0, tilemap.height - epsilon)
        self.position.x = min(max(self.position.x, 0.0), max_x)
        self.position.y = min(max(self.position.y, 0.0), max_y)

        # Hunger drains slowly over time
        drain = PLAYER_HUNGER_DECAY / 60.0 * dt
        self.hunger = max(0.0, self.hunger - drain)

    def eat_available_food(self) -> bool:
        for resource in FOOD_RESOURCES:
            if self.inventory.remove(resource, 1):
                self.hunger = min(100.0, self.hunger + PLAYER_HUNGER_REPLENISH)
                return True
        return False

    def cycle_building(self) -> None:
        if self.selected_block == "wood_block":
            self.selected_block = "stone_block"
        elif self.selected_block == "stone_block":
            self.selected_block = "campfire"
        else:
            self.selected_block = "wood_block"
