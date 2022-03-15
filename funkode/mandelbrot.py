"""Plot the Mandelbrot set."""
import pathlib

import numpy as np
import pygame
from PIL import Image

import funkode.palette
import funkode.scene

FRAMERATE = 60
SCREEN_SIZE = (400, 300)
SCREEN_ITERATIONS = 100
ZOOM_FACTOR = 0.5
TRANSLATE_FACTOR = 0.05

SCREENSHOT_SIZE = (3840, 2160)
SCREENSHOT_ITERATIONS = 1000


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

    def draw(self, screen):
        """Draw the set on a PyGame screen."""
        pixel_colors = self.pixel_colors.transpose((1, 0, 2))
        surface = pygame.surfarray.make_surface(pixel_colors)
        screen.blit(surface, (0, 0))

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


class MandelbrotScene(funkode.scene.Scene):
    """The Mandelbrot scene."""

    def __init__(self, amin, amax, bmin, bmax, na, nb, max_iterations,
                 palettes):
        self.mandelbrot_set = MandelbrotSet(
            amin, amax, bmin, bmax,
            na, nb,
            max_iterations=max_iterations,
            palette=palettes[0],
        )
        self.palette_index = 0
        self.palettes = palettes

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.MOUSE_LEFT:
                x, y = pygame.mouse.get_pos()
                self.mandelbrot_set.center_pixel(x, y)
            if event.button == pygame.MOUSE_RIGHT:
                self.mandelbrot_set.reset_window()
            if event.button == pygame.MOUSE_MIDDLE:
                fp = "/tmp/mandelbrot.png"
                size = SCREENSHOT_SIZE
                iterations = SCREENSHOT_ITERATIONS
                self.mandelbrot_set.save_image(fp, size, iterations)
            if event.button == pygame.MOUSE_SCROLLUP:
                x, y = pygame.mouse.get_pos()
                self.mandelbrot_set.zoom_pixel(x, y, ZOOM_FACTOR)
            if event.button == pygame.MOUSE_SCROLLDN:
                x, y = pygame.mouse.get_pos()
                self.mandelbrot_set.zoom_pixel(x, y, 1/ZOOM_FACTOR)
        elif event.type == pygame.KEYDOWN:
            # Translation.
            if event.key in [pygame.K_a, pygame.K_d]:
                amin, amax = self.mandelbrot_set.amin, self.mandelbrot_set.amax
                a_translation = TRANSLATE_FACTOR*(amax-amin)
                if event.key == pygame.K_a:
                    self.mandelbrot_set.translate(-a_translation, 0.)
                if event.key == pygame.K_d:
                    self.mandelbrot_set.translate(a_translation, 0.)
            if event.key in [pygame.K_w, pygame.K_s]:
                bmin, bmax = self.mandelbrot_set.bmin, self.mandelbrot_set.bmax
                b_translation = TRANSLATE_FACTOR*(bmax-bmin)
                if event.key == pygame.K_w:
                    self.mandelbrot_set.translate(0., -b_translation)
                if event.key == pygame.K_s:
                    self.mandelbrot_set.translate(0., b_translation)
            if event.key == pygame.K_c:
                x, y = pygame.mouse.get_pos()
                self.mandelbrot_set.center_pixel(x, y)
            # Zoom.
            if event.key == pygame.K_e:
                a, b = self.mandelbrot_set.center
                self.mandelbrot_set.zoom_complex(a, b, ZOOM_FACTOR)
            if event.key == pygame.K_q:
                a, b = self.mandelbrot_set.center
                self.mandelbrot_set.zoom_complex(a, b, 1/ZOOM_FACTOR)
            # Others.
            if event.key == pygame.K_z:
                max_iterations = self.mandelbrot_set.max_iterations/2
                self.mandelbrot_set.set_max_iterations(max_iterations)
            if event.key == pygame.K_x:
                max_iterations = self.mandelbrot_set.max_iterations*2
                self.mandelbrot_set.set_max_iterations(max_iterations)
            if event.key == pygame.K_r:
                self.mandelbrot_set.reset_window()
            if event.key == pygame.K_f:
                self.cycle_palette()

    def update(self):
        pass

    def draw(self, screen):
        self.mandelbrot_set.draw(screen)
        self._draw_complex_at_mouse(screen)
        self._draw_max_iterations_at_mouse(screen)

    def _draw_complex_at_mouse(self, screen):
        # Initialize the text.
        x, y = pygame.mouse.get_pos()
        a, b = self.mandelbrot_set.pixel_to_complex(x, y)
        pos = x+12, y+20
        txt = f"{a:.5f}{'+' if b >=0 else ''}{b:.5f}i"
        font = pygame.freetype.SysFont("FreeSans", 12)
        # Draw a rectangle below the text.
        rect = font.get_rect(txt)
        rect.x, rect.y = pos[0]-1, pos[1]-1
        rect.width, rect.height = rect.width+2, rect.height+2
        pygame.draw.rect(screen, pygame.Color("white"), rect)
        # Draw the text.
        font.render_to(screen, pos, txt, pygame.Color("black"))

    def _draw_max_iterations_at_mouse(self, screen):
        # Initialize the text.
        x, y = pygame.mouse.get_pos()
        pos = x+12, y+35
        txt = f"max_iter: {self.mandelbrot_set.max_iterations}"
        font = pygame.freetype.SysFont("FreeSans", 12)
        # Draw a rectangle below the text.
        rect = font.get_rect(txt)
        rect.x, rect.y = pos[0]-1, pos[1]-1
        rect.width, rect.height = rect.width+2, rect.height+2
        pygame.draw.rect(screen, pygame.Color("white"), rect)
        # Draw the text.
        font.render_to(screen, pos, txt, pygame.Color("black"))

    def cycle_palette(self):
        """Cycle through the applied palette."""
        self.palette_index = (self.palette_index+1)%len(self.palettes)
        self.mandelbrot_set.set_palette(self.palettes[self.palette_index])


def main():
    """Main script execution function."""
    # Initial Mandelbrot settings.
    amin, amax = -2.5, 0.5
    bmin, bmax = -1., 1.
    na, nb = SCREEN_SIZE
    max_iterations = SCREEN_ITERATIONS
    palettes = funkode.palette.ALL
    # Initialize some PyGame stuff.
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    icon_fp = pathlib.Path(__file__).resolve().parent/"icons"/"mandelbrot.png"
    icon = pygame.image.load(icon_fp).convert_alpha()
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Mandelbrot Viewer")

    # Set up the scene.
    scene = MandelbrotScene(
        amin, amax, bmin, bmax,
        na, nb,
        max_iterations=max_iterations,
        palettes=palettes,
    )
    # Initialize and run the game.
    game = funkode.scene.SceneContext(scene, FRAMERATE)
    game.run(screen)


if __name__ == "__main__":
    main()
