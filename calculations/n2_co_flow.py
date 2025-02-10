from dataclasses import dataclass
import numpy as np
import cantera as ct


@dataclass
class CoFlowResults:
    """Results container for N2 co-flow calculations"""
    # Mass flow rate
    mass_flow: float

    # Volume flow rate
    volume_flow: float

    # Standard volume flow rate
    std_volume_flow: float

    # Reynolds number
    Re: float

    # Enthalpy
    enthalpy: float

    # Density
    density: float

    # Dynamic viscosity
    dynamic_viscosity: float

    def print_properties(self):
        max_length = max(len(field) for field in self.__dataclass_fields__)  # type: ignore
        for field in self.__dataclass_fields__:  # type: ignore
            value = getattr(self, field)
            if isinstance(value, (int, float)):
                print(f"{field:{max_length}}: {value:.5e}")
            else:
                print(f"{field:{max_length}}: {value}")


class CoFlow:
    """N2 co-flow calculator"""

    def __init__(self, geometry, operating):
        self.geom = geometry
        self.op = operating

        # Store geometry parameters
        self.coflow_ID = self.geom.coflow_ID
        self.coflow_OD = self.geom.coflow_OD

        # Store operating parameters
        self.pressure = self.op.coflow_pressure
        self.temperature = self.op.coflow_temperature
        self.inlet_velocity = self.op.coflow_velocity

    def calculate_flows(self):
        """Calculate N2 co-flow properties"""
        # Initialize N2 gas phase
        N2 = ct.Solution('gri30.yaml')
        N2.TPX = self.temperature, self.pressure, 'N2:1.0'

        # Calculate areas
        inlet_area = np.pi / 4 * (self.coflow_OD ** 2 - self.coflow_ID ** 2)

        # Calculate mass flow
        mass_flow = self.inlet_velocity * inlet_area * N2.density

        # Calculate volume flow
        volume_flow = mass_flow / N2.density

        # Standard conditions (1 atm, 273.15 K)
        N2_std = ct.Solution('gri30.yaml')
        N2_std.TPX = 273.15 + 0, ct.one_atm, 'N2:1.0'

        # Standard volume flow
        std_volume_flow = mass_flow / N2_std.density

        # Calculate Reynolds number
        Re = self.inlet_velocity * (self.coflow_OD - self.coflow_ID) * N2.density / N2.viscosity

        # Calculate enthalpy
        enthalpy = N2.enthalpy_mass

        # Calculate dynamic viscosity
        dynamic_viscosity = N2.viscosity

        return CoFlowResults(
            mass_flow=mass_flow,
            volume_flow=volume_flow,
            std_volume_flow=std_volume_flow,
            Re=Re,
            enthalpy=enthalpy,
            density=N2.density,
            dynamic_viscosity=dynamic_viscosity
        )

    def get_co_flow_properties(self):
        """Get N2 co-flow results"""
        flow_results = self.calculate_flows()
        return flow_results
