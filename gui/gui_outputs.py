# gui/gui_outputs.py
from tkinter import ttk

class OutputTiles:
    def __init__(self, parent):
        self.flow_tile = self.create_tile(parent, "Flow Parameters", 0, 0)
        self.thermal_tile = self.create_tile(parent, "Thermal Properties", 0, 1)
        self.performance_tile = self.create_tile(parent, "Performance", 1, 0)
        self.mixing_tile = self.create_tile(parent, "Mixed Properties", 1, 1)

    def create_tile(self, parent, title, row, col):
        tile = ttk.LabelFrame(parent, text=title, style='Tile.TLabelframe')
        tile.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        content = ttk.Frame(tile)
        content.pack(fill='both', expand=True, pady=5)
        return content

    def update_tiles(self, jet_props, pilot_results, coflow_results, mix_results):
        self.update_flow_tile(jet_props, pilot_results, coflow_results)
        self.update_thermal_tile(jet_props, pilot_results, coflow_results)
        self.update_performance_tile(jet_props, pilot_results, coflow_results)
        self.update_mixing_tile(mix_results)

    def add_label(self, parent, text):
        ttk.Label(parent, text=text, style='TileValue.TLabel').pack()

    def update_flow_tile(self, jet_props, pilot_results, coflow_results):
        self.clear_tile(self.flow_tile)
        mass_flow_frame = ttk.Frame(self.flow_tile)
        mass_flow_frame.pack(fill='x', pady=5)
        ttk.Label(mass_flow_frame, text="Mass Flows", style='TileHeader.TLabel').pack()
        self.add_label(self.flow_tile, f"Jet Mass Flow       :  {jet_props.mass_flow_total * 1000:.2f} g/s")
        self.add_label(self.flow_tile, f"Pilot Fuel Mass Flow:  {pilot_results.mass_flow_h2* 1000:.2f} g/s")
        self.add_label(self.flow_tile, f"Pilot Air Mass Flow :  {pilot_results.mass_flow_air * 1000:.2f} g/s")
        self.add_label(self.flow_tile, f"Co-Flow Mass Flow   : {coflow_results.mass_flow * 1000:.2f} g/s")

    def update_thermal_tile(self, jet_props, pilot_results, coflow_results):
        self.clear_tile(self.thermal_tile)
        # Add thermal properties update logic here

    def update_performance_tile(self, jet_props, pilot_results, coflow_results):
        self.clear_tile(self.performance_tile)
        # Add performance properties update logic here

    def update_mixing_tile(self, mix_results):
        self.clear_tile(self.mixing_tile)
        # Add mixing properties update logic here

    def clear_tile(self, tile):
        for widget in tile.winfo_children():
            widget.destroy()
