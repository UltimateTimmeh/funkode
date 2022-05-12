"""Generate random mazes using the Randomized Kruskal's algorithm."""
import numpy as np

from funkode.maze.base import AbstractMaze
from funkode.maze.base import GrowStep
from funkode.maze.base import GrowAction


class KruskalMaze(AbstractMaze):
    """A maze generated with the Randomized Kruskal's algorithm."""

    def __init__(self, width, height):
        if width < 3:
            raise ValueError("KruskalMaze must be at least 3 wide, "
                             f"got {width}.")
        if height < 3:
            raise ValueError("KruskalMaze must be at least 3 high, "
                             f"got {height}.")
        super().__init__(width, height)

    def __str__(self):
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += " " if self.cells[x][y].active else "X"
            lines.append(line)
        return "\n".join(lines)

    def _generate(self):
        # Step 0: Make walls inactive, they don't matter for this type of maze.
        actions = []
        for x in range(self.width):
            for y in range(self.height):
                actions += [
                    GrowAction("deactivate", (x, y), "north"),
                    GrowAction("deactivate", (x, y), "east"),
                    GrowAction("deactivate", (x, y), "south"),
                    GrowAction("deactivate", (x, y), "west"),
                ]
                for wall in self.cells[x][y].walls:
                    wall.active = False
        self.steps.append(GrowStep(actions))
        # Step 1a: Create a set for each floor cell containing just that cell.
        floor_cells = []
        for x in range(1, self.width-1, 2):
            for y in range(1, self.height-1, 2):
                floor_cells.append(self.cells[x][y])
        for cell in floor_cells:
            cell.set = [cell]
        # Step 1b: Create a list of all walls.
        walls = []
        for cell in floor_cells:
            walls += cell.inner_inactive_neighbors
        walls = list(set(walls))
        # Step 2: For each wall, in some random order:
        rng = np.random.default_rng()
        rng.shuffle(walls)
        for wall in walls:
            # Step 2.1: If the cells divided by it belong to different sets:
            divided_by_wall = [nb for nb in wall.neighbors if nb in floor_cells]
            if len(divided_by_wall) == 1:
                continue
            cell1, cell2 = divided_by_wall
            if cell1 not in cell2.set:
                # Step 2.1.1: Deactivate the wall and activate those cells.
                actions = [
                    GrowAction("activate", cell1.position),
                    GrowAction("activate", cell2.position),
                    GrowAction("activate", wall.position),
                ]
                self.steps.append(GrowStep(actions))
                cell1.active = True
                cell2.active = True
                wall.active = True
                # Step 2.1.2: Join the sets of the two cells.
                new_set = cell1.set+cell2.set
                for cell in cell1.set:
                    cell.set = new_set
                for cell in cell2.set:
                    cell.set = new_set


class AdvancedKruskalMaze(AbstractMaze):
    """A more advanced maze generated with Kruskal's algorithm."""

    def _generate(self):
        # Step 1a: Create a set for each cell containing just that one cell.
        for x in range(self.width):
            for y in range(self.height):
                self.cells[x][y].set = [self.cells[x][y]]
        # Step 1b: Create a list of all walls.
        walls = self.inner_walls
        # Step 2: For each wall, in some random order:
        rng = np.random.default_rng()
        rng.shuffle(walls)
        for wall in walls:
            # Step 2.1: If the cells divided by it belong to different sets:
            cell1, cell2 = wall.adjacent_cells
            if cell1 not in cell2.set:
                # Step 2.1.1: Deactivate the wall and activate those cells.
                wall_position = cell1.get_wall_position(wall)
                actions = [
                    GrowAction("activate", cell1.position),
                    GrowAction("activate", cell2.position),
                    GrowAction("deactivate", cell1.position, wall_position),
                ]
                self.steps.append(GrowStep(actions))
                cell1.active = True
                cell2.active = True
                wall.active = False
                # Step 2.1.2: Join the sets of the two cells.
                new_set = cell1.set+cell2.set
                for cell in cell1.set:
                    cell.set = new_set
                for cell in cell2.set:
                    cell.set = new_set
