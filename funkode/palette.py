"""Color palettes for general visualization purposes."""
import numpy as np


class PaletteColor:
    """A color on a palette."""

    def __init__(self, color, location):
        self.color = color
        self.location = location


class Palette:
    """A palette."""

    def __init__(self, color_stops, ncolors=250):
        self.color_stops = color_stops
        self.ncolors = ncolors
        color_map = map(self._select, np.linspace(0., 1., ncolors))
        self.colors = np.array(list(color_map), dtype=np.uint8)

    def __getitem__(self, ind):
        return self.colors[ind%self.ncolors]

    def _select(self, hue):
        """Select color based on hue."""
        # Make sure hue is between 0. and 1.
        hue = max(0., hue)
        hue = min(1., hue)
        # Select color interval.
        index_min_color = 0
        index_max_color = 1
        while hue > self.color_stops[index_max_color].location:
            index_min_color += 1
            index_max_color += 1
        # Interpolate between min and max colors.
        min_color = self.color_stops[index_min_color]
        max_color = self.color_stops[index_max_color]
        frac = (hue-min_color.location)/(max_color.location-min_color.location)
        color = min_color.color + frac*(max_color.color-min_color.color)
        return color


GRAYSCALE = Palette([
    PaletteColor(np.array([0., 0., 0.]), 0.),
    PaletteColor(np.array([255., 255., 255.]), 0.5),
    PaletteColor(np.array([0., 0., 0.]), 1.),
])
FIRE = Palette([
    PaletteColor(np.array([0., 0., 0.]), 0.),
    PaletteColor(np.array([255., 0., 0.]), 0.2),
    PaletteColor(np.array([255., 255., 0.]), 0.4),
    PaletteColor(np.array([255., 255., 255.]), 0.5),
    PaletteColor(np.array([255., 255., 0.]), 0.6),
    PaletteColor(np.array([255., 0., 0.]), 0.8),
    PaletteColor(np.array([0., 0., 0.]), 1.),
])
SEASHORE = Palette([
    PaletteColor(np.array([0.791, 0.996, 0.763])*255, 0./6.),
    PaletteColor(np.array([0.897, 0.895, 0.656])*255, 1./6.),
    PaletteColor(np.array([0.947, 0.316, 0.127])*255, 2./6.),
    PaletteColor(np.array([0.518, 0.111, 0.092])*255, 3./6.),
    PaletteColor(np.array([0.020, 0.456, 0.684])*255, 4./6.),
    PaletteColor(np.array([0.538, 0.826, 0.818])*255, 5./6.),
    PaletteColor(np.array([0.791, 0.996, 0.763])*255, 6./6.),
])
FOREST = Palette([
    PaletteColor(np.array([30.2, 25.1, 12.5])/100*255, 0./3.),
    PaletteColor(np.array([65.9, 55.7, 42.0])/100*255, 1./3.),
    PaletteColor(np.array([29.0, 52.9, 22.4])/100*255, 1.5/3.),
    PaletteColor(np.array([8.6, 16.9, 42.4])/100*255, 2./3.),
    PaletteColor(np.array([14.5, 34.9, 10.6])/100*255, 2.5/3.),
    PaletteColor(np.array([30.2, 25.1, 12.5])/100*255, 3./3.),
])

ALL = [
    GRAYSCALE,
    FIRE,
    SEASHORE,
    FOREST,
]
