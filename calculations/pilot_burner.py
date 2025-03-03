import cantera as ct
import numpy as np
from dataclasses import dataclass
from geometry.plate_generator import plate_generator
from geometry.honeycomb_generator import honeycomb_generator


@dataclass
class PilotBurnerProperties:
    """Storage class for central jet burner properties"""

    # Unburnt mixture properties
    # Mass flows
    mass_flow_total: float
    mass_flow_h2: float
    mass_flow_air: float

    # Real volumetric flows
    vol_flow_real_total: float
    vol_flow_real_h2: float
    vol_flow_real_air: float

    # Standard volumetric flows at 15°C and 1 atm
    vol_flow_std_total: float
    vol_flow_std_h2: float
    vol_flow_std_air: float

    # Real densities at operating conditions
    rho_h2: float
    rho_air: float
    rho_mix: float

    mixed_velocity: float

    # Relevant dimensionless numbers of the mixture
    reynolds_number_h2: float
    reynolds_number_air: float

    # laminar_flame_speed: float
    # turbulent_intensity: float

    # Flame properties
    flame_density: float
    flame_temperature: float
    flame_enthalpy_mass: float
    flame_enthalpy_mole: float
    flame_power: float
    OF_ratio: float
    equivalence_ratio: float

    # Geometric properties
    flow_area_air: float
    flow_area_fuel: float

    def print_properties(self):
        max_length = max(len(field) for field in self.__dataclass_fields__)  # type: ignore
        for field in self.__dataclass_fields__:  # type: ignore
            value = getattr(self, field)
            if isinstance(value, (int, float)):
                print(f"{field:{max_length}}: {value:.5e}")
            else:
                print(f"{field:{max_length}}: {value}")


