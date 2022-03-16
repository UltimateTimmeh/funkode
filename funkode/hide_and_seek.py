"""Play around with ray casting."""
import numpy as np
import pygame

import funkode.scene
import funkode.raycasting

FRAMERATE = 60
SCREEN_SIZE = (800, 600)
CORNERS = {
    "top_left": np.array([0, 0]),
    "top_right": np.array([SCREEN_SIZE[0], 0]),
    "bottom_left": np.array([0, SCREEN_SIZE[1]]),
    "bottom_right": np.array(SCREEN_SIZE),
}
GAME_OVER_SIZE = 48
SCORE_SIZE = 24

DEGREES = np.pi/180.

RAY_THICKNESS = 1

PLAYER_FOV = 72*DEGREES
PLAYER_NRAYS = 1000
PLAYER_COLOR = pygame.Color("blue")
PLAYER_SIZE = 5
PLAYER_VISION_RAYS = False
PLAYER_VISION_POLYGON = True
PLAYER_MOVE_VELOCITY = 5
PLAYER_TURN_VELOCITY = 5*DEGREES

ENEMY_COLOR = pygame.Color("red")
ENEMY_SIZE = 5
ENEMY_FOV = 72*DEGREES
ENEMY_NRAYS = 1000
ENEMY_VISION_RAYS = False
ENEMY_VISION_POLYGON = True
ENEMY_MOVE_VELOCITY = 5
ENEMY_TURN_VELOCITY = 5*DEGREES
ENEMY_VISIBLE = False

WALL_COLOR = pygame.Color("white")
WALL_THICKNESS = 3
AMOUNT_OF_WALLS = 5


