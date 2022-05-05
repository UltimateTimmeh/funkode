"""Cast rays from your mouse into a set of randomly generated walls."""
import numpy as np
import pygame

import funkode.core.random
import funkode.core.scene
import funkode.ray.cast

FRAMERATE = 60
SCREEN_SIZE = (800, 600)
CORNERS = {
    "top_left": np.array([0, 0]),
    "top_right": np.array([SCREEN_SIZE[0], 0]),
    "bottom_left": np.array([0, SCREEN_SIZE[1]]),
    "bottom_right": np.array(SCREEN_SIZE),
}

DEGREES = np.pi/180.

RAYCASTER_FOV = 360*DEGREES
RAYCASTER_NRAYS = 100
RAYCASTER_COLOR = pygame.Color("white")
RAYCASTER_SIZE = 5
RAYCASTER_RAY_THICKNESS = 1
RAYCASTER_RAYS_VISIBLE = True
RAYCASTER_POLYGON_VISIBLE = False

WALL_COLOR = pygame.Color("white")
WALL_THICKNESS = 3
AMOUNT_OF_WALLS = 10


class RaycastingScene(funkode.core.scene.Scene):
    """The ray casting scene."""

    def __init__(self):
        self.raycaster = funkode.ray.cast.RayCaster(
            position=np.array(SCREEN_SIZE)/2,
            angle=0.,
            field_of_view=RAYCASTER_FOV,
            number_of_rays=RAYCASTER_NRAYS,
        )
        self.walls = []
        self.refresh_walls()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.refresh_walls()

    def update(self):
        self.raycaster.position = np.array(pygame.mouse.get_pos())
        self.raycaster.cast_to(self.walls)

    def draw(self, screen):
        screen.fill(pygame.Color("black"))
        self._draw_raycaster(screen)
        self._draw_walls(screen)

    def _draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.line(screen, WALL_COLOR, wall.p1, wall.p2,
                             WALL_THICKNESS)

    def _draw_raycaster(self, screen):
        # Draw the rays and/or visible area polygon.
        if self.raycaster.rays is not None:
            polygon_points = self.raycaster.polygon_points
            if RAYCASTER_POLYGON_VISIBLE and polygon_points is not None:
                surface = pygame.Surface(SCREEN_SIZE)
                surface.set_alpha(75)
                pygame.draw.polygon(surface, RAYCASTER_COLOR, polygon_points)
                screen.blit(surface, (0,0))
            if RAYCASTER_RAYS_VISIBLE:
                for ray in self.raycaster.rays_that_hit:
                    pygame.draw.line(screen, RAYCASTER_COLOR, ray[0], ray[1],
                                     RAYCASTER_RAY_THICKNESS)
        # Draw the ray caster.
        pygame.draw.circle(screen, RAYCASTER_COLOR, self.raycaster.position,
                           RAYCASTER_SIZE)

    def refresh_walls(self):
        self.walls = []
        for _ in range(AMOUNT_OF_WALLS):
            wall = funkode.ray.cast.Wall(
                funkode.core.random.random_point_on_screen(SCREEN_SIZE),
                funkode.core.random.random_point_on_screen(SCREEN_SIZE),
            )
            self.walls.append(wall)
        self.walls += [
            funkode.ray.cast.Wall(CORNERS["top_left"],
                                  CORNERS["top_right"]),
            funkode.ray.cast.Wall(CORNERS["top_right"],
                                  CORNERS["bottom_right"]),
            funkode.ray.cast.Wall(CORNERS["bottom_right"],
                                  CORNERS["bottom_left"]),
            funkode.ray.cast.Wall(CORNERS["bottom_left"],
                                  CORNERS["top_left"]),
        ]


def main():
    """Main script execution function."""
    # Initialize some PyGame stuff.
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Ray Casting")
    # Set up the scene.
    scene = RaycastingScene()
    # Initialize and run the game.
    game = funkode.core.scene.SceneContext(scene, FRAMERATE)
    game.run(screen)


if __name__ == "__main__":
    main()
