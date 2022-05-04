"""Unittests for the `funkode.ray.cast` module."""
import unittest

import numpy as np

from funkode.ray import cast


class TestFunctions(unittest.TestCase):
    """Unit tests for functions in the `funkode.ray.cast` module."""

    def test_random_point(self):
        """cast.random_point: correct output

        Test if `cast.random_point` correctly returns a random point
        within the bounds of the given screen dimensions.

        """
        np.random.seed(42)
        screen_size = (800, 600)
        output = cast.random_point(screen_size)
        self.assertEqual(output.tolist(), [300.0, 570.0])


class TestRayCatser(unittest.TestCase):
    """Unit tests for the `funkode.cast.RayCaster` class."""

    def setUp(self):
        """Setup for the test class."""
        position = np.array([0., 0.])
        angle = 0.
        field_of_view = np.pi
        number_of_rays = 3
        self.raycaster = cast.RayCaster(
            position, angle, field_of_view, number_of_rays
        )
        self.walls = [
            cast.Wall(np.array([-10., -10.]), np.array([10., -10.])),
            cast.Wall(np.array([10., -10.]), np.array([10., 10.])),
        ]

    def test_init(self):
        """cast.RayCaster: correct output

        Test if `cast.RayCaster` objects are initialized correctly.

        """
        self.assertEqual(self.raycaster.position.tolist(), [0., 0.])
        self.assertEqual(self.raycaster.angle, 0.)
        self.assertEqual(self.raycaster.field_of_view, np.pi)
        self.assertEqual(self.raycaster.number_of_rays, 3)
        self.assertIsNone(self.raycaster.rays)

    def test_polygon_points(self):
        """RayCaster.polygon_points: correct output

        Test if `RayCaster.polygon_points` correctly returns the points of the
        ray caster's visible area polygon.

        """
        self.raycaster.cast_to(self.walls)
        output = self.raycaster.polygon_points
        output[abs(output)<1e-5] = 0.
        expected = [[0., 0.],
                    [0., -10.],
                    [10., 0.],
                    [0., 0.]]
        self.assertEqual(output.tolist(), expected)

    def test_polygon_points_not_cast(self):
        """RayCaster.polygon_points: correct output when not cast

        Test if `RayCaster.polygon_points` correctly returns ``None`` when no
        rays have yet been cast.

        """
        output = self.raycaster.polygon_points
        self.assertIsNone(output)

    def test_polygon_points_no_hits(self):
        """RayCaster.polygon_points: correct output when no hits

        Test if `RayCaster.polygon_points` correctly returns ``None`` when none
        of the rays hits anything.

        """
        walls = []
        self.raycaster.cast_to(walls)
        output = self.raycaster.polygon_points
        self.assertIsNone(output)

    def test_rays_that_hit(self):
        """RayCaster.rays_that_hit: correct output

        Test if `RayCaster.rays_that_hit` correctly returns only the rays that
        hit a wall.

        """
        self.raycaster.cast_to(self.walls)
        output = self.raycaster.rays_that_hit
        output[abs(output)<1e-5] = 0.
        expected = [[[0., 0.], [0., -10.]],
                    [[0., 0.], [10., 0.]]]
        self.assertEqual(output.tolist(), expected)

    def test_rays_that_hit_not_cast(self):
        """RayCaster.rays_that_hit: correct output when not cast

        Test if `RayCaster.rays_that_hit` correctly returns ``None`` when no
        rays have yet been cast.

        """
        output = self.raycaster.rays_that_hit
        self.assertIsNone(output)

    def test_rays_that_hit_no_hits(self):
        """RayCaster.rays_that_hit: correct output when no hits

        Test if `RayCaster.rays_that_hit` correctly returns an empty list when
        none of the rays hits anything.

        """
        walls = []
        self.raycaster.cast_to(walls)
        output = self.raycaster.rays_that_hit
        expected = []
        self.assertEqual(output.tolist(), expected)

    def test_cast_to(self):
        """RayCaster.cast_to: correct result and output

        Test if `RayCaster.cast_to` correctly casts rays to the given walls.

        """
        self.assertIsNone(self.raycaster.rays)
        output = self.raycaster.cast_to(self.walls)
        output[abs(output)<1e-5] = 0.
        expected = [[[0., 0.], [0., -10.]],
                    [[0., 0.], [10., 0.]],
                    [[False, False], [True, True]]]
        self.assertEqual(output[:2].tolist(), expected[:2])
        self.assertEqual(np.isnan(output[-1]).tolist(), expected[-1])
        self.assertIs(output, self.raycaster.rays)

    def test_cast_to_no_walls(self):
        """RayCaster.cast_to: correct output when no walls

        Test if `RayCaster.cast_to` correctly casts rays when no walls are
        given.

        """
        walls = []
        self.assertIsNone(self.raycaster.rays)
        output = self.raycaster.cast_to(walls)
        expected = [[[False, False], [True, True]],
                    [[False, False], [True, True]],
                    [[False, False], [True, True]]]
        self.assertEqual(np.isnan(output).tolist(), expected)

    def test_cast_to_no_rays(self):
        """RayCaster.cast_to: correct output when no rays

        Test if `RayCaster.cast_to` correctly casts rays when there are no rays.

        """
        self.raycaster.number_of_rays = 0
        self.assertIsNone(self.raycaster.rays)
        output = self.raycaster.cast_to(self.walls)
        expected = []
        self.assertEqual(output.tolist(), expected)

    def test_sees_point_visible(self):
        """RayCaster.sees_point: correct output

        Test if `RayCaster.sees_point` correctly returns when a point is
        visible.

        """
        self.raycaster.cast_to(self.walls)
        output = self.raycaster.sees_point(np.array([3., -3.]))
        self.assertTrue(output)

    def test_sees_point_invisible(self):
        """RayCaster.sees_point: correct output

        Test if `RayCaster.sees_point` correctly returns when a point is
        invisible.

        """
        self.raycaster.cast_to(self.walls)
        output = self.raycaster.sees_point(np.array([-3., 3.]))
        self.assertFalse(output)


class TestWall(unittest.TestCase):
    """Unit tests for the `funkode.cast.Wall` class."""

    def test_init(self):
        """cast.Wall: correct output

        Test if `cast.Wall` objects are initialized correctly.

        """
        p1 = np.array([0., 0.])
        p2 = np.array([1., 1.])
        output = cast.Wall(p1, p2)
        self.assertIs(output.p1, p1)
        self.assertIs(output.p2, p2)
