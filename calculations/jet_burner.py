import cantera as ct
import numpy as np
from dataclasses import dataclass


@dataclass
class JetBurnerProperties:
    """Storage class for central jet burner properties"""

    # Unburnt mixture properties
    # Mass flows
    mass_flow_h2:    float
    mass_flow_air:   float
    mass_flow_total: float

    # Real volumetric flows
    vol_flow_real_h2:    float
    vol_flow_real_air:   float
    vol_flow_real_total: float

    # Standard volumetric flows at 15°C and 1 atm
    vol_flow_std_h2:    float
    vol_flow_std_air:   float
    vol_flow_std_total: float

    # Real densities at operating conditions
    rho_h2:    float
    rho_air:   float
    rho_total: float

    # Relevant physical constants of the mixture
    reynolds:  float
    lewis:     float
    karlovitz: float

    # laminar_flame_speed: float
    # turbulent_intensity: float

    # Flame properties
    flame_density:     float
    flame_temperature: float
    flame_enthalpy:    float
    flame_power:       float

    # Geometric properties
    flow_area: float
