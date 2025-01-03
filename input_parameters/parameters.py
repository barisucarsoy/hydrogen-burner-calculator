import dataclasses


@dataclasses.dataclass
class GeometryParams:
    """
    Geometry parameters for the burner model.
    -All dimensions are in meters.
    -For hexagonal honeycomb pilot burner configuration (hex-mesh), the hexagonal cell is equal to the air tube ID.

    Attributes:
    ----------
    jet_ID: float
        Inner diameter of the central jet pipe
    jet_OD: float
        Outer diameter of the central jet pipe.
    pilot_fuel_ID: float
        Inner diameter of the pilot fuel pipe.
    pilot_fuel_OD: float
        Outer diameter of the pilot fuel pipe.
    pilot_air_ID: float
        Inner diameter of the pilot air pipe.
    pilot_burner_ID: float
        Inner diameter of the pilot burner.
        This marks the honeycomb wall boundary in hex-mesh config.
    pilot_burner_OD: float
        Outer diameter of the pilot burner.
    pilot_hex_cell_size: float
        Distance between two parallel faces in the hexagonal cell.
        Also, that means it is the apothem (r) times 2.
    pilot_hex_wall_th: float
        Wall thickness of the hexagonal cell.
    coflow_ID: float
        Inner diameter of the co-flow pipe.
    coflow_OD: float
        Outer diameter of the co-flow pipe.
    """

    # Central jet geometry
    jet_ID: float = 2.0e-3  # 2.0mm inner diameter
    jet_OD: float = 3.5e-3  # 3.5mm outer diameter

    # Pilot fuel-air geometry
    pilot_fuel_ID: float = 1.0e-3   # 1.0mm inner diameter of fuel tube
    pilot_fuel_OD: float = 1.6e-3   # 1.6mm outer diameter of fuel tube
    pilot_air_ID:  float = 1.6e-3   # 1.6mm inner diameter of air tube
    # pilot_air_OD: float = 2.0e-3  # 2.0mm outer diameter of air tube (no use case)

    # Pilot overall size
    pilot_burner_ID: float = 30e-3   # Inner boundary of the pilot burner
    pilot_burner_OD: float = 32e-3   # Outer boundary of the pilot burner

    # Pilot hex grid
    pilot_hex_cell_size: float = pilot_air_ID   # Hex inner circle diameter
    pilot_hex_wall_th:   float = 0.13e-3        # Hex mesh thickness

    # Co-flow geometry
    coflow_ID: float = pilot_burner_OD   # Based on Pilot
    coflow_OD: float = 154.0e-3          # Outer diameter of the co-flow


@dataclasses.dataclass
class OperatingParams:
    """
    Operating conditions at the burner inlet.
    -All temperatures are in Kelvin.
    -All pressures are in Pascal.
    -All velocities are in m/s.
    """

    # Central jet conditions
    jet_equivalence_ratio: float = 0.4
    jet_pressure:          float = 5e5     # 5 bar
    jet_temperature:       float = 298.15  # 25°C
    jet_velocity:          float = 100     # m/s

    # Pilot conditions
    # pilot_equivalence_ratio: float = 0.4
    pilot_pressure:      float = 5.0e5   # 5 bar
    pilot_temperature:   float = 298.15  # 25°C
    pilot_air_velocity:  float = 1.0     # m/s
    pilot_fuel_velocity: float = 1.6     # m/s

    # Co-flow conditions
    coflow_pressure:    float = 5.0e5    # 5 bar
    coflow_temperature: float = 298.15   # 25°C
    coflow_velocity:    float = 0.5      # m/s
