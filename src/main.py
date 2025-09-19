"""Entry point for the Prismalia MVP prototype."""

from __future__ import annotations

import pygame

from .engine.constants import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from .gameplay.world import World
from .ui.command_menu import CommandMenu
from .ui.hud import HUD


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Prismalia MVP")
    clock = pygame.time.Clock()

    world = World()
    world.set_surface_size(screen.get_size())
    hud = HUD()
    command_menu = CommandMenu()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break
            if command_menu.handle_event(event, world):
                continue
            world.handle_event(event)

        keys = pygame.key.get_pressed()
        world.update(dt, keys)
        hud.update(dt)

        message = world.consume_message()
        if message:
            hud.set_message(message)

        world.draw(screen)
        hud.draw(screen, world)
        command_menu.draw(screen, world)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
