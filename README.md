# Sage Physics

[![ci](https://github.com/georgedouzas/sage-physics/workflows/ci/badge.svg)](https://github.com/georgedouzas/sage-physics/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://georgedouzas.github.io/sage-physics/)
[![pypi version](https://img.shields.io/pypi/v/sage-physics.svg)](https://pypi.org/project/sage-physics/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/georgedouzas/sage-physics)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/sage-physics/community)

A Python package to create and simulate physics models. It is based on the open-source Computer Algebra System [SageMath](https://www.sagemath.org/).

## Installation

There are two main ways of installing the library. The first is through
[pip](https://pip.pypa.io/en/stable/)  while the second requires
[PDM](https://pdm.fming.dev/latest/).

### pip

The simplest installation method, recommended mainly for users, is the following:

```bash
sage --pip install sage-physics
```

Another installation method is from the source:

```bash
git clone https://github.com/georgedouzas/sage-physics.git
cd sage-physics
sage --pip install .
```

*The above methods require SageMath with version 9.7 and above, installed from source or prebuilt distribution.*

### PDM

This option requires PDM to be installed. Then you can simply run the following commands:

```bash
git clone https://github.com/georgedouzas/sage-physics.git
cd sage-physics
make setup
```

*The above methods require SageMath with version 9.7 and above, installed only a prebuilt
distribution.*
