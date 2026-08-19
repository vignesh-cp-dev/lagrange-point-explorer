"""Lightweight circular restricted three-body problem helpers.

The system inputs use SI units.  Lagrange points and satellite states use the
usual normalized rotating barycentric frame: separation is one, total mass is
one, and the angular velocity is one.
"""

from dataclasses import dataclass

import numpy as np


G = 6.67430e-11  # m^3 kg^-1 s^-2
_L4_L5_STABILITY_LIMIT = (1.0 - np.sqrt(69.0) / 9.0) / 2.0


@dataclass(frozen=True)
class TwoBodySystem:
	"""Two bodies separated by ``separation`` metres."""

	primary_mass: float
	secondary_mass: float
	separation: float

	def __post_init__(self) -> None:
		if self.primary_mass <= 0 or self.secondary_mass <= 0:
			raise ValueError("masses must be positive")
		if self.separation <= 0:
			raise ValueError("separation must be positive")


def calculate_mu(system: TwoBodySystem) -> float:
	"""Return the dimensionless secondary mass ratio, mu = m2 / (m1 + m2)."""

	return system.secondary_mass / (system.primary_mass + system.secondary_mass)


def calculate_barycenter(system: TwoBodySystem) -> float:
	"""Return the barycenter's SI distance from the primary, in metres."""

	return system.separation * calculate_mu(system)


def _collinear_equation(x: float, mu: float) -> float:
	"""Derivative of the normalized effective potential along the x-axis."""

	primary_distance = abs(x + mu)
	secondary_distance = abs(x - (1.0 - mu))
	return (
		x
		- (1.0 - mu) * (x + mu) / primary_distance**3
		- mu * (x - (1.0 - mu)) / secondary_distance**3
	)


def _bisect_root(left: float, right: float, mu: float) -> float:
	"""Find a sign-changing root without stepping across a primary."""

	f_left = _collinear_equation(left, mu)
	f_right = _collinear_equation(right, mu)
	if f_left * f_right > 0:
		raise RuntimeError("could not bracket a collinear Lagrange point")

	for _ in range(100):
		midpoint = 0.5 * (left + right)
		f_midpoint = _collinear_equation(midpoint, mu)
		if abs(f_midpoint) < 1e-13 or abs(right - left) < 1e-13:
			return midpoint
		if f_left * f_midpoint <= 0:
			right, f_right = midpoint, f_midpoint
		else:
			left, f_left = midpoint, f_midpoint
	return 0.5 * (left + right)


def calculate_lagrange_points(system: TwoBodySystem) -> dict[str, np.ndarray]:
	"""Return all five points in normalized rotating barycentric coordinates."""

	mu = calculate_mu(system)
	primary_x = -mu
	secondary_x = 1.0 - mu
	epsilon = 1e-8

	# Each interval contains one collinear equilibrium and excludes a primary.
	l1 = _bisect_root(primary_x + epsilon, secondary_x - epsilon, mu)
	l2 = _bisect_root(secondary_x + epsilon, secondary_x + 2.0, mu)
	l3 = _bisect_root(-2.0, primary_x - epsilon, mu)
	triangle_height = np.sqrt(3.0) / 2.0
	triangle_x = 0.5 - mu

	return {
		"L1": np.array([l1, 0.0]),
		"L2": np.array([l2, 0.0]),
		"L3": np.array([l3, 0.0]),
		"L4": np.array([triangle_x, triangle_height]),
		"L5": np.array([triangle_x, -triangle_height]),
	}


def cr3bp_acceleration(state: np.ndarray, mu: float) -> np.ndarray:
	"""Return ``[ax, ay]`` for a normalized rotating-frame state.

	The Coriolis terms depend on velocity, so this is the acceleration part of
	the first-order ODE used by the RK4 integrator below.
	"""

	x, y, vx, vy = np.asarray(state, dtype=float)
	primary_distance = np.hypot(x + mu, y)
	secondary_distance = np.hypot(x - (1.0 - mu), y)
	if min(primary_distance, secondary_distance) == 0.0:
		raise ValueError("satellite state cannot be at a primary")

	ax = (
		x
		+ 2.0 * vy
		- (1.0 - mu) * (x + mu) / primary_distance**3
		- mu * (x - (1.0 - mu)) / secondary_distance**3
	)
	ay = (
		y
		- 2.0 * vx
		- (1.0 - mu) * y / primary_distance**3
		- mu * y / secondary_distance**3
	)
	return np.array([ax, ay])


def _state_derivative(state: np.ndarray, mu: float) -> np.ndarray:
	return np.concatenate((state[2:], cr3bp_acceleration(state, mu)))


def _rk4_step(state: np.ndarray, step: float, mu: float) -> np.ndarray:
	k1 = _state_derivative(state, mu)
	k2 = _state_derivative(state + 0.5 * step * k1, mu)
	k3 = _state_derivative(state + 0.5 * step * k2, mu)
	k4 = _state_derivative(state + step * k3, mu)
	return state + step * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0


def simulate_satellite(
	system: TwoBodySystem,
	initial_position: np.ndarray,
	initial_velocity: np.ndarray,
	duration: float,
	dt: float,
) -> np.ndarray:
	"""Integrate a massless satellite in normalized rotating-frame time.

	``initial_position`` and ``initial_velocity`` are normalized rotating-frame
	values. ``duration`` and ``dt`` are normalized time units; one unit equals
	``sqrt(separation**3 / (G * total_mass))`` seconds.
	"""

	if duration < 0 or dt <= 0:
		raise ValueError("duration must be non-negative and dt must be positive")
	state = np.concatenate(
		(np.asarray(initial_position, dtype=float), np.asarray(initial_velocity, dtype=float))
	)
	if state.shape != (4,):
		raise ValueError("initial position and velocity must each have shape (2,)")

	steps = int(np.ceil(duration / dt))
	trajectory = np.empty((steps + 1, 4), dtype=float)
	trajectory[0] = state
	mu = calculate_mu(system)
	for index in range(steps):
		step = min(dt, duration - index * dt)
		state = _rk4_step(state, step, mu)
		trajectory[index + 1] = state
	return trajectory


# Useful for quick local experiments; functions remain general for any system.
EARTH_MOON = TwoBodySystem(
	primary_mass=5.97219e24,
	secondary_mass=7.342e22,
	separation=3.844e8,
)


def classify_lagrange_points(system: TwoBodySystem) -> dict[str, str]:
	"""Classify collinear points as unstable and triangular points when stable."""

	triangular_stability = calculate_mu(system) < _L4_L5_STABILITY_LIMIT
	triangular_label = "stable" if triangular_stability else "unstable"
	return {"L1": "unstable", "L2": "unstable", "L3": "unstable", "L4": triangular_label, "L5": triangular_label}
