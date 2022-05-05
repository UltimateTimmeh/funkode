"""Play around with ray casting."""
import numpy as np
import shapely.geometry


class RayCaster:
    """An entity in the scene which emits rays in a certain field of view.

    Args:
        position (tuple[float]): The ray caster's position as an (x, y) tuple.
        angle (float): The direction in which the ray caster is facing as an
            angle in radians.
        field_of_view (float): The ray caster's field of view in radians. The
            field of view is centered on the angle in which the ray caster is
            facing.
        number_of_rays (int): The number of rays emitted by the ray caster.
            These are evenly distributed across the field of view, end-points
            included.

    """

    def __init__(self, position, angle, field_of_view, number_of_rays):
        self.position = position
        self.angle = angle
        self.field_of_view = field_of_view
        self.number_of_rays = number_of_rays
        self.rays = None

    @property
    def polygon_points(self):
        """np.array or None: The ray caster's visible area polygon points.

        This is ``None`` if the ray caster has not yet cast any rays or if none
        of the rays hit anything.

        """
        points = None
        if self.rays is not None and len(self.rays_that_hit)>0:
            position = self.position.reshape(-1, 2)
            points = self.rays_that_hit[:, 1]
            points = np.concatenate([position, points, position], axis=0)
        return points

    @property
    def rays_that_hit(self):
        """np.array or None: The rays that have a valid target point.

        This is ``None`` if the ray caster has not yet cast any rays. If none
        of the rays hit anything, the resulting array is empty.

        """
        rays = None
        if self.rays is not None:
            rays = self.rays.copy()
            rays = rays[~np.isnan(rays[:, 1, 0])]
        return rays

    def cast_to(self, walls):
        """Have the ray caster cast rays to a list of walls.

        The resulting rays in ``self.rays`` that don't hit anything have
        ``[np.nan, np.nan]`` as their target point. To get only the rays that
        hit something, use ``self.rays_that_hit``.

        Args:
            walls (list[Wall]): List of walls.

        Returns:
            np.array: The resulting rays. Note that this is also an in-place
            operation which stores the rays in `self.rays`, but the rays are
            also returned by this method for convenience.

        """
        # If there are no walls, then none of the rays hit anything.
        if not walls:
            ray = np.concatenate([self.position, [np.nan, np.nan]])
            rays = ray.reshape((1, 2, 2)).repeat(self.number_of_rays, axis=0)
            self.rays = rays
            return self.rays
        # The array of arc angles.
        arc_start = self.angle - self.field_of_view/2
        arc_stop = self.angle + self.field_of_view/2
        arc = np.linspace(arc_start, arc_stop, self.number_of_rays)
        arc = arc.repeat(len(walls))
        # The array of ray source points.
        number_of_combinations = self.number_of_rays*len(walls)
        p1 = self.position.reshape(-1, 2).astype(float)
        p1 = p1.repeat(number_of_combinations, axis=0)
        x1, y1 = p1.T
        # The array of initial ray target points.
        p2 = p1.copy()
        p2[:, 0] += np.cos(arc)
        p2[:, 1] += np.sin(arc)
        x2, y2 = p2.T
        # The array of first wall points.
        p3 = np.array([wall.p1 for wall in walls])
        p3 = np.tile(p3, (self.number_of_rays, 1))
        x3, y3 = p3.T
        # The array of second wall points.
        p4 = np.array([wall.p2 for wall in walls])
        p4 = np.tile(p4, (self.number_of_rays, 1))
        x4, y4 = p4.T
        # Calculate the line intersection parameters.
        denominator = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        denominator[abs(denominator) < 1e-5] = np.nan
        t_enumerator = (x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)
        u_enumerator = (x1-x3)*(y1-y2) - (y1-y3)*(x1-x2)
        t, u = t_enumerator/denominator, u_enumerator/denominator
        # Adjust ray intersection parameter to exclude invalid intersections.
        # The length of invalid intersections is set to infinite, to avoid their
        # selection if a valid option is available.
        t[np.isnan(t) | (t<0) | (u<0) | (u>1)] = np.inf
        # For each ray, find the closest hit.
        t_reshaped = t.reshape(self.number_of_rays, len(walls), 1)
        closest = np.argmin(t_reshaped, axis=1).flatten()
        closest += np.arange(self.number_of_rays)*len(walls)
        # Now set the length of invalid intersections to NaN.
        t[np.isinf(t)] = np.nan
        # Update the array of ray target points.
        p2 = p1 + t[:, None]*(p2-p1)
        # Select final ray source and target points.
        p1 = p1.flatten().reshape(-1, 2)[closest]
        p2 = p2.flatten().reshape(-1, 2)[closest]
        self.rays = np.column_stack((p1, p2))
        self.rays = self.rays.reshape(self.number_of_rays, 2, 2)
        return self.rays

    def sees_point(self, point):
        """Return whether the ray caster can see a point.

        Args:
            point (np.array): The point.

        Returns:
            bool or None: Whether the ray caster can see the point, i.e. whether
            the point is inside the ray caster's visible area polygon. This is
            ``None`` if the ray caster hasn't cast any rays or if none of the
            rays hit anything.

        """
        visible = None
        if self.polygon_points is not None:
            polygon = shapely.geometry.Polygon(self.polygon_points)
            visible = polygon.contains(shapely.geometry.Point(point))
        return visible


class Wall:
    """A ray-blocking wall.

    Args:
        p1 (np.array): The wall's first point.
        p2 (np.array): The wall's second point.

    """

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
