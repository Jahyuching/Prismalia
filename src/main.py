"""Entry point for the Prismalia MVP prototype."""

from __future__ import annotations

from typing import Literal, Optional

import pygame

from .engine.constants import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from .gameplay.world import World, load_world, list_saved_worlds
from .ui.command_menu import CommandMenu
from .ui.hud import HUD
from .ui.main_menu import MainMenu


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Prismalia MVP")
    clock = pygame.time.Clock()

    hud = HUD()
    command_menu = CommandMenu()

    world: Optional[World] = None
    state: Literal["menu", "playing"] = "menu"
    running = True

    def reset_ui_state() -> None:
        command_menu.visible = False
        command_menu.pending = None
        command_menu.sequence.clear()
        command_menu.status_text = ""
        hud.message = ""
        hud.message_timer = 0.0

    def start_world(new_world: World) -> None:
        nonlocal world, state
        world = new_world
        world.set_surface_size(screen.get_size())
        reset_ui_state()
        state = "playing"
        main_menu.close()

    def handle_new_world(seed: int | None) -> None:
        start_world(World.new(seed))

    def handle_load_world(identifier: str) -> None:
        try:
            loaded_world = load_world(identifier)
        except FileNotFoundError:
            main_menu.set_status(f"Sauvegarde '{identifier}' introuvable")
            main_menu.set_saves(list_saved_worlds())
            return
        start_world(loaded_world)

    def handle_quit() -> None:
        nonlocal running
        running = False

    main_menu = MainMenu(
        on_new_world=handle_new_world,
        on_load_world=handle_load_world,
        on_quit=handle_quit,
    )
    main_menu.open(list_saved_worlds())

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if state == "menu":
                if main_menu.handle_event(event):
                    continue
            elif state == "playing":
                assert world is not None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "menu"
                    main_menu.open(list_saved_worlds())
                    continue
                if command_menu.handle_event(event, world):
                    continue
                world.handle_event(event)

        if not running:
            break

        if state == "menu":
            screen.fill((10, 12, 20))
            main_menu.draw(screen)
        elif state == "playing" and world is not None:
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
