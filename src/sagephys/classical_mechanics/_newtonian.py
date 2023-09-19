"""Newtonian mechanics models.

This module implements classes which can be used to define and solve the
dynamical equations of Netwonian models.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>
# License: MIT

from collections.abc import Callable
from typing import Any, Self

from sage.all import Expression, assume, desolve, diff, function, var, vector, zero_vector

Forces = dict[str, dict[str, list[str]]]

SPACE_DIM = 3
VARIABLES = ('m', 'x', 'y', 'z', 'v_x', 'v_y', 'v_z')


def check_particles_labels(forces: Forces | None) -> list[str]:
    """Check the particles labels."""
    if forces is None:
        return ['particle']
    particles_labels = list(forces.keys())
    for forces_label in forces.values():
        for F_vect in forces_label.values():
            for F in F_vect:
                if isinstance(F, Expression):
                    for variable in F.variables():
                        *prefix, suffix = str(variable).split('_')
                        error_msg = f'Wrong variable name `{variable}` was found.'
                        if prefix and prefix[0].startswith(VARIABLES):
                            if '_'.join(prefix) not in VARIABLES:
                                raise ValueError(error_msg)
                            particles_labels.append(suffix)
                        elif suffix in VARIABLES:
                            raise ValueError(error_msg)
    particles_labels = sorted(set(particles_labels))
    return particles_labels


def check_force_vector(F_vect: list[Expression]) -> Callable:
    """Check the provided force vector."""
    if not isinstance(F_vect, list):
        error_msg = f'Force vector {F_vect} is not a list.'
        raise TypeError(error_msg)
    elif len(F_vect) != SPACE_DIM:
        error_msg = f'Force vector {F_vect} is a list but does not have three elements.'
        raise TypeError(error_msg)
    F_vect_time = F_vect.copy()
    variables = tuple(set(VARIABLES).difference(['m']))
    for ind, F in enumerate(F_vect_time):
        if not isinstance(F, Expression):
            F_vect_time[ind] = F * function('F')(var('t'))
        else:
            args_space = [str(arg) for arg in F.args() if arg != 't' and str(arg).startswith(variables)]
            coordinates = {var_name: function(var_name)(var('t')) for var_name in args_space}
            F_vect_time[ind] = F(**coordinates)
    return vector(F_vect_time)


class NewtonianPointParticlesModel:
    """Newtonial model of point particles.

    Define and solve the dynamical equations of a Newtonian mechanics model
    of a system of point particles.

    Args:
        forces:
            A dictionary that represents the forces on the particles. Each key
            is a particle label and each value is a dictionary of pairs with keys as the force
            label and values as the force vector. Please check the examples below.

    Attributes:
        particle_labels_ (list[str]):
            The labels of the particles.

        dynamic_equations_ (dict[str: Any]):
            The dynamic equations, one for each particle.

        dynamic_equations_solutions_ (dict[str: Any]):
            The solutions of the dynamic equations, one for each particle.
    """

    def __init__(self: Self, forces: Forces | None = None) -> None:
        self.forces = forces

    def __repr__(self: Self) -> str:
        return f'{self.__class__.__name__} with {len(self.particles_labels_)} point particle(s)'

    @property
    def particles_labels_(self: Self) -> list[str]:
        return check_particles_labels(self.forces)

    @property
    def forces_(self: Self) -> Forces:
        forces = self.forces.copy() if self.forces is not None else {}
        for label in self.particles_labels_:
            if label not in forces:
                forces[label] = {}
        return forces

    def analyze(self: Self) -> Self:
        """Analyze the model's dynamic equations."""
        self.equations_: dict[str, list[Any]] = {}
        t = var('t')
        for label in self.particles_labels_:
            coords = [function(coord)(t) for coord in (f'x_{label}', f'y_{label}', f'z_{label}')]
            F_total_vect = zero_vector(SPACE_DIM)
            for _, F_vect in self.forces_[label].items():
                F_total_vect += check_force_vector(F_vect)
            m = var(f'm_{label}')
            assume(m > 0)
            self.equations_[label] = []
            for ind, F in enumerate(F_total_vect):
                self.equations_[label].append(m * diff(coords[ind], t, 2) == F)
        return self

    def solve(self: Self, initial_conditions: dict[str, Any] | None = None) -> dict[str, list[Any]]:
        """Solve the model's dynamic equations."""
        if not hasattr(self, 'equations_'):
            error_msg = 'Call the method `analyze` before the `solve`.'
            raise RuntimeError(error_msg)
        solutions: dict[str, list[Any]] = {}
        t = var('t')
        for label, des in self.equations_.items():
            coords = [function(coord)(t) for coord in (f'x_{label}', f'y_{label}', f'z_{label}')]
            solutions[label] = []
            for ind, de in enumerate(des):
                initial_conditions_label = initial_conditions[label][ind] if initial_conditions is not None else None
                solutions[label].append(
                    desolve(de, dvar=coords[ind], ivar=t, ics=initial_conditions_label),
                )
        return solutions
