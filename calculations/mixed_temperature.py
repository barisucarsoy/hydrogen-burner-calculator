import cantera as ct
from dataclasses import dataclass

from calculations.jet_burner import JetBurner as jb
from calculations.pilot_burner import PilotBurner as pb
from calculations.n2_co_flow import CoFlow as cf


@dataclass
class MixingResults:
    # Input mass flows
    jet_mass_flow: float
    pilot_mass_flow: float
    coflow_mass_flow: float
    total_mass_flow: float

    # Mixed state
    mixed_temp: float
    mixed_enthalpy: float
    mixed_cp: float
    species_mass_fracs: dict
    mixed_velocity: float

    def print_properties(self):
        max_length = max(len(field) for field in self.__dataclass_fields__)  # type: ignore
        for field in self.__dataclass_fields__:  # type: ignore
            value = getattr(self, field)
            if isinstance(value, (int, float)):
                print(f"{field:{max_length}}: {value:.5e}")
            else:
                print(f"{field:{max_length}}: {value}")


class MixedTemperature:

    def __init__(self, geometry, operating):
        self.geom = geometry
        self.op = operating

        self.jet = jb(geometry, operating)
        self.pilot = pb(geometry, operating)
        self.coflow = cf(geometry, operating)

    def calculate_mixed_temperature(self):
        """Calculate mixed temperature and enthalpy"""
        jet_results = self.jet.get_jet_burner_properties()
        pilot_results = self.pilot.get_pilot_burner_properties()
        coflow_results = self.coflow.calculate_flows()

        # Get mass flows
        jet_mass_flow = jet_results.mass_flow_total
        pilot_mass_flow = pilot_results.mass_flow_total
        coflow_mass_flow = coflow_results.mass_flow
        total_mass_flow = jet_mass_flow + pilot_mass_flow + coflow_mass_flow

        # Get enthalpies
        jet_h = jet_results.flame_enthalpy_mass
        pilot_h = pilot_results.flame_enthalpy_mass
        coflow_h = coflow_results.enthalpy

        # Mass fractions for the mixed state
        Y_jet = jet_mass_flow / total_mass_flow
        Y_pilot = pilot_mass_flow / total_mass_flow
        Y_coflow = coflow_mass_flow / total_mass_flow

        # Mass weighted mixing of enthalpies
        h_mix = Y_jet * jet_h + Y_pilot * pilot_h + Y_coflow * coflow_h

        # Set mixture state with corrected N2 coflow
        mix = ct.Solution('gri30.yaml')

        mix.HPY = h_mix, self.op.jet_pressure, {
            'H2': 0.0,  # Fully reacted
            'O2': 0.21 * (Y_jet + Y_pilot),  # From jet and pilot
            'N2': Y_jet * 0.79 + Y_pilot * 0.79 + Y_coflow * 1.0,  # Include pure N2 coflow
            'H2O': (Y_jet + Y_pilot) * 0.21  # Combustion products
        }

        return MixingResults(
            jet_mass_flow=jet_mass_flow,
            pilot_mass_flow=pilot_mass_flow,
            coflow_mass_flow=coflow_mass_flow,
            total_mass_flow=total_mass_flow,
            mixed_temp=mix.T,
            mixed_enthalpy=mix.h,
            mixed_cp=mix.cp,
            species_mass_fracs=None,
            mixed_velocity=None
        )

    def get_mixed_properties(self):
        """Get mixed properties"""
        return self.calculate_mixed_temperature()


if __name__ == '__main__':
    from input_parameters import parameters

    geometry = parameters.GeometryParams()
    operating = parameters.OperatingParams()

    mixed_temp = MixedTemperature(geometry, operating)
    results = mixed_temp.get_mixed_properties()
    results.print_properties()
    print('check this file')
