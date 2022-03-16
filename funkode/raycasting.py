"""Play around with ray casting."""
import numpy as np
import pygame
import shapely.geometry

import funkode.scene

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
RAYCASTER_VISION_RAYS = True
RAYCASTER_VISION_POLYGON = False

WALL_COLOR = pygame.Color("white")
WALL_THICKNESS = 3
AMOUNT_OF_WALLS = 10


def random_point():
    """Return a random point on the screen.

    Returns:
        np.array: The 2D coordinates of a random point on the screen.

    """
    return np.round(np.random.rand(2)*SCREEN_SIZE)


class RayCaster:
    """An entity in the scene which emits rays in a certain field of view."""

    def __init__(self, position, angle, field_of_view, number_of_rays, color,
                 size, ray_thickness, draw_rays, draw_polygon):
        self.position = position
        self.angle = angle
        self.field_of_view = field_of_view
        self.number_of_rays = number_of_rays
        self.color = color
        self.size = size
        self.ray_thickness = ray_thickness
        self.draw_rays = draw_rays
        self.draw_polygon = draw_polygon
        self.rays = None

    @property
    def polygon_points(self):
        """Return the points of the ray caster's visible polygon area."""
        points = None
        if self.rays is not None:
            position = self.position.reshape(-1, 2)
            points = self.rays[:, 1]
            points = np.concatenate([position, points, position], axis=0)
        return points

    def update(self, walls):
        self.cast_to(walls)

    def draw(self, screen):
        if self.rays is not None:
            if self.draw_polygon:
                surface = pygame.Surface(SCREEN_SIZE)
                surface.set_alpha(75)
                pygame.draw.polygon(surface, self.color, self.polygon_points)
                screen.blit(surface, (0,0))
            if self.draw_rays:
                for ray in self.rays:
                    pygame.draw.line(screen, self.color, ray[0], ray[1],
                                     self.ray_thickness)
        # Draw the ray caster.
        pygame.draw.circle(screen, self.color, self.position, self.size)

    def cast_to(self, walls):
        """Have the ray caster cast rays to a list of walls."""
        # The array of arc angles.
        arc_start = self.angle - self.field_of_view/2
        arc_stop = self.angle + self.field_of_view/2
        arc = np.linspace(arc_start, arc_stop, self.number_of_rays)
        arc = arc.repeat(len(walls))
        # The array of ray source points.
        number_of_combinations = self.number_of_rays*len(walls)
        p1 = self.position.reshape(-1, 2).astype(float)
        p1 = p1.repeat(number_of_combinations, axis=0)
        x1, y1 = p1.T
        # The array of initial ray target points.
        p2 = p1.copy()
        p2[:, 0] += np.cos(arc)
        p2[:, 1] += np.sin(arc)
        x2, y2 = p2.T
        # The array of first wall points.
        p3 = np.array([wall.p1 for wall in walls])
        p3 = np.tile(p3, (self.number_of_rays, 1))
        x3, y3 = p3.T
        # The array of second wall points.
        p4 = np.array([wall.p2 for wall in walls])
        p4 = np.tile(p4, (self.number_of_rays, 1))
        x4, y4 = p4.T
        # Calculate the line intersection parameters.
        denominator = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        denominator[abs(denominator) < 1e-5] = np.nan
        t_enumerator = (x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)
        u_enumerator = (x1-x3)*(y1-y2) - (y1-y3)*(x1-x2)
        t, u = t_enumerator/denominator, u_enumerator/denominator
        # Adjust ray intersection parameter to exclude invalid intersections.
        # The maximum length a ray could be is the diameter of the screen, so
        # letting the length of invalid intersections to twice this length
        # should make sure they're not selected.
        t[np.isnan(t) | (t<0) | (u<0) | (u>1)] = 2*np.square(SCREEN_SIZE).sum()
        # Update ray target points.
        p2 = p1 + t[:, None]*(p2-p1)
        # For each ray, find the closest valid target point.
        t = t.reshape(self.number_of_rays, -1, 1)
        closest = np.argmin(t, axis=1).flatten()
        closest += np.arange(self.number_of_rays)*len(walls)
        p1 = p1.flatten().reshape(-1, 2)[closest]
        p2 = p2.flatten().reshape(-1, 2)[closest]
        self.rays = np.column_stack((p1, p2))
        self.rays = self.rays.reshape(self.number_of_rays, 2, 2)

    def sees_point(self, point):
        """Return whether the ray caster can see a point."""
        visible = None
        if self.polygon_points is not None:
            polygon = shapely.geometry.Polygon(self.polygon_points)
            visible = polygon.contains(shapely.geometry.Point(point))
        return visible


class Wall:
    """A ray-blocking wall."""

    def __init__(self, p1, p2, color, thickness):
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.thickness = thickness

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.p1, self.p2, self.thickness)


class RaycastingScene(funkode.scene.Scene):
    """The ray casting scene."""

    def __init__(self):
        self.raycaster = RayCaster(
            position=np.array(SCREEN_SIZE)/2,
            angle=0.,
            field_of_view=RAYCASTER_FOV,
            number_of_rays=RAYCASTER_NRAYS,
            color=RAYCASTER_COLOR,
            size=RAYCASTER_SIZE,
            ray_thickness=RAYCASTER_RAY_THICKNESS,
            draw_rays=RAYCASTER_VISION_RAYS,
            draw_polygon=RAYCASTER_VISION_POLYGON,
        )
        self.walls = []
        self.refresh_walls()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.refresh_walls()

    def update(self):
        self.raycaster.position = np.array(pygame.mouse.get_pos())
        self.raycaster.update(self.walls)

    def draw(self, screen):
        screen.fill(pygame.Color("black"))
        self.raycaster.draw(screen)
        for wall in self.walls:
            wall.draw(screen)

    def refresh_walls(self):
        self.walls = []
        for _ in range(AMOUNT_OF_WALLS):
            wall = Wall(random_point(), random_point(),
                        WALL_COLOR, WALL_THICKNESS)
            self.walls.append(wall)
        self.walls += [
            Wall(CORNERS["top_left"], CORNERS["top_right"],
                 WALL_COLOR, WALL_THICKNESS),
            Wall(CORNERS["top_right"], CORNERS["bottom_right"],
                 WALL_COLOR, WALL_THICKNESS),
            Wall(CORNERS["bottom_right"], CORNERS["bottom_left"],
                 WALL_COLOR, WALL_THICKNESS),
            Wall(CORNERS["bottom_left"], CORNERS["top_left"],
                 WALL_COLOR, WALL_THICKNESS),
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
    game = funkode.scene.SceneContext(scene, FRAMERATE)
    game.run(screen)


if __name__ == "__main__":
    main()
