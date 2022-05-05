"""Unittests for the `funkode.core.random` module."""
import unittest

import numpy as np

from funkode.core import random


class TestFunctions(unittest.TestCase):
    """Unit tests for functions in the `funkode.core.random` module."""

    def test_random_point_on_screen(self):
        """random.random_point_on_screen: correct output

        Test if `cast.random_point` correctly returns a random point
        within the bounds of the given screen dimensions.

        """
        np.random.seed(42)
        screen_size = (800, 600)
        output = random.random_point_on_screen(screen_size)
        self.assertEqual(output.tolist(), [300.0, 570.0])
