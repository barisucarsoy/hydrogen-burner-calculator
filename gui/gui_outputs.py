from tkinter import ttk


class OutputTiles:
    def __init__(self, parent):
        self.flow_tile = self.create_tile(parent, "Flow Parameters", 0, 0, columnspan=1)
        self.thermal_tile = self.create_tile(parent, "Thermal Properties", 1, 0, columnspan=1)
        self.performance_tile = self.create_tile(parent, "Performance", 2, 0, columnspan=1)
        self.burner_geometry_display = self.create_tile(parent, "Burner Geometry Display", 0, 2, columnspan=1, rowspan=4)
        self.flow_labels = {}

    def create_tile(self, parent, title, row, col, columnspan=1, rowspan=1):
        tile = ttk.LabelFrame(parent, text=title, style='Tile.TLabelframe')
        tile.grid(row=row, column=col, columnspan=columnspan, rowspan=rowspan, padx=5, pady=5, sticky="nsew")
        content = ttk.Frame(tile)
        content.pack(fill='both', expand=True, pady=5)
        return content

    def add_label(self, parent, text, style='TileValue.TLabel'):
        label = ttk.Label(parent, text=text, style=style)
        label.pack(fill='x', expand=True, padx=5, pady=2)
        return label

    def update_tiles(self, jet_props, pilot_results, coflow_results, mix_results):
        self.update_flow_tile(jet_props, pilot_results, coflow_results)
        self.update_thermal_tile(jet_props, pilot_results, coflow_results, mix_results)
        self.update_performance_tile(jet_props, pilot_results, coflow_results)

    def update_flow_tile(self, jet_props, pilot_results, coflow_results):
        kgs_to_gms = 1000  # Conversion factor from kg/s to g/s
        m3s_to_lpm = 60000  # Conversion factor from m³/s to LPM

        # Add section titles with a distinct style
        mass_flow_frame = ttk.Frame(self.flow_tile)
        mass_flow_frame.pack(fill='x', expand=True, pady=5)
        ttk.Label(mass_flow_frame, text="Mass Flows", style='TileHeader.TLabel').pack()
        self.flow_labels['Jet Mass Flow'] = self.add_label(self.flow_tile,
                                                           f"Jet Mass Flow: {jet_props.mass_flow_total * kgs_to_gms:.2f} g/s")
        self.flow_labels['Pilot Fuel Mass Flow'] = self.add_label(self.flow_tile,
                                                                  f"Pilot Fuel Mass Flow: {pilot_results.mass_flow_h2 * kgs_to_gms:.2f} g/s")
        self.flow_labels['Pilot Air Mass Flow'] = self.add_label(self.flow_tile,
                                                                 f"Pilot Air Mass Flow: {pilot_results.mass_flow_air * kgs_to_gms:.2f} g/s")
        self.flow_labels['Co-Flow Mass Flow'] = self.add_label(self.flow_tile,
                                                               f"Co-Flow Mass Flow: {coflow_results.mass_flow * kgs_to_gms:.2f} g/s")

        volume_flow_frame = ttk.Frame(self.flow_tile)
        volume_flow_frame.pack(fill='x', expand=True, pady=5)
        ttk.Label(volume_flow_frame, text="Volume Flows", style='TileHeader.TLabel').pack()
        self.flow_labels['Jet Volume Flow'] = self.add_label(self.flow_tile,
                                                             f"Jet Volume Flow: {jet_props.vol_flow_real_total * m3s_to_lpm:.2f} LPM")
        self.flow_labels['Pilot Fuel Volume Flow'] = self.add_label(self.flow_tile,
                                                                    f"Pilot Fuel Volume Flow: {pilot_results.vol_flow_real_h2 * m3s_to_lpm:.2f} LPM")
        self.flow_labels['Pilot Air Volume Flow'] = self.add_label(self.flow_tile,
                                                                   f"Pilot Air Volume Flow: {pilot_results.vol_flow_real_air * m3s_to_lpm:.2f} LPM")
        self.flow_labels['Co-Flow Volume Flow'] = self.add_label(self.flow_tile,
                                                                 f"Co-Flow Volume Flow: {coflow_results.volume_flow * m3s_to_lpm:.2f} LPM")

        std_volume_flow_frame = ttk.Frame(self.flow_tile)
        std_volume_flow_frame.pack(fill='x', expand=True, pady=5)
        ttk.Label(std_volume_flow_frame, text="Normal Volume Flows at 1 atm, 0 degC", style='TileHeader.TLabel').pack()
        self.flow_labels['Jet Fuel Volume Flow'] = self.add_label(self.flow_tile,
                                                                  f"Jet Fuel Volume Flow: {jet_props.vol_flow_std_h2 * m3s_to_lpm:.2f} nLPM, {jet_props.vol_flow_std_h2 * 3600:.3f} m³/h")
        self.flow_labels['Jet Air Volume Flow'] = self.add_label(self.flow_tile,
                                                                 f"Jet Air Volume Flow: {jet_props.vol_flow_std_air * m3s_to_lpm:.2f} nLPM, {jet_props.vol_flow_std_air * 3600:.3f} m³/h")
        self.flow_labels['Pilot Fuel Volume Flow'] = self.add_label(self.flow_tile,
                                                                    f"Pilot Fuel Volume Flow: {pilot_results.vol_flow_std_h2 * m3s_to_lpm:.2f} nLPM, {pilot_results.vol_flow_std_h2 * 3600:.3f} m³/h")
        self.flow_labels['Pilot Air Volume Flow'] = self.add_label(self.flow_tile,
                                                                   f"Pilot Air Volume Flow: {pilot_results.vol_flow_std_air * m3s_to_lpm:.2f} nLPM, {pilot_results.vol_flow_std_air * 3600:.3f} m³/h")
        self.flow_labels['Co-Flow Volume Flow'] = self.add_label(self.flow_tile,
                                                                 f"Co-Flow Volume Flow: {coflow_results.std_volume_flow * m3s_to_lpm:.2f} nLPM, {coflow_results.std_volume_flow * 3600:.3f} m³/h")

    def update_thermal_tile(self, jet_props, pilot_results, coflow_results, mix_results):
        thermal_frame = ttk.Frame(self.thermal_tile)
        thermal_frame.pack(fill='x', expand=True, pady=5)
        ttk.Label(thermal_frame, text="Thermal Properties", style='TileHeader.TLabel').pack()

        self.flow_labels['Mixed Temp'] = self.add_label(self.thermal_tile,
                                                        f"Mixed Temp: {mix_results.mixed_temp - 273.15:.1f}°C")

        # Add flame power
        self.flow_labels['Jet Flame Power'] = self.add_label(self.thermal_tile,
                                                             f"Flame Power: {jet_props.flame_power:.2f} W")
        self.flow_labels['Pilot Flame Power'] = self.add_label(self.thermal_tile,
                                                               f"Flame Power: {pilot_results.flame_power:.2f} W")

        self.flow_labels['Jet Enthalpy'] = self.add_label(self.thermal_tile,
                                                          f"Jet Enthalpy: {jet_props.flame_enthalpy_mass:.1f} J/kg")
        self.flow_labels['Jet Flame Temp'] = self.add_label(self.thermal_tile,
                                                            f"Jet Flame Temp: {jet_props.flame_temperature - 273.15:.1f}°C")
        self.flow_labels['Pilot Flame Temp'] = self.add_label(self.thermal_tile,
                                                              f"Pilot Flame Temp: {pilot_results.flame_temperature - 273.15:.1f}°C")
        self.flow_labels['Pilot OF Ratio'] = self.add_label(self.thermal_tile,
                                                            f"Pilot equivalence Ratio: {pilot_results.equivalence_ratio:.4f}")

    def update_performance_tile(self, jet_props, pilot_results, coflow_results):
        self.clear_tile(self.performance_tile)
        # Add Physical Parameters such as Reynolds numbers
        performance_frame = ttk.Frame(self.performance_tile)
        performance_frame.pack(fill='x', expand=True, pady=5)
        ttk.Label(performance_frame, text="Performance", style='TileHeader.TLabel').pack()

        self.flow_labels['Jet Reynolds Number'] = self.add_label(self.performance_tile,
                                                                 f"Jet Reynolds Number: {jet_props.reynolds_number:.2f}")
        self.flow_labels['Pilot Reynolds Number'] = self.add_label(self.performance_tile,
                                                                   f"Pilot Fuel Reynolds Number: {pilot_results.reynolds_number_h2:.2f}")
        self.flow_labels['Pilot Reynolds Number'] = self.add_label(self.performance_tile,
                                                                   f"Pilot Air Reynolds Number: {pilot_results.reynolds_number_air:.2f}")
        self.flow_labels['Co-Flow Reynolds Number'] = self.add_label(self.performance_tile,
                                                                     f"Co-Flow Reynolds Number: {coflow_results.Re:.2f}")
        self.flow_labels['Pilot Mixed Flow Velocity'] = self.add_label(self.performance_tile,
                                                                       f"Mixed Flow Velocity: {pilot_results.mixed_velocity:.2f} m/s")
        self.flow_labels['Pilot Mixed Flow Density'] = self.add_label(self.performance_tile,
                                                                 f"Pilot Mixed Flow Density: {pilot_results.rho_mix:.2f} kg/m³")
        self.flow_labels['Pilot air density'] = self.add_label(self.performance_tile,
                                                                f"Pilot Air Density: {pilot_results.rho_air:.2f} kg/m³")

    def clear_tile(self, tile):
        for widget in tile.winfo_children():
            widget.destroy()
