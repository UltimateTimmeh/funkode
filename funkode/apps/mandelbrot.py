"""Interactively navigate the Mandelbrot set."""
import pygame

import funkode.complex.mandelbrot
import funkode.core.constants
import funkode.core.palette
import funkode.core.scene

FRAMERATE = 60
SCREEN_SIZE = (400, 300)
SCREEN_ITERATIONS = 100
ZOOM_FACTOR = 0.5
TRANSLATE_FACTOR = 0.05

SCREENSHOT_SIZE = (3840, 2160)
SCREENSHOT_ITERATIONS = 1000


class MandelbrotScene(funkode.core.scene.Scene):
    """The Mandelbrot scene."""

    def __init__(self, amin, amax, bmin, bmax, na, nb, max_iterations,
                 palettes):
        self.mandelbrot_set = funkode.complex.mandelbrot.MandelbrotSet(
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
        self._draw_mandelbrot_set(screen)
        self._draw_complex_at_mouse(screen)
        self._draw_max_iterations_at_mouse(screen)

    def _draw_mandelbrot_set(self, screen):
        pixel_colors = self.mandelbrot_set.pixel_colors.transpose((1, 0, 2))
        surface = pygame.surfarray.make_surface(pixel_colors)
        screen.blit(surface, (0, 0))

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
    palettes = funkode.core.palette.ALL
    # Initialize some PyGame stuff.
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    icon_fp = funkode.core.constants.ICONS_DIR/"mandelbrot.png"
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
    game = funkode.core.scene.SceneContext(scene, FRAMERATE)
    game.run(screen)


if __name__ == "__main__":
    main()
