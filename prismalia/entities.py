"""Entities present in the world (player, companion animal, world objects)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import pygame

from .assets import Animation, AssetManager
from .constants import (
    ANIMAL_COLLISION_RADIUS,
    ANIMAL_SPEED,
    GRID_TILE_SIZE,
    PLAYER_COLLISION_RADIUS,
    PLAYER_SPEED,
)
from .constants import ANIMAL_SPEED, GRID_TILE_SIZE, PLAYER_SPEED
from .inventory import Inventory
from .isoutils import cartesian_to_isometric
from .tilemap import TileMap
from .input import InputState


@dataclass
class EntityState:
    position: pygame.Vector2
    animation: str = "idle"
    facing: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 1))


class Entity:
    """Base class for all moving actors."""

    def __init__(
        self,
        name: str,
        position: Tuple[float, float],
        speed: float,
        collision_radius: float = 0.35,
    ) -> None:
    def __init__(self, name: str, position: Tuple[float, float], speed: float) -> None:
        self.name = name
        self.state = EntityState(position=pygame.Vector2(position))
        self.speed = speed
        self.animations: Dict[str, Animation] = {}
        self.collision_radius = collision_radius


    def add_animation(self, key: str, animation: Animation) -> None:
        self.animations[key] = animation

    def set_animation(self, key: str) -> None:
        if key == self.state.animation:
            return
        self.state.animation = key
        animation = self.animations.get(key)
        if animation:
            animation.reset()

    def update(self, dt: float, *_) -> None:
        animation = self.animations.get(self.state.animation)
        if animation:
            animation.update(dt)

    def draw(self, surface: pygame.Surface, asset_manager: AssetManager, camera_offset: Tuple[float, float]) -> None:
        animation = self.animations.get(self.state.animation)
        if animation:
            sprite = animation.current_surface
        else:
            sprite = asset_manager.load_image(f"entity:{self.name}", GRID_TILE_SIZE)
        iso_x, iso_y = cartesian_to_isometric(self.state.position.x, self.state.position.y)
        draw_x = iso_x + camera_offset[0] - sprite.get_width() // 2
        draw_y = iso_y + camera_offset[1] - sprite.get_height() + GRID_TILE_SIZE[1] // 2
        surface.blit(sprite, (draw_x, draw_y))

    def move_with_collisions(self, tilemap: TileMap, velocity: pygame.Vector2) -> None:
        """Move the entity while respecting non-walkable tiles."""

        if velocity.length_squared() == 0:
            return

        proposed = self.state.position + velocity
        radius = self.collision_radius
        if tilemap.is_walkable_point(proposed.x, proposed.y, radius):
            self.state.position = proposed
            return

        if tilemap.is_walkable_point(proposed.x, self.state.position.y, radius):
            self.state.position.x = proposed.x
        if tilemap.is_walkable_point(self.state.position.x, proposed.y, radius):
            self.state.position.y = proposed.y


class Player(Entity):
    def __init__(self, position: Tuple[float, float]) -> None:
        super().__init__("player", position, PLAYER_SPEED, PLAYER_COLLISION_RADIUS)

class Player(Entity):
    def __init__(self, position: Tuple[float, float]) -> None:
        super().__init__("player", position, PLAYER_SPEED)
        self.inventory = Inventory()
        self.health = 100
        self.energy = 100

    def update(self, dt: float, tilemap: TileMap, input_state: InputState) -> None:  # type: ignore[override]
        move = pygame.Vector2(input_state.move_x, input_state.move_y)
        if move.length_squared() > 0:
            move = move.normalize()
            self.state.facing = move
            self.set_animation("walk")
        else:
            self.set_animation("idle")

        velocity = move * self.speed * dt
        self.move_with_collisions(tilemap, velocity)
        new_position = self.state.position + velocity
        target_tile = pygame.Vector2(int(round(new_position.x)), int(round(new_position.y)))
        if tilemap.is_walkable(int(target_tile.x), int(target_tile.y)):
            self.state.position = new_position

        super().update(dt)


class CompanionAnimal(Entity):
    def __init__(self, position: Tuple[float, float]) -> None:
        super().__init__("animal", position, ANIMAL_SPEED, ANIMAL_COLLISION_RADIUS)
        super().__init__("animal", position, ANIMAL_SPEED)
        self.hunger = 100
        self.task_queue: list[Tuple[str, dict]] = []

    def update(self, dt: float, tilemap: TileMap, target: Player) -> None:  # type: ignore[override]
        direction = target.state.position - self.state.position
        if direction.length_squared() > 0.25:
        if direction.length_squared() > 4:
            direction = direction.normalize()
            self.state.facing = direction
            self.set_animation("walk")
        else:
            direction.update(0, 0)
            self.set_animation("idle")
        velocity = direction * self.speed * dt
        self.move_with_collisions(tilemap, velocity)
        new_position = self.state.position + velocity
        tile = pygame.Vector2(int(round(new_position.x)), int(round(new_position.y)))
        if tilemap.is_walkable(int(tile.x), int(tile.y)):
            self.state.position = new_position

        self.hunger = max(0, self.hunger - dt * 2)
        super().update(dt)

    def enqueue_task(self, name: str, parameters: Optional[dict] = None) -> None:
        self.task_queue.append((name, parameters or {}))

    def consume_food(self, food_type: str) -> None:
        # Placeholder; future iterations will apply different hunger restoration values
        self.hunger = min(100, self.hunger + 25)
