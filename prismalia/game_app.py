"""Entry point orchestrating the Pygame loop."""

from __future__ import annotations

import pygame

from .assets import AssetManager
from .constants import FPS, WINDOW_HEIGHT, WINDOW_WIDTH, init_fonts
from .devchecks import ensure_no_merge_conflicts
from .input import InputManager
from .world import World


class GameApp:
    """High level application controller."""

    def __init__(self) -> None:
        ensure_no_merge_conflicts()

        pygame.init()
        pygame.display.set_caption("Prismalia Prototype")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        init_fonts()

        self.asset_manager = AssetManager()
        self.input_manager = InputManager()
        self.world = World(self.asset_manager)
        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            try:
                input_state = self.input_manager.process_events()
            except SystemExit:
                self.running = False
                break

            self.world.update(dt, input_state)
            self.world.draw(self.screen)
            pygame.display.flip()

        pygame.quit()


def main() -> None:
    GameApp().run()


if __name__ == "__main__":
    main()
