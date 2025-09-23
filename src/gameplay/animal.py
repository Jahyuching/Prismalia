"""Companion animal logic including command execution."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import pygame

from ..engine.constants import ANIMAL_HUNGER_DECAY, ANIMAL_HUNGER_REPLENISH, ANIMAL_MOVE_SPEED
from ..engine.entities import Entity
from ..engine.tilemap import TileMap

if TYPE_CHECKING:
    from .player import Player
    from .world import World


class Animal(Entity):
    def __init__(self, position: Tuple[float, float]) -> None:
        super().__init__("animal", position)
        self.hunger = 100.0
        self.pending_commands: List[Dict[str, object]] = []
        self.active_command: Optional[Dict[str, object]] = None

    def update(self, world: "World", dt: float) -> None:
        if self.active_command is None and self.pending_commands:
            self.active_command = self.pending_commands.pop(0)

        if self.active_command:
            finished = self._process_command(world, dt)
            if finished:
                self.active_command = None
        else:
            self._idle_follow(world.player, world.tilemap, dt)

        drain = ANIMAL_HUNGER_DECAY / 60.0 * dt
        self.hunger = max(0.0, self.hunger - drain)

    def _move_with_collisions(
        self,
        target: pygame.Vector2,
        tilemap: TileMap,
        speed: float,
        dt: float,
    ) -> float:
        """Move towards *target* while respecting tile collisions."""

        direction = target - self.position
        distance = direction.length()
        if distance < 1e-3:
            if tilemap.is_walkable(math.floor(target.x), math.floor(target.y)):
                self.position.update(target)
            return distance

        direction.scale_to_length(min(distance, speed * dt))
        next_position = self.position + direction

        if tilemap.is_walkable(math.floor(next_position.x), math.floor(next_position.y)):
            self.position.update(next_position)

        return distance

    def _idle_follow(self, player: "Player", tilemap: TileMap, dt: float) -> None:
        target = player.position + pygame.Vector2(-1, 0)
        if (target - self.position).length() > 1.8:
            self._move_with_collisions(target, tilemap, ANIMAL_MOVE_SPEED, dt)

    def _process_command(self, world: "World", dt: float) -> bool:
        command_type = self.active_command.get("type")  # type: ignore[assignment]
        if command_type == "goto":
            target = pygame.Vector2(self.active_command["target"])  # type: ignore[index]
            distance = self._move_with_collisions(target, world.tilemap, ANIMAL_MOVE_SPEED, dt)
            return distance <= 0.1
        if command_type == "take":
            target = pygame.Vector2(self.active_command["target"])  # type: ignore[index]
            distance = self._move_with_collisions(target, world.tilemap, ANIMAL_MOVE_SPEED, dt)
            if distance <= 0.2:
                world.harvest_at(int(target.x), int(target.y), recipient="player")
                return True
            return False
        if command_type == "place":
            target = pygame.Vector2(self.active_command["target"])  # type: ignore[index]
            block = str(self.active_command.get("block", "wood_block"))
            distance = self._move_with_collisions(target, world.tilemap, ANIMAL_MOVE_SPEED, dt)
            if distance <= 0.2:
                world.place_block(int(target.x), int(target.y), block, actor="animal")
                return True
            return False
        return True

    def enqueue_sequence(self, commands: List[Dict[str, object]]) -> None:
        self.pending_commands.extend(commands)

    def feed(self) -> None:
        self.hunger = min(100.0, self.hunger + ANIMAL_HUNGER_REPLENISH)
