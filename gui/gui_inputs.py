from tkinter import ttk
from input_parameters.parameters import GeometryParams, OperatingParams


def create_input_fields(self, parent, section_title, params, row_start=0):
    frame = ttk.LabelFrame(parent, text=section_title, padding="10")
    frame.grid(row=row_start, column=0, columnspan=2, sticky="ew", pady=5)

    for i, (label, key, default) in enumerate(params):
        ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", padx=5)
        self.entries[key] = ttk.Entry(frame, width=12, style='Custom.TEntry')
        self.entries[key].insert(0, str(default))
        self.entries[key].grid(row=i, column=1, padx=10, pady=5, sticky='w')


def create_geometry_inputs(self, parent):
    params = [
        ("Jet inner diameter [mm]", "jet_ID", GeometryParams.jet_ID * 1e3),
        ("Jet outer diameter [mm]", "jet_OD", GeometryParams.jet_OD * 1e3),
        ("Pilot fuel tube ID [mm]", "pilot_fuel_ID", GeometryParams.pilot_fuel_ID * 1e3),
        ("Pilot fuel tube OD [mm]", "pilot_fuel_OD", GeometryParams.pilot_fuel_OD * 1e3),
        ("Pilot outer diameter [mm]", "pilot_burner_OD", GeometryParams.pilot_burner_OD * 1e3),
        ("Pilot wall thickness [mm]", "pilot_hex_wall_th", GeometryParams.pilot_hex_wall_th * 1e3),
        ("Pilot hex cell size [mm]", "pilot_hex_cell_size", GeometryParams.pilot_hex_cell_size * 1e3),
        ("Coflow outer diameter [mm]", "coflow_OD", GeometryParams.coflow_OD * 1e3)
    ]
    create_input_fields(self, parent, "Geometric Parameters", params)


def create_operating_inputs(self, parent):
    params = [
        ("Jet equivalence ratio [-]", "jet_equivalence_ratio", OperatingParams.jet_equivalence_ratio),
        ("Jet pressure [bar]", "jet_pressure", OperatingParams.jet_pressure * 1e-5),
        ("Jet temperature [°C]", "jet_temperature", OperatingParams.jet_temperature - 273.15),
        ("Jet velocity [m/s]", "jet_velocity", OperatingParams.jet_velocity),
        ("Pilot pressure [bar]", "pilot_pressure", OperatingParams.pilot_pressure * 1e-5),
        ("Pilot temperature [°C]", "pilot_temperature", OperatingParams.pilot_temperature - 273.15),
        ("Pilot air velocity [m/s]", "pilot_air_velocity", OperatingParams.pilot_air_velocity),
        ("Pilot fuel velocity [m/s]", "pilot_fuel_velocity", OperatingParams.pilot_fuel_velocity),
        ("Coflow pressure [bar]", "coflow_pressure", OperatingParams.coflow_pressure * 1e-5),
        ("Coflow temperature [°C]", "coflow_temperature", OperatingParams.coflow_temperature - 273.15),
        ("Coflow velocity [m/s]", "coflow_velocity", OperatingParams.coflow_velocity)
    ]
    create_input_fields(self, parent, "Operating Parameters", params, row_start=1)
