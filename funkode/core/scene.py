"""PyGame scenes and their context manager."""
import abc

import pygame

pygame.MOUSE_LEFT = 1
pygame.MOUSE_MIDDLE = 2
pygame.MOUSE_RIGHT = 3
pygame.MOUSE_SCROLLUP = 4
pygame.MOUSE_SCROLLDN = 5


class SceneContext:
    """The scene context class."""

    _scene = None
    """The current scene of the game."""

    def __init__(self, scene, framerate):
        self.framerate = framerate
        self.transition_to(scene)

    def transition_to(self, scene):
        """Transition to another scene."""
        self._scene = scene
        self._scene.context = self

    def run(self, screen):
        """Run the game."""
        # Initialize the frame rate clock.
        clock = pygame.time.Clock()

        # Main game loop.
        while True:
            # Handle events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                self._scene.handle_event(event)
            # Update state.
            self._scene.update()
            # Draw.
            self._scene.draw(screen)
            pygame.display.flip()
            clock.tick(self.framerate)


class Scene(abc.ABC):
    """Abstract base class for a game scene."""

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context

    @abc.abstractmethod
    def handle_event(self, event):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def draw(self, screen):
        pass
