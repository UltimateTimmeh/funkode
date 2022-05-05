"""Functions that do something random."""
import numpy as np


def random_point_on_screen(screen_size):
    """Return a random point on a 2D screen of given size.

    Args:
        screen_size (tuple[int]): The screen size as a (width, height) tuple.

    Returns:
        np.array: The 2D coordinates of a random point on the screen.

    """
    return np.round(np.random.rand(2)*screen_size)
