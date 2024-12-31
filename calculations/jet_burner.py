import cantera as ct
import numpy as np
from dataclasses import dataclass


@dataclass
class JetBurnerProperties:
    """Storage class for central jet burner properties"""

    # Unburnt mixture properties
    # Mass flows
    mass_flow_h2: float
    mass_flow_air: float
    mass_flow_total: float

    # Real volumetric flows
    vol_flow_real_h2: float
    vol_flow_real_air: float
    vol_flow_real_total: float

    # Standard volumetric flows at 15°C and 1 atm
    vol_flow_std_h2: float
    vol_flow_std_air: float
    vol_flow_std_total: float

    # Real densities at operating conditions
    rho_h2: float
    rho_air: float
    rho_total: float

    # Relevant dimensionless numbers of the mixture
    reynolds: float
    lewis: float
    karlovitz: float

    # laminar_flame_speed: float
    # turbulent_intensity: float

    # Flame properties
    flame_density: float
    flame_temperature: float
    flame_enthalpy: float
    flame_power: float

    # Geometric properties
    flow_area: float


class JetBurner:
    def __init__(self, geometry, operating):
        """Initialize central jet calculations.

        Args:
            geometry: Geometry parameters containing jet dimensions
            operating: Operating parameters containing flow conditions
        """
        # Store geometry parameters
        self.pipe_ID = geometry.jet_ID  # Inner diameter of the jet pipe
        self.flow_area = np.pi * (self.pipe_ID / 2) ** 2  # Flow area of the jet pipe

        # Store operating parameters
        self.phi = operating.jet_equivalence_ratio  # Target equivalence ratio of the jet flame
        self.pressure = operating.jet_pressure
        self.temperature = operating.jet_temperature
        self.velocity = operating.jet_velocity

        # Initialize Cantera objects
        self.gas = ct.Solution('gri30.yaml')
        self.gas.TPX = self.temperature, self.pressure
        self.gas.set_equivalence_ratio(self.phi, 'H2:1.0', 'O2:1.0, N2:3.76')
        self.mixture_density = self.gas.density

    def calculate_flows(self):
        """Calculate flow properties including standard flows"""
        # Calculate mass flows
        mass_flow_total = self.velocity * self.flow_area * self.mixture_density

        return {
            'flow_area': self.flow_area,
            'mass_flow_total': mass_flow_total,

        }

    def calculate_flame_properties(self):
        return {
            'flame_density': None,
            'flame_temperature': None,
            'flame_enthalpy': None,
            'flame_power': None,
        }

    def calculate_dimensionless_numbers(self):
        return {
            'reynolds': None,
            'lewis': None,
            'karlovitz': None,
        }

    def get_jet_burner_properties(self):
        flows = self.calculate_flows()
        flame_properties = self.calculate_flame_properties()
        dimensionless_numbers = self.calculate_dimensionless_numbers()

        combined_properties = {**flows, **flame_properties, **dimensionless_numbers, 'flow_area': self.flow_area}
        return JetBurnerProperties(**combined_properties)
