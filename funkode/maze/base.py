"""Base classes for mazes."""


class MazeCell:
    """A cell in a maze.

    A maze cell contains references to all its neighbors, allowing for easy
    movement between linked cells.

    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = False
        self.north_neighbor = None
        self.east_neighbor = None
        self.south_neighbor = None
        self.west_neighbor = None
        self.north_wall = None
        self.east_wall = None
        self.south_wall = None
        self.west_wall = None

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
    def walls(self):
        walls = [
            self.north_wall,
            self.east_wall,
            self.south_wall,
            self.west_wall,
        ]
        return walls

    @property
    def active_walls(self):
        return [wall for wall in self.walls if wall.active]

    @property
    def inner_active_walls(self):
        walls = []
        for wall in self.active_walls:
            if len(wall.adjacent_cells) > 1:
                walls.append(wall)
        return walls

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

    def get_wall_position(self, wall):
        if wall not in self.walls:
            raise ValueError("Given wall is not adjacent to this cell.")
        if wall is self.north_wall:
            wall_position = "north"
        elif wall is self.east_wall:
            wall_position = "east"
        elif wall is self.south_wall:
            wall_position = "south"
        else:
            wall_position = "west"
        return wall_position

    def get_wall_between(self, neighbor):
        if neighbor not in self.neighbors:
            raise ValueError("Given cell is not a neighbor of this cell.")
        if neighbor is self.north_neighbor:
            wall = self.north_wall
        elif neighbor is self.east_neighbor:
            wall = self.east_wall
        elif neighbor is self.south_neighbor:
            wall = self.south_wall
        else:
            wall = self.west_wall
        return wall

    def move_to(self, target_cell, target_wall):
        if target_cell is None or not target_cell.active or target_wall.active:
            target_cell = self
        return target_cell

    def move_north(self):
        return self.move_to(self.north_neighbor, self.north_wall)

    def move_east(self):
        return self.move_to(self.east_neighbor, self.east_wall)

    def move_south(self):
        return self.move_to(self.south_neighbor, self.south_wall)

    def move_west(self):
        return self.move_to(self.west_neighbor, self.west_wall)


class MazeWall:
    """A wall dividing two adjacent cells in a maze."""

    def __init__(self):
        self.active = True
        self.cell1 = None
        self.cell2 = None

    @property
    def adjacent_cells(self):
        return [cell for cell in [self.cell1, self.cell2] if cell is not None]

    @property
    def active_adjacent_cells(self):
        return [cell for cell in self.adjacent_cells if cell.active]

    @property
    def inactive_adjacent_cells(self):
        return [cell for cell in self.adjacent_cells if not cell.active]


class AbstractMaze:
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
                # Assign neighbors.
                if y > 0:
                    cell.north_neighbor = cells[x][y-1]
                if y < self.height-1:
                    cell.south_neighbor = cells[x][y+1]
                if x > 0:
                    cell.west_neighbor = cells[x-1][y]
                if x < self.width-1:
                    cell.east_neighbor = cells[x+1][y]
                # Assign walls.
                if cell.north_wall is None:
                    wall = MazeWall()
                    wall.cell1 = cell
                    cell.north_wall = wall
                    if cell.north_neighbor is not None:
                        wall.cell2 = cell.north_neighbor
                        cell.north_neighbor.south_wall = wall
                if cell.east_wall is None:
                    wall = MazeWall()
                    wall.cell1 = cell
                    cell.east_wall = wall
                    if cell.east_neighbor is not None:
                        wall.cell2 = cell.east_neighbor
                        cell.east_neighbor.west_wall = wall
                if cell.south_wall is None:
                    wall = MazeWall()
                    wall.cell1 = cell
                    cell.south_wall = wall
                    if cell.south_neighbor is not None:
                        wall.cell2 = cell.south_neighbor
                        cell.south_neighbor.north_wall = wall
                if cell.west_wall is None:
                    wall = MazeWall()
                    wall.cell1 = cell
                    cell.west_wall = wall
                    if cell.west_neighbor is not None:
                        wall.cell2 = cell.west_neighbor
                        cell.west_neighbor.east_wall = wall
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
        step = self.steps.pop(0)
        step.apply(self)

    def mature(self):
        """Fully mature the maze by exhausting its list of steps."""
        while self.steps:
            self.update()


class GrowStep:
    """A single step in the growing of a maze."""

    def __init__(self, actions):
        if isinstance(actions, GrowAction):
            actions = [actions]
        self.actions = actions

    def apply(self, maze):
        for action in self.actions:
            action.apply(maze)


class GrowAction:
    """A single action in the growing of a maze."""

    def __init__(self, action, cell_position, wall_position=None):
        self.action = action
        self.cell_position = cell_position
        self.wall_position = wall_position

    def apply(self, maze):
        # Get the cell or wall to adjust.
        x, y = self.cell_position
        adjusted = maze.cells[x][y]
        if self.wall_position is not None:
            adjusted = getattr(adjusted, f"{self.wall_position}_wall")
        # Apply the action to the adjusted item.
        if self.action in ["activate", "deactivate"]:
            adjusted.active = self.action == "activate"
        else:
            raise NotImplementedError(f"Invalid action: {self.action}.")
