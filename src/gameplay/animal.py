"""Companion animal logic including command execution."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

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

    def _idle_follow(self, player: "Player", tilemap: TileMap, dt: float) -> None:
        target = player.position + pygame.Vector2(-1, 0)
        if (target - self.position).length() > 1.8:
            self.move_towards(target, ANIMAL_MOVE_SPEED, dt)

    def _process_command(self, world: "World", dt: float) -> bool:
        command_type = self.active_command.get("type")  # type: ignore[assignment]
        if command_type == "goto":
            target = pygame.Vector2(self.active_command["target"])  # type: ignore[index]
            distance = self.move_towards(target, ANIMAL_MOVE_SPEED, dt)
            return distance <= 0.1
        if command_type == "take":
            target = pygame.Vector2(self.active_command["target"])  # type: ignore[index]
            distance = self.move_towards(target, ANIMAL_MOVE_SPEED, dt)
            if distance <= 0.2:
                world.harvest_at(int(target.x), int(target.y), recipient="player")
                return True
            return False
        if command_type == "place":
            target = pygame.Vector2(self.active_command["target"])  # type: ignore[index]
            block = str(self.active_command.get("block", "wood_block"))
            distance = self.move_towards(target, ANIMAL_MOVE_SPEED, dt)
            if distance <= 0.2:
                world.place_block(int(target.x), int(target.y), block, actor="animal")
                return True
            return False
        return True

    def enqueue_sequence(self, commands: List[Dict[str, object]]) -> None:
        self.pending_commands.extend(commands)

    def feed(self) -> None:
        self.hunger = min(100.0, self.hunger + ANIMAL_HUNGER_REPLENISH)

    def to_dict(self) -> dict[str, Any]:
        return {
            "position": [float(self.position.x), float(self.position.y)],
            "hunger": float(self.hunger),
            "pending_commands": [
                self._serialise_command(command) for command in self.pending_commands
            ],
            "active_command": self._serialise_command(self.active_command),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Animal":
        position_data = data.get("position", (0.0, 0.0))
        if isinstance(position_data, (list, tuple)) and len(position_data) >= 2:
            pos = (float(position_data[0]), float(position_data[1]))
        else:
            pos = (0.0, 0.0)
        animal = cls(pos)
        hunger = data.get("hunger")
        if hunger is not None:
            animal.hunger = float(hunger)
        pending = data.get("pending_commands", [])
        if isinstance(pending, list):
            animal.pending_commands = [
                cls._deserialise_command(command)
                for command in pending
                if isinstance(command, dict)
            ]
        active = data.get("active_command")
        if isinstance(active, dict):
            animal.active_command = cls._deserialise_command(active)
        else:
            animal.active_command = None
        return animal

    @staticmethod
    def _serialise_command(command: Optional[Dict[str, object]]) -> Optional[Dict[str, object]]:
        if command is None:
            return None
        serialised = dict(command)
        target = serialised.get("target")
        if isinstance(target, pygame.Vector2):
            serialised["target"] = [float(target.x), float(target.y)]
        elif isinstance(target, (list, tuple)) and len(target) >= 2:
            serialised["target"] = [float(target[0]), float(target[1])]
        return serialised

    @staticmethod
    def _deserialise_command(command: Dict[str, object]) -> Dict[str, object]:
        deserialised = dict(command)
        target = deserialised.get("target")
        if isinstance(target, (list, tuple)) and len(target) >= 2:
            deserialised["target"] = (float(target[0]), float(target[1]))
        return deserialised
