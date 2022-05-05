"""The Mandelbrot set."""
import numpy as np
from PIL import Image


class MandelbrotSet:
    """The Mandelbrot set."""

    def __init__(self, amin, amax, bmin, bmax, na, nb, max_iterations,
                 palette):
        self.na = na
        self.nb = nb
        self.max_iterations = max_iterations
        self.palette = palette
        self.amin_original, self.amax_original = amin, amax
        self.bmin_original, self.bmax_original = bmin, bmax
        self.amin, self.amax = None, None
        self.bmin, self.bmax = None, None
        self.pixel_iterations = None
        self.pixel_colors = None
        self.set_window(amin, amax, bmin, bmax)

    def _update_iterations(self):
        # Calculate the amount of iterations for each pixel to escape.
        aa = np.linspace(self.amin, self.amax, self.na)
        bb = np.linspace(self.bmin, self.bmax, self.nb)
        ca, cb = np.meshgrid(aa, bb)
        za, zb = np.zeros(self.shape), np.zeros(self.shape)
        za2, zb2 = np.zeros(self.shape), np.zeros(self.shape)
        self.pixel_iterations = np.zeros(self.shape, dtype=int)
        self.pixel_iterations += self.max_iterations
        for iterations in range(self.max_iterations):
            zb = (za+za)*zb + cb
            za = za2 - zb2 + ca
            za2 = za*za
            zb2 = zb*zb
            escaped = za2+zb2 > 4
            za[escaped], zb[escaped] = np.nan, np.nan
            za2[escaped], zb2[escaped] = np.nan, np.nan
            self.pixel_iterations[escaped] = iterations

    def _update_colors(self):
        self.pixel_colors = self.palette[self.pixel_iterations]
        converged = self.pixel_iterations==self.max_iterations
        self.pixel_colors[converged] = (0, 0, 0)

    @property
    def center(self):
        """tuple[float]: The complex center of the Mandelbrot set's window."""
        return (self.amax+self.amin)/2, (self.bmax+self.bmin)/2

    @property
    def shape(self):
        """tuple[int]: The shape of the Mandelbrot set."""
        return (self.nb, self.na)

    def center_complex(self, a, b):
        """Center the Mandelbrot set's window on a complex number."""
        a_center, b_center = self.center
        a_translation = a - a_center
        b_translation = b - b_center
        self.translate(a_translation, b_translation)

    def center_pixel(self, x, y):
        """Center the Mandelbrot set's window on a pixel."""
        a, b = self.pixel_to_complex(x, y)
        self.center_complex(a, b)

    def pixel_to_complex(self, x, y):
        """Convert window pixel indices to the corresponding complex number."""
        a = self.amin + x/self.na*(self.amax-self.amin)
        b = self.bmin + y/self.nb*(self.bmax-self.bmin)
        return a, b

    def reset_window(self):
        """Reset the Mandelbrot set's window."""
        amin, amax = self.amin_original, self.amax_original
        bmin, bmax = self.bmin_original, self.bmax_original
        self.set_window(amin, amax, bmin, bmax)

    def save_image(self, fp, size=None, max_iterations=None):
        """Save the set as an image file.

        Args:
            fp (Path or str): Path of the image file.

        """
        pixel_colors = self.pixel_colors
        if size is not None or max_iterations is not None:
            na, nb = self.na, self.nb
            if size is not None:
                na, nb = size
            if max_iterations is None:
                max_iterations = self.max_iterations
            mandelbrot_sized = MandelbrotSet(
                self.amin, self.amax, self.bmin, self.bmax,
                na, nb,
                max_iterations=max_iterations,
                palette=self.palette,
            )
            pixel_colors = mandelbrot_sized.pixel_colors
        image = Image.fromarray(pixel_colors)
        image.save(fp)

    def set_max_iterations(self, max_iterations):
        """Set the Mandelbrot set's amount of maximum iterations."""
        # Make sure the number is acceptable.
        max_iterations = int(max_iterations)
        max_iterations = max(max_iterations, 10)
        max_iterations = min(max_iterations, 10000)
        self.max_iterations = max_iterations
        self._update_iterations()
        self._update_colors()

    def set_palette(self, palette):
        """Set the Mandelbrot set's palette."""
        self.palette = palette
        self._update_colors()

    def set_window(self, amin, amax, bmin, bmax):
        """Set the Mandelbrot set's window."""
        self.amin, self.amax = amin, amax
        self.bmin, self.bmax = bmin, bmax
        self._update_iterations()
        self._update_colors()

    def translate(self, a_translation, b_translation):
        """Translate the Mandelbrot set's window."""
        self.amin += a_translation
        self.amax += a_translation
        self.bmin += b_translation
        self.bmax += b_translation
        self._update_iterations()
        self._update_colors()

    def zoom_complex(self, a, b, zoom_factor):
        """Zoom the Mandelbrot set's window, targetting a complex number."""
        amin_new = a + zoom_factor*(self.amin-a)
        amax_new = a + zoom_factor*(self.amax-a)
        bmin_new = b + zoom_factor*(self.bmin-b)
        bmax_new = b + zoom_factor*(self.bmax-b)
        self.set_window(amin_new, amax_new, bmin_new, bmax_new)

    def zoom_pixel(self, x, y, zoom_factor):
        """Zoom the Mandelbrot set's window, targetting a pixel."""
        a, b = self.pixel_to_complex(x, y)
        self.zoom_complex(a, b, zoom_factor)
