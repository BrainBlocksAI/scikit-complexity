r"""
Newtonian mechanics models.

This module implements the :class:`NewtonianPointParticlesModel` and 
:class:`NewtonianRigidBodiesModel` classes which can be used to define 
and solve the dynamical equations of Netwonian models.
"""

from sage.all import *
from sage.symbolic.expression import Expression

ExternalForces = dict[str : dict[str:Expression] | None] | None
InternalForces = dict[tuple[str, str] : dict[str:Expression] | None] | None


class NewtonianPointParticlesModel:
    r"""
    Define and solve the dynamical equations of a Newtonian mechanics model
    of point particles.

    INPUT:

    - ``F_external`` -- A dictionary of key and value pairs (default: ``None``) that
      represents the external forces on the particles. Each key is a particle
      label and each value is either a list of expressions or dictionary of force
      label and expression pairs or ``None`` if there is no force. The expressions
      should be either a force vector or a potential function or a constraint
      equation. Please check the examples below.

    - ``F_internal`` -- A dictionary of key and value pairs (default: ``None``) that
      represents the internal forces between the particles. Each key is a tuple of
      particle labels pair and each value is either a list of expressions
      or dictionary of force label and expression pairs or ``None`` if there is no
      force. The expressions should be either a force vector or a potential function.
      Please check the examples below.

    EXAMPLES::

    Motion with constant velocity::

        sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
        sage: model = NewtonianPointParticlesModel(F_external={'bullet': None})
        sage: model.solve_dynamic_equations()
        NewtonianPointParticlesModel with 1 point particle(s)
        sage: model.dynamic_equations_solutions_
        {'bullet': [_K2*t + _K1, _K2*t + _K1, _K2*t + _K1]}
    """

    def __init__(self, F_external: ExternalForces = None, F_internal: InternalForces = None) -> None:
        """ """
        self.F_external = F_external
        self.F_internal = F_internal

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.particles_labels_)} point particle(s)"

    @property
    def particles_labels_(self):
        labels_ext = set()
        labels_int = set()
        if self.F_external is not None:
            labels_ext = self.F_external.keys()
        if self.F_internal is not None:
            labels_int = {label for pair in self.F_internal.keys() for label in pair}
        assert labels_int.issubset(
            labels_ext
        ), f"The particles with labels {labels_int.difference(labels_ext)} should be defined in the external forces."
        return labels_ext

    @property
    def dynamic_equations_(self):
        des = {}
        t = var("t")
        coords = [function(coord)(t) for coord in ("x", "y", "z")]
        for label, F_ext_vect in self.F_external.items():
            if F_ext_vect is None:
                F_ext_vect = zero_vector(3)
            m = var(f"m_{label}")
            assume(m > 0)
            des[label] = []
            for ind, F in enumerate(F_ext_vect):
                des[label].append(m * diff(coords[ind], t, 2) == F)
        return des

    def solve_dynamic_equations(self, initial_conditions=None, solver=None):
        self.dynamic_equations_solutions_ = {}
        t = var("t")
        coords = [function(coord)(t) for coord in ("x", "y", "z")]
        for label, des in self.dynamic_equations_.items():
            self.dynamic_equations_solutions_[label] = []
            for ind, de in enumerate(des):
                self.dynamic_equations_solutions_[label].append(
                    desolve(de, dvar=coords[ind], ivar=t, ics=initial_conditions)
                )
        return self

    def set_frame_reference(self):
        return self
