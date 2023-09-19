[black badge]: <https://img.shields.io/badge/%20style-black-000000.svg>
[black]: <https://github.com/psf/black>
[docformatter badge]: <https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg>
[docformatter]: <https://github.com/PyCQA/docformatter>
[ruff badge]: <https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json>
[ruff]: <https://github.com/charliermarsh/ruff>
[mypy badge]: <http://www.mypy-lang.org/static/mypy_badge.svg>
[mypy]: <http://mypy-lang.org>
[mkdocs badge]: <https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat>
[mkdocs]: <https://squidfunk.github.io/mkdocs-material>
[version badge]: <https://img.shields.io/pypi/v/sage-physics.svg>
[pythonversion badge]: <https://img.shields.io/pypi/pyversions/sage-physics.svg>
[downloads badge]: <https://img.shields.io/pypi/dd/sage-physics>
[gitter]: <https://gitter.im/sage-physics/community>
[gitter badge]: <https://badges.gitter.im/join%20chat.svg>
[discussions]: <https://github.com/georgedouzas/sage-physics/discussions>
[discussions badge]: <https://img.shields.io/github/discussions/georgedouzas/sage-physics>

# sage-physics

| Category          | Tools    |
| ------------------| -------- |
| **Development**   | [![black][black badge]][black] [![ruff][ruff badge]][ruff] [![mypy][mypy badge]][mypy] [![docformatter][docformatter badge]][docformatter] |
| **Package**       | ![version][version badge] ![pythonversion][pythonversion badge] ![downloads][downloads badge] |
| **Documentation** | [![mkdocs][mkdocs badge]][mkdocs]|
| **Communication** | [![gitter][gitter badge]][gitter] [![discussions][discussions badge]][discussions] |

## Introduction

A Python package to create and simulate physics models.

## Prerequisites

An installation of [SageMath](https://www.sagemath.org/) with version > 10.0 is required.

## Installation

You can install `sage-physics` either as a normal user or for development purposes.

### User

For user installation, `sage-physics` is currently available on the PyPi's repository, and you can
install it via `pip`:

```bash
sage --pip install sage-physics
```

You can then start the Sage REPL with the command `sage` and use `sage-physics` through the Sage REPL:

```python
import sagephys
```

### Development

Development installation requires to clone the repository and change directory to the project's root:

```bash
git clone https://github.com/georgedouzas/sage-physics.git
cd sage-physics
```

Then create a Python virtual environment using the `sage` command:

```bash
sage -python -m venv --system-site-packages .venv
```

Finally, use [PDM](https://github.com/pdm-project/pdm) to select the virtual environment and install the project as well as the
main and development dependencies:

```bash
pdm use .venv
pdm install
```

You can then start the Sage REPL with the command `PYTHONPATH=src sage` and use `sage-physics` through the Sage REPL:

```python
import sagephys
```

## Usage

One of the `sage-physics` main goals is to provide a unified interface for various physics models. For example let's define two
independent harmonic oscillators that oscillate in the axes x and y:

```python
from sage.all import var, assume
from sagephys.classical_mechanics import NewtonianPointParticlesModel
k, x_particle1, y_particle2 = var('k x_particle1 y_particle2')
assume(k > 0)
forces = {
    'particle1': {'elastic': [- k * x_particle1, 0, 0]},
    'particle2': {'elastic': [0, -k * y_particle2, 0]}
}
model = NewtonianPointParticlesModel(forces)
```

We can get the dynamical equations:

```python
model.analyze()
model.equations_
```

We can also try to solve them:

```python
model.solve()
```
