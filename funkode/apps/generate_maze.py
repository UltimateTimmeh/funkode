"""Watch mazes grow automatically."""
import pygame

import funkode.maze.depth
import funkode.maze.kruskal
import funkode.maze.prim
import funkode.core.scene

FRAMERATE = 60

MAZE_WIDTH = 31
MAZE_HEIGHT = 21
CELL_WIDTH = 30
CELL_HEIGHT = 30

SCREEN_SIZE = (MAZE_WIDTH*CELL_WIDTH, MAZE_HEIGHT*CELL_HEIGHT)

WALL_COLOR = pygame.Color("black")
FLOOR_COLOR = pygame.Color("white")
WALL_WIDTH = 5
ANIMATE=True


class DrawableMaze(funkode.maze.base.GrowingMaze):
    """A growing maze that can be drawn in PyGame."""

    def draw(self, screen):
        # Draw the cell floor.
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                pos = (x*CELL_WIDTH, y*CELL_WIDTH)
                size = (CELL_WIDTH, CELL_HEIGHT)
                rect = pygame.Rect(pos, size)
                color = FLOOR_COLOR if cell.active else WALL_COLOR
                pygame.draw.rect(screen, color, rect)
        # Draw the cell walls.
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells[x][y]
                if cell is cell.north_wall.cell1 and cell.north_wall.active:
                    start = (x*CELL_WIDTH, y*CELL_HEIGHT)
                    end = (start[0]+CELL_WIDTH, start[1])
                    pygame.draw.line(screen, WALL_COLOR, start, end, WALL_WIDTH)
                if cell is cell.east_wall.cell1 and cell.east_wall.active:
                    start = ((x+1)*CELL_WIDTH, y*CELL_HEIGHT)
                    end = (start[0], start[1]+CELL_HEIGHT)
                    pygame.draw.line(screen, WALL_COLOR, start, end, WALL_WIDTH)
                if cell is cell.south_wall.cell1 and cell.south_wall.active:
                    start = (x*CELL_WIDTH, (y+1)*CELL_HEIGHT)
                    end = (start[0]+CELL_WIDTH, start[1])
                    pygame.draw.line(screen, WALL_COLOR, start, end, WALL_WIDTH)
                if cell is cell.west_wall.cell1 and cell.west_wall.active:
                    start = (x*CELL_WIDTH, y*CELL_HEIGHT)
                    end = (start[0], start[1]+CELL_HEIGHT)
                    pygame.draw.line(screen, WALL_COLOR, start, end, WALL_WIDTH)


class MazeGeneratorScene(funkode.core.scene.Scene):
    """A maze generator scene."""

    def __init__(self, maze_class, animate=ANIMATE):
        self.maze_class = maze_class
        self.animate = animate
        self.maze = None
        self.drawn_maze = None
        self.restart_scene()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart_scene()
            if event.key == pygame.K_s:
                self.skip_animation()
            if event.key == pygame.K_t:
                self.toggle_animation()
            if event.key == pygame.K_RIGHT:
                self.transition_to_next_scene()
            if event.key == pygame.K_LEFT:
                self.transition_to_previous_scene()

    def update(self):
        self.drawn_maze.update()

    def draw(self, screen):
        self.drawn_maze.draw(screen)

    def restart_scene(self):
        self.maze = self.maze_class(MAZE_WIDTH, MAZE_HEIGHT)
        self.drawn_maze = DrawableMaze(MAZE_WIDTH, MAZE_HEIGHT, self.maze.steps)
        if not self.animate:
            self.drawn_maze.mature()

    def skip_animation(self):
        self.drawn_maze.mature()

    def toggle_animation(self):
        self.animate = not self.animate
        if not self.animate:
            self.drawn_maze.mature()

    def transition_to_next_scene(self):
        pass

    def transition_to_previous_scene(self):
        pass


class DepthMazeScene(MazeGeneratorScene):
    """The Depth Maze Scene."""

    def __init__(self, animate=ANIMATE):
        super().__init__(funkode.maze.depth.DepthMaze, animate)

    def transition_to_previous_scene(self):
        scene = AdvancedPrimMazeScene(self.animate)
        self.context.transition_to(scene)

    def transition_to_next_scene(self):
        scene = KruskalMazeScene(self.animate)
        self.context.transition_to(scene)


class KruskalMazeScene(MazeGeneratorScene):
    """The Kruskal Maze Scene."""

    def __init__(self, animate=ANIMATE):
        super().__init__(funkode.maze.kruskal.KruskalMaze, animate)

    def transition_to_previous_scene(self):
        scene = DepthMazeScene(self.animate)
        self.context.transition_to(scene)

    def transition_to_next_scene(self):
        scene = PrimMazeScene(self.animate)
        self.context.transition_to(scene)


class PrimMazeScene(MazeGeneratorScene):
    """The Prim Maze Scene."""

    def __init__(self, animate=ANIMATE):
        super().__init__(funkode.maze.prim.PrimMaze, animate)

    def transition_to_previous_scene(self):
        scene = KruskalMazeScene(self.animate)
        self.context.transition_to(scene)

    def transition_to_next_scene(self):
        scene = AdvancedDepthMazeScene(self.animate)
        self.context.transition_to(scene)


class AdvancedDepthMazeScene(MazeGeneratorScene):
    """The Advanced Depth Maze Scene."""

    def __init__(self, animate=ANIMATE):
        super().__init__(funkode.maze.depth.AdvancedDepthMaze, animate)

    def transition_to_previous_scene(self):
        scene = PrimMazeScene(self.animate)
        self.context.transition_to(scene)

    def transition_to_next_scene(self):
        scene = AdvancedKruskalMazeScene(self.animate)
        self.context.transition_to(scene)


class AdvancedKruskalMazeScene(MazeGeneratorScene):
    """The Advanced Kruskal Maze Scene."""

    def __init__(self, animate=ANIMATE):
        super().__init__(funkode.maze.kruskal.AdvancedKruskalMaze, animate)

    def transition_to_previous_scene(self):
        scene = AdvancedDepthMazeScene(self.animate)
        self.context.transition_to(scene)

    def transition_to_next_scene(self):
        scene = AdvancedPrimMazeScene(self.animate)
        self.context.transition_to(scene)


class AdvancedPrimMazeScene(MazeGeneratorScene):
    """The Advanced Prim Maze Scene."""

    def __init__(self, animate=ANIMATE):
        super().__init__(funkode.maze.prim.AdvancedPrimMaze, animate)

    def transition_to_previous_scene(self):
        scene = AdvancedKruskalMazeScene(self.animate)
        self.context.transition_to(scene)

    def transition_to_next_scene(self):
        scene = DepthMazeScene(self.animate)
        self.context.transition_to(scene)


def main():
    """Main script execution function."""
    # Initialize some PyGame stuff.
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Maze Generator")

    # Set up the scene.
    scene = DepthMazeScene()
    # Initialize and run the game.
    game = funkode.core.scene.SceneContext(scene, FRAMERATE)
    game.run(screen)


if __name__ == "__main__":
    main()
