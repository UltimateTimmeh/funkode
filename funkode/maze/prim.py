"""Generate random mazes using the Randomized Prim's algorithm."""
import numpy as np

from funkode.maze.base import AbstractMaze
from funkode.maze.base import GrowStep
from funkode.maze.base import GrowAction


class PrimMaze(AbstractMaze):
    """A maze generated with the Randomized Prim's algorithm."""

    def __init__(self, width, height):
        if width < 3:
            raise ValueError(f"PrimMaze must be at least 3 wide, got {width}.")
        if height < 3:
            raise ValueError(f"PrimMaze must be at least 3 high, got {height}.")
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
        # Step 1: Start with a grid full of inactive cells.
        ## Fulfilled by initialization of base class.
        ## Make all walls inactive, as they don't matter for this type of maze.
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
        # Step 2: Pick a random cell.
        rng = np.random.default_rng()
        first_x = rng.choice(range(1, self.width-1, 2))
        first_y = rng.choice(range(1, self.height-1, 2))
        first_cell = self.cells[first_x][first_y]
        # Step 3 : Activate that cell.
        action = GrowAction("activate", (first_x, first_y))
        self.steps.append(GrowStep(action))
        first_cell.active = True
        # Step 4: Add its inner inactive neighbors to a list of "walls".
        walls = first_cell.inner_inactive_neighbors
        # Step 5: While there are walls in the list:
        rng = np.random.default_rng()
        while walls:
            # Step 5.1: Pick a random wall from the list:
            wall = rng.choice(walls)
            # Step 5.2: If only one of the wall's neighbors is active:
            if len(wall.active_neighbors) == 1:
                # Step 5.2.1: Find the neighbor opposite to the wall's active
                # neighbor.
                active_neighbor = wall.active_neighbors[0]
                opposite_neighbor = wall.get_opposite_neighbor(active_neighbor)
                # Step 5.2.2: If that opposite neighbor is not on the edge:
                if not opposite_neighbor.is_on_edge:
                    # Activate the wall and the opposite neighbor.
                    actions = [
                        GrowAction("activate", wall.position),
                        GrowAction("activate", opposite_neighbor.position),
                    ]
                    self.steps.append(GrowStep(actions))
                    wall.active = True
                    opposite_neighbor.active = True
                    # And add the opposite neighbor's inner inactive neighbors
                    # to the list of walls.
                    walls += opposite_neighbor.inner_inactive_neighbors
            # Step 5.3: Remove the inactive cell from the list.
            walls.remove(wall)


class AdvancedPrimMaze(AbstractMaze):
    """A more advanced maze generated with the Randomized Prim's algorithm."""

    def _generate(self):
        # Step 1: Start with a grid full of inactive cells.
        ## Fulfilled by initialization of base class.
        # Step 2: Pick a random cell.
        rng = np.random.default_rng()
        first_x = rng.choice(range(self.width))
        first_y = rng.choice(range(self.height))
        first_cell = self.cells[first_x][first_y]
        # Step 3 : Activate that cell.
        action = GrowAction("activate", (first_x, first_y))
        self.steps.append(GrowStep(action))
        first_cell.active = True
        # Step 4: Add its inner active walls to a list of walls.
        walls = first_cell.inner_active_walls
        # Step 5: While there are walls in the list:
        rng = np.random.default_rng()
        while walls:
            # Step 5.1: Pick a random wall from the list:
            wall = rng.choice(walls)
            # Step 5.2: If only one of the cells adjacent to the wall is active:
            if len(wall.active_adjacent_cells) == 1:
                # Step 5.2.1: Activate the other cell and deactivate the wall.
                other_cell = wall.inactive_adjacent_cells[0]
                cell_position = other_cell.position
                wall_position = other_cell.get_wall_position(wall)
                actions = [
                    GrowAction("activate", cell_position),
                    GrowAction("deactivate", cell_position, wall_position),
                ]
                self.steps.append(GrowStep(actions))
                wall.active = False
                other_cell.active = True
                # Step 5.2.2: Add the other cell's inner active walls to the
                # list of walls.
                walls += other_cell.inner_active_walls
            # Step 5.3: Remove the wall from the list.
            walls.remove(wall)
