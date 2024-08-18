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
[version badge]: <https://img.shields.io/pypi/v/scikit-complexity.svg>
[pythonversion badge]: <https://img.shields.io/pypi/pyversions/scikit-complexity.svg>
[downloads badge]: <https://img.shields.io/pypi/dd/scikit-complexity>
[gitter]: <https://gitter.im/scikit-complexity/community>
[gitter badge]: <https://badges.gitter.im/join%20chat.svg>
[discussions]: <https://github.com/georgedouzas/scikit-complexity/discussions>
[discussions badge]: <https://img.shields.io/github/discussions/georgedouzas/scikit-complexity>
[ci]: <https://github.com/georgedouzas/scikit-complexity/actions?query=workflow>
[ci badge]: <https://github.com/georgedouzas/scikit-complexity/actions/workflows/ci.yml/badge.svg?branch=main>
[doc]: <https://github.com/georgedouzas/scikit-complexity/actions?query=workflow>
[doc badge]: <https://github.com/georgedouzas/scikit-complexity/actions/workflows/doc.yml/badge.svg?branch=main>

# scikit-complexity

| Category          | Tools    |
| ------------------| -------- |
| **Development**   | [![black][black badge]][black] [![ruff][ruff badge]][ruff] [![mypy][mypy badge]][mypy] [![docformatter][docformatter badge]][docformatter] |
| **Package**       | ![version][version badge] ![pythonversion][pythonversion badge] ![downloads][downloads badge] |
| **Documentation** | [![mkdocs][mkdocs badge]][mkdocs]|
| **Communication** | [![gitter][gitter badge]][gitter] [![discussions][discussions badge]][discussions] |

## Introduction

A Python package to create and simulate complex systems.

## Prerequisites

Either `sagemath-standard` or an installation of [SageMath](https://www.sagemath.org/) is required with a version greater than
10.0.

## Installation

Initially, create a Python virtual environment with one of the following two ways: 

- Use the command `sage -python -m venv --system-site-packages .venv` to create and activate Python virtual environment with all the prerequisites installed:

- Use one of the standard ways to create a Python virtual environment and install the package `sagemath-standard`.

You can install `scikit-complexity` either as a normal user or for development purposes.

### User

For user installation, `scikit-complexity` is currently available on the PyPi's repository, and you can
install it via `pip`:

```bash
pip install scikit-complexity
```

### Development

Development installation requires to clone the repository and change directory to the project's root:

```bash
git clone https://github.com/georgedouzas/scikit-complexity.git
cd scikit-complexity
```

Finally, use [PDM](https://github.com/pdm-project/pdm) to select the virtual environment and install the project as well as the
main and development dependencies:

```bash
pdm use .venv
pdm install
```

## Usage

One of the `scikit-complexity` main goals is to provide a unified interface for modelling various complex systems.
For example, let's define two independent harmonic oscillators that oscillate in the axes x and y:

```python
from sage.all import assume, symbolic_expression, var, cos, sin, sqrt
from skcomplex.physics import (
    ClassicalMechanicsSystem,
    ExternalForce,
    PointParticle,
)
from skcomplex.spaces import EuclideanSpace
k, x__1, y__2 = var('k x__1 y__2')
assume(k > 0)
system = ClassicalMechanicsSystem(
    particles=[PointParticle('1'), PointParticle('2')],
    external_interactions=[
        ExternalForce('elastic1', '1', [-k * x__1, 0]),
        ExternalForce('elastic2', '2', [0, -k * y__2])
    ],
    space=EuclideanSpace('euclidean', n_dim=2),
)
```

We can simulate the system and solve the dynamical equations:

```python
system.simulate()
var('_K1 _K2 m__1 m__2 t')
assert system.simulation_results_['dynamic_equations']['solutions'] == {
    '1': [_K2*cos(sqrt(k)*t/sqrt(m__1)) + _K1*sin(sqrt(k)*t/sqrt(m__1)), _K2*t + _K1],
    '2': [_K2*t + _K1, _K2*cos(sqrt(k)*t/sqrt(m__2)) + _K1*sin(sqrt(k)*t/sqrt(m__2))]
}
```
