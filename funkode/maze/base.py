"""Base classes for mazes."""
import abc

import numpy as np


class MazeCell:
    """A cell in a maze.

    A maze cell contains references to all its neighbors, allowing for easy
    movement between linked cells.

    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.north_neighbor = None
        self.east_neighbor = None
        self.south_neighbor = None
        self.west_neighbor = None
        self.active = False

    @property
    def is_on_edge(self):
        return len(self.neighbors) < 4

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def neighbors(self):
        neighbors = [
            self.north_neighbor,
            self.east_neighbor,
            self.south_neighbor,
            self.west_neighbor,
        ]
        neighbors = [neighbor for neighbor in neighbors if neighbor is not None]
        return neighbors

    @property
    def active_neighbors(self):
        return [neighbor for neighbor in self.neighbors if neighbor.active]

    @property
    def inactive_neighbors(self):
        return [neighbor for neighbor in self.neighbors if not neighbor.active]

    @property
    def inner_inactive_neighbors(self):
        return [nb for nb in self.inactive_neighbors if not nb.is_on_edge]

    @property
    def shuffled_inner_inactive_neighbors(self):
        neighbors = self.inner_inactive_neighbors
        np.random.shuffle(neighbors)
        return neighbors

    def get_opposite_neighbor(self, neighbor):
        if neighbor not in self.neighbors:
            raise ValueError("Given cell is not a neighbor of this cell.")
        if neighbor is self.north_neighbor:
            opposite_neighbor = self.south_neighbor
        elif neighbor is self.east_neighbor:
            opposite_neighbor = self.west_neighbor
        elif neighbor is self.south_neighbor:
            opposite_neighbor = self.north_neighbor
        else:
            opposite_neighbor = self.east_neighbor
        return opposite_neighbor

    def move_to(self, target_cell):
        if target_cell is None or not target_cell.active:
            target_cell = self
        return target_cell

    def move_north(self):
        return self.move_to(self.north_neighbor)

    def move_east(self):
        return self.move_to(self.east_neighbor)

    def move_south(self):
        return self.move_to(self.south_neighbor)

    def move_west(self):
        return self.move_to(self.west_neighbor)


class AbstractMaze(abc.ABC):
    """Abstract base class for mazes."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = self._new_cells()
        self.steps = []
        self._generate()

    def _new_cells(self):
        # Generate blank cells.
        width, height = self.width, self.height
        cells = [[MazeCell(x, y) for y in range(height)] for x in range(width)]
        # Connect neighboring cells.
        for x in range(width):
            for y in range(height):
                cell = cells[x][y]
                if y > 0:
                    cell.north_neighbor = cells[x][y-1]
                if y < self.height-1:
                    cell.south_neighbor = cells[x][y+1]
                if x > 0:
                    cell.west_neighbor = cells[x-1][y]
                if x < self.width-1:
                    cell.east_neighbor = cells[x+1][y]
        return cells

    def _generate(self):
        pass


class GrowingMaze(AbstractMaze):
    """A maze that starts blank and grows based on a given list of steps."""

    def __init__(self, width, height, steps):
        super().__init__(width, height)
        self.steps = steps

    def update(self):
        """Update the maze a single step."""
        if not self.steps:
            return
        step_x, step_y = self.steps.pop(0)
        self.cells[step_x][step_y].active = True

    def mature(self):
        """Fully mature the maze by exhausting its list of steps."""
        while self.steps:
            self.update()
