# FunKode

A repository in which I have fun with Python code!

## Setup

### Regular users

First, clone the git repository:

```bash
git clone https://www.github.com/UltimateTimmeh/funkode /tmp/funkode
```

Next, install FunKode as a Python package:

```bash
cd /tmp/funkode
python -m pip install .
```

Finally, remove the git repository:

```bash
rm -r /tmp/funkode
```

To update to the latest version, simply repeat the above steps.

### Developers

First, clone the git repository to a destination of your choosing we'll call
`<FUNKODE_ROOT>`:

```bash
git clone https://www.github.com/UltimateTimmeh/funkode <FUNKODE_ROOT>
```

Next, set up the virtual environment:

```bash
cd <FUNKODE_ROOT>
virtualenv -ppython3 .venv
```

Finally, install FunKode and its development dependencies in editable mode:

```bash
cd <FUNKODE_ROOT>
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements_dev.txt
```

## Usage

### Mandelbrot Viewer

Interactively explore the wonderful fractals of the Mandelbrot set. Move around, zoom in/out
and take screenshots with different color palettes. For example:

![Mandelbrot set with GRAYSCALE palette](screenshots/mandelbrot_viewer_0.png)
![Zoomed in Mandelbrot set with FIRE palette](screenshots/mandelbrot_viewer_1.png)

Launch with the following command:

```bash
mandelbrot
```

### Ray Casting

Move the mouse and watch as rays are emitted from it and stop at the first randomly generated
wall they encounter.

![Ray Casting](screenshots/ray_casting_0.png)

Launch with the following command:

```bash
raycasting
```

### Hide and Seek

A simple game which uses the ray casting module. Move around the randomly generated levels
and try to find the enemy before the enemy finds you.

![Hide and Seek - You Won!](screenshots/hide_and_seek_0.png)
![Hide and Seek - You Lost!](screenshots/hide_and_seek_1.png)

Launch with the following command:

```bash
hide-and-seek
```

## Testing

### Unit tests

To run the unit tests, execute the following commands, where `<FUNKODE_ROOT>` is the root
directory of your local copy of the funkode repository:

```bash
cd <FUNKODE_ROOT>
source .venv/bin/activate
pytest --cov=funkode/ --cov-report=term-missing tests/
```

This will run the unit tests and print a coverage report that shows which lines are not
covered by the unit tests.

### Code style

Use pylint to check the code style:

```bash
cd <FUNKODE_ROOT>
source .venv/bin/activate
pylint --rcfile=tests/pylintrc funkode/
```

Feature branches cannot be merged until all comments are dealt with.

## Ideas for future fun

Here are some ideas for topics to explore in the future:

- **3D Rendering with ray casting** - To create Doom-like scenarios (the game).
- **Smart Rockets** - Genetic algorithm in which rockets automatically learn to hit a target.
  or perhaps some other genetic algorithm challenge, like particles learning to navigate
  a maze (running only) or a 2D platformer level (running and jumping)
- **Mandelbulb** - This groovy 3D object first requires exploring the following:
  - *Signed Distance Functions*
  - *Ray Marching*
