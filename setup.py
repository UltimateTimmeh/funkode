#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script for the Funkode package."""

import setuptools

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as req_file:
    requirements = req_file.read()

version = "0.0.1"

setuptools.setup(
    author="Tim Dezutter",
    author_email="dezutter.tim@gmail.com",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
    ],
    description="Having some fun with code.",
    entry_points = {
              "console_scripts": [
                  "mandelbrot = funkode.apps.mandelbrot:main",
                  "raycasting = funkode.apps.raycasting:main",
                  "hide-and-seek = funkode.apps.hide_and_seek:main",
                  "generate-maze = funkode.apps.generate_maze:main",
              ],
          },
    install_requires=requirements,
    long_description=readme + "\n",
    include_package_data=True,
    keywords="funkode",
    name="funkode",
    packages=setuptools.find_packages(),
    test_suite="tests",
    url="https://www.github.com/UltimateTimmeh/funkode",
    zip_safe=False,
    version=version,
)
