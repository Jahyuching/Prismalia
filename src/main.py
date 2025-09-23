"""Entry point for the Prismalia MVP prototype."""

from __future__ import annotations

import pygame

from .engine.constants import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from .gameplay.world import World
from .storage import save_manager
from .ui.command_menu import CommandMenu
from .ui.hud import HUD
from .ui.main_menu import MainMenu
from .ui.pause_menu import PauseMenu


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Prismalia MVP")
    clock = pygame.time.Clock()

    world: World | None = None
    hud: HUD | None = None
    command_menu: CommandMenu | None = None
    main_menu = MainMenu()
    pause_menu = PauseMenu()
    state: str = "menu"

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if world is not None:
                    try:
                        world.save()
                    except Exception as error:  # pragma: no cover - best effort logging
                        print(f"Échec de la sauvegarde du monde: {error}")
                running = False
                break

            if not running:
                break

            if state == "menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    break
                result = main_menu.handle_event(event)
                if result:
                    action, payload = result
                    if action == "new_world":
                        slot_value = payload.get("slot_name")
                        if isinstance(slot_value, str) and slot_value:
                            slot_name = slot_value
                        elif slot_value is not None:
                            slot_name = str(slot_value)
                        else:
                            continue
                        title_value = payload.get("title")
                        title = title_value if isinstance(title_value, str) else slot_name
                        seed = payload.get("seed")
                        seed_int: int | None
                        if seed is not None:
                            try:
                                seed_int = int(seed)
                            except (TypeError, ValueError):
                                seed_int = None
                        else:
                            seed_int = None
                        world = World(
                            slot_name=slot_name,
                            title=title,
                            seed=seed_int,
                        )
                        world.set_surface_size(screen.get_size())
                        hud = HUD()
                        command_menu = CommandMenu()
                        state = "game"
                    elif action == "load_world":
                        slot = payload.get("slot_name")
                        if not isinstance(slot, str):
                            continue
                        try:
                            world = save_manager.load_world(slot)
                        except (FileNotFoundError, ValueError) as error:
                            print(f"Impossible de charger '{slot}': {error}")
                            main_menu.refresh()
                            continue
                        world.set_surface_size(screen.get_size())
                        hud = HUD()
                        command_menu = CommandMenu()
                        state = "game"
                continue

            if state == "game" and world is not None and command_menu is not None:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = "pause"
                    continue
                if command_menu.handle_event(event, world):
                    continue
                world.handle_event(event)
                continue

            if state == "pause":
                action = pause_menu.handle_event(event)
                if action == "resume":
                    state = "game"
                elif action == "save_quit":
                    if world is not None:
                        try:
                            world.save()
                        except Exception as error:  # pragma: no cover - best effort logging
                            print(f"Échec de la sauvegarde du monde: {error}")
                    world = None
                    hud = None
                    command_menu = None
                    state = "menu"
                    main_menu.refresh()
                    main_menu.selection = 0
                continue

        if not running:
            break

        if state == "menu":
            main_menu.draw(screen)
        elif state == "game" and world is not None and hud is not None and command_menu is not None:
            keys = pygame.key.get_pressed()
            world.update(dt, keys)
            hud.update(dt)

            message = world.consume_message()
            if message:
                hud.set_message(message)

            world.draw(screen)
            hud.draw(screen, world)
            command_menu.draw(screen, world)
        elif state == "pause" and world is not None and hud is not None and command_menu is not None:
            hud.update(dt)
            world.draw(screen)
            hud.draw(screen, world)
            command_menu.draw(screen, world)
            pause_menu.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
