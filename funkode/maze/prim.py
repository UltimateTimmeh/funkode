"""Generate random mazes using the Randomized Prim's algorithm."""
import numpy as np

import funkode.maze.base


class PrimMaze(funkode.maze.base.AbstractMaze):
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
        ## Already fulfilled when initializing base class.
        # Step 2: Pick a random cell.
        rng = np.random.default_rng()
        first_x = rng.choice(range(1, self.width-1, 2))
        first_y = rng.choice(range(1, self.height-1, 2))
        first_cell = self.cells[first_x][first_y]
        # Step 3 : Activate that cell.
        self.steps.append(first_cell.position)
        first_cell.active = True
        # Step 4: Add its inner inactive neighbors to a list of "walls".
        walls = first_cell.shuffled_inner_inactive_neighbors
        # Step 5: While there are walls in the list:
        while len(walls) > 0:
            # Step 5.1: Pick a random wall from the list:
            wall = walls[-1]
            # Step 5.2: If only one of the wall's neighbors is active:
            if len(wall.active_neighbors) == 1:
                # Step 5.2.1: Find the neighbor opposite to the wall's active
                # neighbor.
                active_neighbor = wall.active_neighbors[0]
                opposite_neighbor = wall.get_opposite_neighbor(active_neighbor)
                # Step 5.2.2: If that opposite neighbor is not on the edge:
                if not opposite_neighbor.is_on_edge:
                    # Activate the wall and the opposite neighbor.
                    self.steps.append(wall.position)
                    wall.active = True
                    self.steps.append(opposite_neighbor.position)
                    opposite_neighbor.active = True
                    # And add the opposite neighbor's inner inactive neighbors
                    # to the list of walls.
                    walls += opposite_neighbor.shuffled_inner_inactive_neighbors
            # Step 5.3: Remove the inactive cell from the list.
            walls.remove(wall)
