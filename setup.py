#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script for the Funkode package."""

import setuptools

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as req_file:
    requirements = req_file.read()

with open("requirements_dev.txt") as req_dev_file:
    requirements_dev = req_dev_file.read()

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    requirements,
    requirements_dev,
]

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
                  "mandelbrot = funkode.mandelbrot:main",
                  "raycasting = funkode.raycasting:main",
              ],
          },
    install_requires=requirements,
    long_description=readme + "\n",
    include_package_data=True,
    keywords="funkode",
    name="funkode",
    packages=setuptools.find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://www.github.com/UltimateTimmeh/funkode",
    zip_safe=False,
    version=version,
)
