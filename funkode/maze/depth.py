"""Generate random mazes using the Randomized Depth First Search algorithm."""
import numpy as np

from funkode.maze.base import AbstractMaze
from funkode.maze.base import GrowStep
from funkode.maze.base import GrowAction


class DepthMaze(AbstractMaze):
    """A maze generated with the Randomized Depth First Search algorithm."""

    def __init__(self, width, height):
        if width < 3:
            raise ValueError(f"DepthMaze must be at least 3 wide, got {width}.")
        if height < 3:
            raise ValueError("DepthMaze must be at least 3 high, "
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
        self.steps.append(GrowStep(actions))
        # # Step 1: Pick a random cell. Activate it and push it to the stack.
        rng = np.random.default_rng()
        first_x = rng.choice(range(1, self.width-1, 2))
        first_y = rng.choice(range(1, self.height-1, 2))
        first_cell = self.cells[first_x][first_y]
        action = GrowAction("activate", (first_x, first_y))
        self.steps.append(GrowStep(action))
        first_cell.active = True
        stack = [first_cell]
        # Step 2: While the stack is not empty:
        while stack:
            # Step 2.1: Pop the last cell from the stack and make it current.
            current_cell = stack.pop()
            # Step 2.2: If the current cell has inactive neighbors:
            inactive_neighbors = []
            for wall in current_cell.neighbors:
                if wall.is_on_edge:
                    continue
                neighbor = wall.get_opposite_neighbor(current_cell)
                if not neighbor.is_on_edge and not neighbor.active:
                    inactive_neighbors.append((neighbor, wall))
            # return
            if inactive_neighbors:
                # Step 2.2.1: Push the current cell to the stack.
                stack.append(current_cell)
                # Step 2.2.2: Choose one of the inactive neighbors.
                neighbor, wall = rng.choice(inactive_neighbors)
                # Step 2.2.3: Activate the chosen inactive neighbor and the wall
                # between it and the current cell.
                actions = [
                    GrowAction("activate", neighbor.position),
                    GrowAction("activate", wall.position),
                ]
                self.steps.append(GrowStep(actions))
                neighbor.active = True
                wall.active = True
                # Step 2.2.4: Push the now active neighbor to the stack.
                stack.append(neighbor)


class AdvancedDepthMaze(AbstractMaze):
    """A more advanced maze generated with the Depth First Search algorithm."""

    def _generate(self):
        # # Step 1: Pick a random cell. Activate it and push it to the stack.
        rng = np.random.default_rng()
        first_x = rng.choice(range(self.width))
        first_y = rng.choice(range(self.height))
        first_cell = self.cells[first_x][first_y]
        action = GrowAction("activate", (first_x, first_y))
        self.steps.append(GrowStep(action))
        first_cell.active = True
        stack = [first_cell]
        # Step 2: While the stack is not empty:
        while stack:
            # Step 2.1: Pop the last cell from the stack and make it current.
            current_cell = stack.pop()
            # Step 2.2: If the current cell has inactive neighbors:
            if current_cell.inactive_neighbors:
                # Step 2.2.1: Push the current cell to the stack.
                stack.append(current_cell)
                # Step 2.2.2: Choose one of the inactive neighbors.
                neighbor = rng.choice(current_cell.inactive_neighbors)
                # Step 2.2.3: Activate the chosen inactive neighbor and
                # deactivate the wall between it and the current cell.
                wall = current_cell.get_wall_between(neighbor)
                cell_position = neighbor.position
                wall_position = neighbor.get_wall_position(wall)
                actions = [
                    GrowAction("activate", cell_position),
                    GrowAction("deactivate", cell_position, wall_position),
                ]
                self.steps.append(GrowStep(actions))
                wall.active = False
                neighbor.active = True
                # Step 2.2.4: Push the now active neighbor to the stack.
                stack.append(neighbor)
