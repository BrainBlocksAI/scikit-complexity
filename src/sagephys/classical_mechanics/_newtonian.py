r"""
Newtonian mechanics models.

This module implements the :class:`NewtonianPointParticlesModel` and
:class:`NewtonianRigidBodiesModel` classes which can be used to define
and solve the dynamical equations of Netwonian models.
"""

from sage.all import *
from sage.symbolic.expression import Expression

ExternalForces = dict[str, dict[str, Expression] | None] | None
InternalForces = dict[tuple[str, str], dict[str, Expression] | None] | None


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

    Motion with constant acceleration::

        sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
        sage: F = var('F')
        sage: model = NewtonianPointParticlesModel(F_external={None: vector([F, 0, 0])})
        sage: model.solve_dynamic_equations()
        NewtonianPointParticlesModel with 1 point particle(s)
        sage: model.dynamic_equations_solutions_
        {'particle': [_K2*t + 1/2*F*t^2/m + _K1, _K2*t + _K1, _K2*t + _K1]}

    One-dimensional harmonic oscilator::

        sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
        sage: k, x = var('k x')
        sage: assume(k > 0)
        sage: model = NewtonianPointParticlesModel(F_external={'bullet': vector([-k * x, 0, 0])})
        sage: model.solve_dynamic_equations()
        NewtonianPointParticlesModel with 1 point particle(s)
        sage: model.dynamic_equations_solutions_
        {'bullet': [_K2*cos(sqrt(k)*t/sqrt(m_bullet)) + _K1*sin(sqrt(k)*t/sqrt(m_bullet)), _K2*t + _K1, _K2*t + _K1]}
    """

    def __init__(self, F_external: ExternalForces = None, F_internal: InternalForces = None) -> None:
        """ """
        self.F_external = F_external
        self.F_internal = F_internal

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} with {len(self.particles_labels_)} point particle(s)"

    @property
    def particles_labels_(self):
        r"""
        The particle labels.

        TESTS::

        Correct labels::

            sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
            sage: model = NewtonianPointParticlesModel(F_external={'bullet': None, 'box': None})
            sage: model.particles_labels_
            ['bullet', 'box']

        External forces does not include a label::

            sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
            sage: model = NewtonianPointParticlesModel(F_external={'bullet': None, 'box': None}, F_internal={('bullet', 'sphere'): None})
            sage: model.particles_labels_
            Traceback (most recent call last):
            ...
            AssertionError: The particle(s) with label(s) `sphere` included only in the internal and not in the external forces.

        A label is missing::
            sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
            sage: model = NewtonianPointParticlesModel(F_external={None: vector([0, 0, 0]), 'box': None})
            sage: model.particles_labels_
            ['particle', 'box']

        A label is the reserved label `particle`::
            sage: from sagephys.classical_mechanics import NewtonianPointParticlesModel
            sage: model = NewtonianPointParticlesModel(F_external={'particle': None, 'box': None})
            sage: model.particles_labels_
            Traceback (most recent call last):
            ...
            ValueError: Label `particle` is a reserved label. Please select another label.
        """
        labels_external = set()
        labels_internal = set()
        if self.F_external is not None and self.F_internal is not None:
            labels_external = self.F_external.keys()
            labels_internal = {label for pair in self.F_internal.keys() for label in pair}
        labels_extra = ", ".join({f"`{label}`" for label in labels_internal.difference(labels_external)})
        assert labels_internal.issubset(
            labels_external
        ), f"The particle(s) with label(s) {labels_extra} included only in the internal and not in the external forces."
        for label in self.F_external.keys():
            if label == "particle":
                raise ValueError("Label `particle` is a reserved label. Please select another label.")
        labels = [(label if label else "particle") for label in self.F_external.keys()]
        return labels

    @staticmethod
    def _check_force(F_vect):
        t = var("t")
        if F_vect is None:
            return zero_vector(3)
        F_vect_norm = []
        for F in F_vect:
            if isinstance(F, Expression):
                for var_name in ("x", "y", "z", "x0", "y0", "z0", "x1", "y1", "z1"):
                    _ = var(var_name)
                    F = F(**{var_name: function(var_name)(t)})
            F_vect_norm.append(F)
        return F_vect_norm

    @property
    def dynamic_equations_(self):
        des = {}
        t = var("t")
        coords = [function(coord)(t) for coord in ("x", "y", "z")]
        for label, F_ext_vect in self.F_external.items():
            label = label if label else "particle"
            F_ext_vect = self._check_force(F_ext_vect)
            m = var(f"m_{label}" if label and label != "particle" else "m")
            assume(m > 0)
            des[label] = []
            for ind, F_ext in enumerate(F_ext_vect):
                des[label].append(m * diff(coords[ind], t, 2) == F_ext)
        return des

    def solve_dynamic_equations(self, initial_conditions=None, solver=None):
        self.dynamic_equations_solutions_ = {}
        t = var("t")
        coords = [function(coord)(t) for coord in ("x", "y", "z")]
        for label, des in self.dynamic_equations_.items():
            self.dynamic_equations_solutions_[label] = []
            for ind, de in enumerate(des):
                if initial_conditions is not None:
                    initial_conditions = initial_conditions[label][ind]
                self.dynamic_equations_solutions_[label].append(
                    desolve(de, dvar=coords[ind], ivar=t, ics=initial_conditions)
                )
        return self

    def set_frame_reference(self):
        return self
