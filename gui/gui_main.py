import tkinter as tk
from tkinter import ttk, messagebox

from gui.styles import setup_styles
from gui.gui_inputs import create_geometry_inputs, create_operating_inputs
from gui.gui_outputs import update_tiles
from input_parameters.parameters import GeometryParams, OperatingParams

from calculations import jet_burner as jb
from calculations import pilot_burner as pb
from calculations import n2_co_flow as cf
from calculations import mixed_temperature as mt


def create_tile(parent, title, row, col):
    tile = ttk.LabelFrame(parent, text=title, style='Tile.TLabelframe')
    tile.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    # Create content frame inside tile
    content = ttk.Frame(tile)
    content.pack(fill='both', expand=True, pady=5)

    return content


class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title('Hydrogen Burner Toolbox')

        setup_styles()

        # Set initial window size (width x height)
        self.root.geometry("1200x900")  # Format is "WIDTHxHEIGHT"

        # Optional: Set minimum window size
        self.root.minsize(1200, 900)  # Minimum width=1200, height=700

        # Create main container frames
        input_frame = ttk.Frame(root, padding="5")
        input_frame.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)

        # Create dashboard frame
        dashboard_frame = ttk.Frame(root, padding="5")
        dashboard_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configure grid weights
        root.grid_columnconfigure(1, weight=3)  # Dashboard takes more space
        root.grid_columnconfigure(0, weight=1)  # Input panel
        root.grid_rowconfigure(0, weight=1)

        # Create input sections
        self.entries = {}
        create_geometry_inputs(self, input_frame)
        create_operating_inputs(self, input_frame)

        # Create dashboard tiles
        self.create_dashboard(dashboard_frame)

        ttk.Button(input_frame,
                   text="Calculate",
                   command=self.calculate).grid(row=2,
                                                column=0,
                                                columnspan=2,
                                                sticky="ew",
                                                pady=5)

    def create_dashboard(self, parent):
        # Create 2x2 grid of tiles
        self.flow_tile = create_tile(parent, "Flow Parameters", 0, 0)
        self.thermal_tile = create_tile(parent, "Thermal Properties", 0, 1)
        self.performance_tile = create_tile(parent, "Performance", 1, 0)
        self.mixing_tile = create_tile(parent, "Mixed Properties", 1, 1)

        # Configure grid weights for tiles
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

    def calculate(self):
        # Clear previous results
        for widget in self.flow_tile.winfo_children():
            widget.destroy()
        for widget in self.thermal_tile.winfo_children():
            widget.destroy()
        for widget in self.performance_tile.winfo_children():
            widget.destroy()
        for widget in self.mixing_tile.winfo_children():
            widget.destroy()

        try:
            # Retrieve input values
            geom = GeometryParams(
                jet_ID=float(self.entries["jet_ID"].get()) * 1e-3,
                jet_OD=float(self.entries["jet_OD"].get()) * 1e-3,
                pilot_fuel_ID=float(self.entries["pilot_fuel_ID"].get()) * 1e-3,
                pilot_fuel_OD=float(self.entries["pilot_fuel_OD"].get()) * 1e-3,
                pilot_burner_OD=float(self.entries["pilot_burner_OD"].get()) * 1e-3,
                pilot_hex_wall_th=float(self.entries["pilot_hex_wall_th"].get()) * 1e-3,
                pilot_hex_cell_size=float(self.entries["pilot_hex_cell_size"].get()) * 1e-3,
                coflow_OD=float(self.entries["coflow_OD"].get()) * 1e-3
            )

            op = OperatingParams(
                jet_equivalence_ratio=float(self.entries["jet_equivalence_ratio"].get()),
                jet_pressure=float(self.entries["jet_pressure"].get()) * 1e5,
                jet_temperature=float(self.entries["jet_temperature"].get()) + 273.15,
                jet_velocity=float(self.entries["jet_velocity"].get()),
                pilot_pressure=float(self.entries["pilot_pressure"].get()) * 1e5,
                pilot_temperature=float(self.entries["pilot_temperature"].get()) + 273.15,
                pilot_air_velocity=float(self.entries["pilot_air_velocity"].get()),
                pilot_fuel_velocity=float(self.entries["pilot_fuel_velocity"].get()),
                coflow_pressure=float(self.entries["coflow_pressure"].get()) * 1e5,
                coflow_temperature=float(self.entries["coflow_temperature"].get()) + 273.15,
                coflow_velocity=float(self.entries["coflow_velocity"].get())
            )

            # Calculate properties
            jet = jb.JetBurner(geom, op)
            pilot = pb.PilotBurner(geom, op)
            coflow = cf.CoFlow(geom, op)

            jet_props = jet.get_jet_burner_properties()
            pilot_results = pilot.get_pilot_burner_properties()
            coflow_results = coflow.get_co_flow_properties()

            mixer = mt.MixedTemperature(geom, op)
            mix_results = mixer.calculate_mixed_temperature()

            # Update dashboard tiles with results
            update_tiles(jet_props, pilot_results, coflow_results, mix_results)

        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()
