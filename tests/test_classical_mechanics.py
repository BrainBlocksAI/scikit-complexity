"""Test the classical mechanics module."""

import re

import pytest
from sage.all import Rational, assume, cos, function, sin, sqrt, var, vector
from sagephys.classical_mechanics import NewtonianPointParticlesModel, check_force_vector, check_particles_labels


def test_check_particles_labels_default():
    """Test default particle label when no particles are provided."""
    assert check_particles_labels(None) == ['particle']


def test_check_particles_labels_wrong():
    """Test raise of error when wrong label of is provided."""
    m, g = var('m g')
    with pytest.raises(ValueError, match='Wrong variable name'):
        check_particles_labels({'body': {'weight': [0, -m * g, 0]}})


def test_particles_labels():
    """Test the particles labels."""
    m_body, g, k, x_particle1, b, v_x_particle2 = var('m_body g k x_particle1 b v_x_particle2')
    forces = {
        'body': {'weight': [0, -m_body * g, 0]},
        'particle1': {'force': [-k * x_particle1, 0, 0]},
        'particle2': {'force': [-b * v_x_particle2, 0, 0]},
    }
    assert check_particles_labels(forces) == ['body', 'particle1', 'particle2']


def test_check_force_vector_not_list():
    """The the check of force vector when it is not a list."""
    F_vect = (0, 1, 0)
    with pytest.raises(TypeError, match=re.escape(f'Force vector {F_vect} is not a list.')):
        check_force_vector(F_vect)


def test_check_force_vector_three_elements():
    """The the check of force vector when it does not have three elements."""
    F_vect = [0, 1]
    with pytest.raises(
        TypeError,
        match=re.escape(f'Force vector {F_vect} is a list but does not have three elements.'),
    ):
        check_force_vector(F_vect)


def test_check_force_vector():
    """The the check of force vector."""
    m_body, g, k, x_body, t = var('m_body g k x_body t')
    F_vect = [m_body * g, -k * x_body, 0]
    assert check_force_vector(F_vect) == vector([m_body * g, -k * function('x_body')(t), 0])


def test_forces_attr_no_labels():
    """The the forces attribute when no particles are provided."""
    model = NewtonianPointParticlesModel()
    assert model.forces_ == {'particle': {}}


def test_forces_attr():
    """The the forces attribute."""
    m_body, g, k, x_particle1, b, v_x_particle2 = var('m_body g k x_particle1 b v_x_particle12')
    forces = {
        'body': {'weight': [0, -m_body * g, 0]},
        'particle1': {'force': [-k * x_particle1, 0, 0]},
        'particle2': {'force': [-b * v_x_particle2, 0, 0]},
    }
    model = NewtonianPointParticlesModel(forces=forces)
    assert model.forces_ == forces


def test_forces_attr_implied_label():
    """The the forces attribute when label is implied."""
    x_particle1 = var('x_particle1')
    forces = {'body': {'internal': [-x_particle1, 0, 0]}}
    model = NewtonianPointParticlesModel(forces=forces)
    assert model.forces_ == {**forces, 'particle1': {}}


def test_motion_with_constant_velocity():
    """Test the solution of dynamic equations of a free particle."""
    t, _K1, _K2 = var('t _K1 _K2')
    model = NewtonianPointParticlesModel()
    model.analyze()
    solutions = model.solve()
    assert solutions['particle'][0].match(_K2 * t + _K1) is not None
    assert solutions['particle'][1].match(_K2 * t + _K1) is not None
    assert solutions['particle'][2].match(_K2 * t + _K1) is not None


def test_motion_with_constant_acceleration():
    """Test the solution of dynamic equations under constant external force."""
    t, _K1, _K2, F, m_particle = var('t _K1 _K2 F m_particle')
    model = NewtonianPointParticlesModel(forces={'particle': {'constant': [F, 0, 0]}})
    model.analyze()
    solutions = model.solve()
    assert solutions['particle'][0].match(_K2 * t + Rational(1 / 2) * F * t**2 / m_particle + _K1) is not None
    assert solutions['particle'][1].match(_K2 * t + _K1) is not None
    assert solutions['particle'][2].match(_K2 * t + _K1) is not None


def test_motion_one_dimensional_harmonic_oscillator():
    """Test the solution of dynamic equations of harmonic oscillator."""
    t, _K1, _K2, k, x_sphere, m_sphere = var('t _K1 _K2 k x_sphere m_sphere')
    assume(k > 0)
    model = NewtonianPointParticlesModel(forces={'sphere': {'elastic': [-k * x_sphere, 0, 0]}})
    model.analyze()
    solutions = model.solve()
    assert (
        solutions['sphere'][0].match(
            _K2 * cos(sqrt(k) * t / sqrt(m_sphere)) + _K1 * sin(sqrt(k) * t / sqrt(m_sphere)),
        )
        is not None
    )
    assert solutions['sphere'][1].match(_K2 * t + _K1) is not None
    assert solutions['sphere'][2].match(_K2 * t + _K1) is not None
