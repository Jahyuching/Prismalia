"""Player entity implementation."""

from __future__ import annotations

from typing import Any, Tuple

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
            if tilemap.is_walkable(int(proposed.x), int(proposed.y)):
                self.position.update(proposed)

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": [float(self.position.x), float(self.position.y)],
            "hunger": float(self.hunger),
            "selected_block": self.selected_block,
            "inventory": self.inventory.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Player":
        position_data = data.get("position", (0.0, 0.0))
        if isinstance(position_data, (list, tuple)) and len(position_data) >= 2:
            pos = (float(position_data[0]), float(position_data[1]))
        else:
            pos = (0.0, 0.0)
        player = cls(pos)
        hunger = data.get("hunger")
        if hunger is not None:
            player.hunger = float(hunger)
        selected_block = data.get("selected_block")
        if isinstance(selected_block, str):
            player.selected_block = selected_block
        inventory_data = data.get("inventory")
        if isinstance(inventory_data, dict):
            player.inventory = Inventory.from_dict(inventory_data)
        return player