class Character(funkode.raycasting.RayCaster):
    """A character on the playing field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity = 0.
        self.rotation = 0.
        self.visible = True

    @property
    def heading(self):
        return np.array([np.cos(self.angle), np.sin(self.angle)])

    def update(self, walls):
        # Update the character's angle and position.
        self.angle += self.rotation
        self.position += self.velocity*self.heading
        # Make sure the character doesn't leave the screen.
        self.position[0] = max(self.position[0], 0.)
        self.position[0] = min(self.position[0], SCREEN_SIZE[0])
        self.position[1] = max(self.position[1], 0.)
        self.position[1] = min(self.position[1], SCREEN_SIZE[1])
        super().update(walls)

    def draw(self, screen):
        if self.visible:
            super().draw(screen)


class RaycastingScene(funkode.scene.Scene):
    """The ray casting scene."""

    def __init__(self):
        self.player = Character(
            position=funkode.raycasting.random_point(SCREEN_SIZE),
            angle=np.random.rand()*360*DEGREES,
            field_of_view=PLAYER_FOV,
            number_of_rays=PLAYER_NRAYS,
            color=PLAYER_COLOR,
            size=PLAYER_SIZE,
            ray_thickness=RAY_THICKNESS,
            draw_rays=PLAYER_VISION_RAYS,
            draw_polygon=PLAYER_VISION_POLYGON,
        )
        self.enemy = Character(
            position=funkode.raycasting.random_point(SCREEN_SIZE),
            angle=np.random.rand()*360*DEGREES,
            field_of_view=ENEMY_FOV,
            number_of_rays=ENEMY_NRAYS,
            color=ENEMY_COLOR,
            size=ENEMY_SIZE,
            ray_thickness=RAY_THICKNESS,
            draw_rays=ENEMY_VISION_RAYS,
            draw_polygon=ENEMY_VISION_POLYGON,
        )
        self.walls = []
        self.scene_running = False
        self.score = 0
        self.restart_scene()

    @property
    def enemy_sees_player(self):
        return self.enemy.sees_point(self.player.position)

    @property
    def player_sees_enemy(self):
        return self.player.sees_point(self.enemy.position)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.player.velocity = PLAYER_MOVE_VELOCITY
            if event.key == pygame.K_s:
                self.player.velocity = -PLAYER_MOVE_VELOCITY
            if event.key == pygame.K_a:
                self.player.rotation = -PLAYER_TURN_VELOCITY
            if event.key == pygame.K_d:
                self.player.rotation = PLAYER_TURN_VELOCITY
            if event.key == pygame.K_r:
                self.restart_scene()
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_s]:
                self.player.velocity = 0.
            if event.key in [pygame.K_a, pygame.K_d]:
                self.player.rotation = 0.

    def update(self):
        if not self.scene_running:
            return
        # Update the enemy, including random changes to movement.
        if np.random.rand() < 0.01:
            self.enemy.velocity = ENEMY_MOVE_VELOCITY
        if np.random.rand() < 0.01:
            self.enemy.velocity = -ENEMY_MOVE_VELOCITY
        if np.random.rand() < 0.01:
            self.enemy.velocity = 0.
        if np.random.rand() < 0.01:
            self.enemy.rotation = ENEMY_TURN_VELOCITY
        if np.random.rand() < 0.01:
            self.enemy.rotation = -ENEMY_TURN_VELOCITY
        if np.random.rand() < 0.01:
            self.enemy.rotation = 0.
        self.enemy.update(self.walls)
        # Update the player.
        self.player.update(self.walls)
        # Check for game over.
        if self.player_sees_enemy and self.enemy_sees_player:
            self.stop_scene()
        elif self.player_sees_enemy:
            self.score += 1
            self.stop_scene()
        elif self.enemy_sees_player:
            self.score -= 1
            self.stop_scene()

    def draw(self, screen):
        # Draw the battlefield.
        screen.fill(pygame.Color("black"))
        self.enemy.draw(screen)
        self.player.draw(screen)
        for wall in self.walls:
            wall.draw(screen)
        # Draw the score.
        txt = f"Score: {self.score}"
        txt_pos = (12, SCREEN_SIZE[1]-SCORE_SIZE-12)
        txt_color = pygame.Color("yellow")
        font = pygame.freetype.SysFont("FreeSans", SCORE_SIZE)
        font.render_to(screen, txt_pos, txt, txt_color)
        # Draw a message when the game is over.
        if not self.scene_running:
            if self.player_sees_enemy and self.enemy_sees_player:
                txt = "DRAW!"
            elif self.player_sees_enemy:
                txt = "YOU WON!"
            elif self.enemy_sees_player:
                txt = "YOU LOST!"
            else:
                txt = "EVERYBODY LOSES!"  ## Shouldn't happen, but who knows.
            txt += " Hit R to continue."
            txt_pos = (12, 12)
            txt_color = pygame.Color("yellow")
            font = pygame.freetype.SysFont("FreeSans", GAME_OVER_SIZE)
            font.render_to(screen, txt_pos, txt, txt_color)

    def refresh_walls(self):
        self.walls = []
        for _ in range(AMOUNT_OF_WALLS):
            wall = funkode.raycasting.Wall(
                funkode.raycasting.random_point(SCREEN_SIZE),
                funkode.raycasting.random_point(SCREEN_SIZE),
                WALL_COLOR, WALL_THICKNESS,
            )
            self.walls.append(wall)
        self.walls += [
            funkode.raycasting.Wall(
                CORNERS["top_left"], CORNERS["top_right"],
                WALL_COLOR, WALL_THICKNESS
            ),
            funkode.raycasting.Wall(
                CORNERS["top_right"], CORNERS["bottom_right"],
                WALL_COLOR, WALL_THICKNESS
            ),
            funkode.raycasting.Wall(
                CORNERS["bottom_right"], CORNERS["bottom_left"],
                WALL_COLOR, WALL_THICKNESS
            ),
            funkode.raycasting.Wall(
                CORNERS["bottom_left"], CORNERS["top_left"],
                WALL_COLOR, WALL_THICKNESS
            ),
        ]

    def restart_scene(self):
        if not self.scene_running:
            self.refresh_walls()
            self.player.position = funkode.raycasting.random_point(SCREEN_SIZE)
            self.player.angle = np.random.rand()*360*DEGREES
            self.enemy.position = funkode.raycasting.random_point(SCREEN_SIZE)
            self.enemy.angle = np.random.rand()*360*DEGREES
            self.enemy.visible = ENEMY_VISIBLE
            self.scene_running = True

    def stop_scene(self):
        if self.scene_running:
            self.enemy.visible = True
            self.scene_running = False



def main():
    """Main script execution function."""
    # Initialize some PyGame stuff.
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Hide and Seek")

    # Set up the scene.
    scene = RaycastingScene()
    # Initialize and run the game.
    game = funkode.scene.SceneContext(scene, FRAMERATE)
    game.run(screen)


if __name__ == "__main__":
    main()
