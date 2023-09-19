"""Classical mechanics functionality."""

from ._newtonian import NewtonianPointParticlesModel, check_force_vector, check_particles_labels

__all__: list[str] = ['NewtonianPointParticlesModel', 'check_force_vector', 'check_particles_labels']
