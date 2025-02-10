import cantera as ct
import numpy as np
from dataclasses import dataclass


@dataclass
class JetBurnerProperties:
    """Storage class for central jet burner properties"""

    # Unburnt mixture properties
    # Mass flows
    mass_flow_total: float
    mass_flow_h2: float
    mass_flow_air: float

    # Real volumetric flows
    vol_flow_real_total: float

    # Standard volumetric flows at 15°C and 1 atm
    vol_flow_std_total: float
    vol_flow_std_h2: float
    vol_flow_std_air: float

    # Real densities at operating conditions
    rho_mix: float
    rho_h2: float
    rho_air: float

    # Relevant dimensionless numbers of the mixture
    reynolds_number: float
    lewis_number: float
    karlovitz_number: float

    # laminar_flame_speed: float
    # turbulent_intensity: float

    # Flame properties
    flame_density: float
    flame_temperature: float
    flame_enthalpy_mass: float
    flame_enthalpy_mole: float
    flame_power: float

    # Geometric properties
    flow_area: float

    def print_properties(self):
        max_length = max(len(field) for field in self.__dataclass_fields__)  # type: ignore
        for field in self.__dataclass_fields__:  # type: ignore
            value = getattr(self, field)
            if isinstance(value, (int, float)):
                print(f"{field:{max_length}}: {value:.5e}")
            else:
                print(f"{field:{max_length}}: {value}")


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

    def calculate_flows(self):
        """Calculate flow properties including standard flows"""

        # Initialize Cantera objects
        gas = ct.Solution('gri30.yaml')
        gas.TP = self.temperature, self.pressure
        gas.set_equivalence_ratio(self.phi, 'H2', 'O2:1.0, N2:3.76')
        mixture_density = gas.density_mass

        # Store species indices for later use
        h2_idx = gas.species_index('H2')
        o2_idx = gas.species_index('O2')
        n2_idx = gas.species_index('N2')

        Y_h2 = gas.Y[h2_idx]
        Y_o2 = gas.Y[o2_idx]
        Y_n2 = gas.Y[n2_idx]

        # Calculate mass flows
        mass_flow_total = self.velocity * self.flow_area * mixture_density
        mass_flow_h2 = mass_flow_total * Y_h2
        mass_flow_air = mass_flow_total * (Y_o2 + Y_n2)

        # Calculate Real volumetric flow
        vol_flow_real_total = mass_flow_total / mixture_density

        # Calculate Real densities at operating conditions
        gas_h2 = ct.Solution('gri30.yaml')
        gas_h2.TPX = self.temperature, self.pressure, 'H2:1.0'
        rho_h2 = gas_h2.density_mass

        gas_air = ct.Solution('gri30.yaml')
        gas_air.TPX = self.temperature, self.pressure, 'O2:0.21, N2:0.79'
        rho_air = gas_air.density_mass

        # Calculate Standard volumetric flows at 15°C and 1 atm
        gas_std_air = ct.Solution('gri30.yaml')
        gas_std_air.TPX = 273.15 + 0, ct.one_atm, 'O2:0.21, N2:0.79'
        std_density_air = gas_std_air.density_mass

        gas_std_h2 = ct.Solution('gri30.yaml')
        gas_std_h2.TPX = 273.15 + 0, ct.one_atm, 'H2:1.0'
        std_density_h2 = gas_std_h2.density_mass

        vol_flow_std_h2 = mass_flow_h2 / std_density_h2
        vol_flow_std_air = mass_flow_air / std_density_air
        vol_flow_std_total = vol_flow_std_h2 + vol_flow_std_air

        # Dimensionless numbers
        reynolds_number = self.velocity * self.pipe_ID * mixture_density / gas.viscosity

        thermal_diff = (gas.thermal_conductivity / (mixture_density * gas.cp_mass))
        mass_diff = gas.mix_diff_coeffs[h2_idx]
        lewis_number = thermal_diff / mass_diff

        # Karlovitz number
        u_prime = 0.1 * self.velocity  # Assuming 10% turbulence intensity
        l_0 = self.pipe_ID # Integral length scale
        l_f = 0.5e-3  # Thermal thickness (approximate)

        # Estimate laminar flame speed
        sl_1atm = 0.24  # m/s at 1 atm reference
        sl = sl_1atm * (self.pressure / ct.one_atm) ** (-0.5)  # Pressure scaling

        karlovitz_number = (u_prime / sl) ** (3 / 2) * (l_f / l_0) ** (1 / 2)

        return {
            'flow_area': self.flow_area,
            'rho_mix': mixture_density,
            'rho_h2': rho_h2,
            'rho_air': rho_air,
            'mass_flow_total': mass_flow_total,
            'mass_flow_h2': mass_flow_h2,
            'mass_flow_air': mass_flow_air,
            'vol_flow_real_total': vol_flow_real_total,
            'vol_flow_std_total': vol_flow_std_total,
            'vol_flow_std_h2': vol_flow_std_h2,
            'vol_flow_std_air': vol_flow_std_air,
            'reynolds_number': reynolds_number,
            'lewis_number': lewis_number,
            'karlovitz_number': karlovitz_number,

        }

    def calculate_flame_properties(self, mass_flow_h2):
        # Initialize Cantera objects
        flame = ct.Solution('gri30.yaml')
        flame.TP = self.temperature, self.pressure
        flame.set_equivalence_ratio(self.phi, 'H2', 'O2:1.0, N2:3.76')

        # Calculate equilibrium
        flame.equilibrate('HP')

        flame_density = flame.density_mass
        flame_temperature = flame.T
        flame_enthalpy_mass = flame.enthalpy_mass
        flame_enthalpy_mole = flame.enthalpy_mole

        # Calculate power output
        LHV_H2 = 120.1e6  # Lower heating value of H2 [J/kg]
        flame_power = mass_flow_h2 * LHV_H2

        return {
            'flame_density': flame_density,
            'flame_temperature': flame_temperature,
            'flame_enthalpy_mass': flame_enthalpy_mass,
            'flame_enthalpy_mole': flame_enthalpy_mole,
            'flame_power': flame_power,
        }

    def get_jet_burner_properties(self):
        flows = self.calculate_flows()
        flame_properties = self.calculate_flame_properties(mass_flow_h2=flows['mass_flow_h2'])

        combined_properties = {**flows, **flame_properties, 'flow_area': self.flow_area}
        return JetBurnerProperties(**combined_properties)
