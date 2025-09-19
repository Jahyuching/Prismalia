"""Translate pygame events into high level input commands."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class InputState:
    """High level representation of player input for a single frame."""

    move_x: float = 0.0
    move_y: float = 0.0
    interact: bool = False
    open_inventory: bool = False
    feed_animal: bool = False
    toggle_logic: bool = False


class InputManager:
    """Collect events and update an :class:`InputState` instance."""

    def __init__(self) -> None:
        self.state = InputState()

    def process_events(self) -> InputState:
        self.state = InputState()
        keys = pygame.key.get_pressed()
        # Movement in cartesian grid axes (x -> east, y -> south)
        if keys[pygame.K_w] or keys[pygame.K_z] or keys[pygame.K_UP]:
            self.state.move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.state.move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_q] or keys[pygame.K_LEFT]:

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.state.move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.state.move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:

            self.state.move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.state.move_x += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise SystemExit
                if event.key == pygame.K_e:
                    self.state.interact = True
                if event.key == pygame.K_i:
                    self.state.open_inventory = True
                if event.key == pygame.K_f:
                    self.state.feed_animal = True
                if event.key == pygame.K_l:

                if event.key == pygame.K_q:

                    self.state.toggle_logic = True

        return self.state