class PilotBurner:
    def __init__(self, geometry, operating):
        # Store geometry parameters
        self.pilot_fuel_ID = geometry.pilot_fuel_ID
        self.pilot_fuel_OD = geometry.pilot_fuel_OD

        # Store operating parameters
        self.pilot_pressure = operating.pilot_pressure
        self.pilot_temperature = operating.pilot_temperature
        self.pilot_air_velocity = operating.pilot_air_velocity
        self.pilot_fuel_velocity = operating.pilot_fuel_velocity

        self.hencken_OD = geometry.pilot_burner_ID
        self.hencken_ID = geometry.jet_OD

        # Area of the mixed pilot
        self.hencken_area = (np.pi * (self.hencken_OD / 2) ** 2) - (np.pi * (self.hencken_ID / 2) ** 2)


    def calculate_mass_flows(self):
        """Calculate mass flows of the pilot burner"""
        # Initialize gas phases
        air = ct.Solution('gri30.yaml')
        air.TPX = self.pilot_temperature, self.pilot_pressure, 'O2:0.21, N2:0.79'

        h2 = ct.Solution('gri30.yaml')
        h2.TPX = self.pilot_temperature, self.pilot_pressure, 'H2:1.0'

        # Calculate mass flows
        mass_flow_air = self.pilot_air_velocity * self.air_hole_area * air.density
        mass_flow_h2 = self.pilot_fuel_velocity * self.fuel_hole_area * h2.density
        mass_flow_total = mass_flow_air + mass_flow_h2

        # Real volume flows
        air_volume_flow = mass_flow_air / air.density
        fuel_volume_flow = mass_flow_h2 / h2.density
        vol_flow_real_total = air_volume_flow + fuel_volume_flow

        # Standard conditions (1 atm, 273.15 K)
        air_std = ct.Solution('gri30.yaml')
        air_std.TPX = 273.15 + 0, ct.one_atm, 'O2:0.21, N2:0.79'

        h2_std = ct.Solution('gri30.yaml')
        h2_std.TPX = 273.15 + 0, ct.one_atm, 'H2:1.0'

        # Standard volume flows
        vol_flow_std_air = mass_flow_air / air_std.density
        vol_flow_std_h2 = mass_flow_h2 / h2_std.density
        vol_flow_std_total = vol_flow_std_air + vol_flow_std_h2

        # Dimensionless numbers
        reynolds_h2 = self.pilot_fuel_velocity * self.pilot_fuel_ID * h2.density / h2.viscosity
        reynolds_air = self.pilot_air_velocity * self.air_hole_area * air.density / air.viscosity

        # Mixed flow properties
        gas_mix = ct.Solution('gri30.yaml')
        gas_mix.TPX = self.pilot_temperature, self.pilot_pressure, 'H2:1.0, O2:1.0, N2:3.76'
        stoich_ratio = gas_mix.stoich_air_fuel_ratio('H2:1.0', 'O2:1.0, N2:3.76', basis='mass')
        phi = stoich_ratio / (mass_flow_air / mass_flow_h2)
        gas_mix.set_equivalence_ratio(phi, 'H2', 'O2:1.0, N2:3.76')

        rho_mix = gas_mix.density_mass
        mixed_velocity = mass_flow_total / self.hencken_area / rho_mix



        return {
            'flow_area_air': self.air_hole_area,
            'flow_area_fuel': self.fuel_hole_area,
            'rho_h2': h2.density,
            'rho_air': air.density,
            'mass_flow_total': mass_flow_total,
            'mass_flow_h2': mass_flow_h2,
            'mass_flow_air': mass_flow_air,
            'vol_flow_real_total': vol_flow_real_total,
            'vol_flow_real_h2': fuel_volume_flow,
            'vol_flow_real_air': air_volume_flow,
            'vol_flow_std_total': vol_flow_std_total,
            'vol_flow_std_h2': vol_flow_std_h2,
            'vol_flow_std_air': vol_flow_std_air,
            'reynolds_number_h2': reynolds_h2,
            'reynolds_number_air': reynolds_air,
            'mixed_velocity': mixed_velocity,
            'rho_mix': rho_mix
        }

    def calculate_flame_properties(self, mass_flow_h2, mass_flow_air):
        """Calculate flame properties including temperature and power output from the mass flows."""

        # Initialize Cantera objects
        gas = ct.Solution('gri30.yaml')
        # Calculate stoichiometric fuel-to-air ratio
        #gas.set_equivalence_ratio(1.0, 'H2', 'O2:1.0, N2:3.76')
        stoich_ratio = gas.stoich_air_fuel_ratio('H2:1.0', 'O2:1.0, N2:3.76', basis='mass')

        # Calculate equivalence ratio
        phi = stoich_ratio / (mass_flow_air / mass_flow_h2)

        # Set up flame mixture with calculated equivalence ratio
        flame = ct.Solution('gri30.yaml')
        flame.set_equivalence_ratio(phi, 'H2', 'O2:1.0, N2:3.76')
        flame.TP = self.pilot_temperature, self.pilot_pressure

        # Calculate equilibrium
        flame.equilibrate('HP')

        # Get flame properties
        flame_density = flame.density
        flame_temperature = flame.T
        flame_enthalpy_mass = flame.enthalpy_mass
        flame_enthalpy_mole = flame.enthalpy_mole

        LHV_H2 = 120.1e6  # Lower heating value of H2 [J/kg]
        flame_power = mass_flow_h2 * LHV_H2

        return {
            'flame_density': flame_density,
            'flame_temperature': flame_temperature,
            'flame_enthalpy_mass': flame_enthalpy_mass,
            'flame_enthalpy_mole': flame_enthalpy_mole,
            'flame_power': flame_power,
            'OF_ratio': mass_flow_air / mass_flow_h2,
            'equivalence_ratio': phi
        }

    def get_pilot_burner_properties(self, geometry_config):
        if geometry_config == 'Honeycomb':
            stats = honeycomb_generator(generate_dxf=False)
            print("Honeycomb Generator Output:", stats)
        elif geometry_config == 'Plate':
            stats = plate_generator(generate_dxf=False)
            print("Plate Generator Output:", stats)

        self.air_hole_number = stats['air_hole_number']
        self.air_hole_area = stats['air_hole_area']
        self.fuel_hole_number = stats['fuel_hole_number']
        self.fuel_hole_area = stats['fuel_hole_area']
        self.air_to_fuel_area_ratio = stats['air_to_fuel_area_ratio']

        flows = self.calculate_mass_flows()
        flame_properties = self.calculate_flame_properties(mass_flow_h2=flows['mass_flow_h2'],
                                                           mass_flow_air=flows['mass_flow_air'])
        combined_properties = {**flows, **flame_properties}
        return PilotBurnerProperties(**combined_properties)
