# gui/gui_main.py
import tkinter as tk
from tkinter import ttk, messagebox

from gui.styles import setup_styles
from gui.gui_inputs import InputFields
from gui.gui_outputs import OutputTiles
from input_parameters.parameters import GeometryParams, OperatingParams

from calculations import jet_burner as jb
from calculations import pilot_burner as pb
from calculations import n2_co_flow as cf
from calculations import mixed_temperature as mt

class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title('Hydrogen Burner Toolbox')
        setup_styles()
        self.root.geometry("1200x900")
        self.root.minsize(1200, 900)

        input_frame = ttk.Frame(root, padding="5")
        input_frame.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)
        dashboard_frame = ttk.Frame(root, padding="5")
        dashboard_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        root.grid_columnconfigure(1, weight=3)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        self.inputs = InputFields(input_frame)
        self.outputs = OutputTiles(dashboard_frame)

        ttk.Button(input_frame, text="Calculate", command=self.calculate).grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

    def calculate(self):
        self.outputs.clear_tile(self.outputs.flow_tile)
        self.outputs.clear_tile(self.outputs.thermal_tile)
        self.outputs.clear_tile(self.outputs.performance_tile)
        self.outputs.clear_tile(self.outputs.mixing_tile)

        try:
            geom = GeometryParams(
                jet_ID=float(self.inputs.entries["jet_ID"].get()) * 1e-3,
                jet_OD=float(self.inputs.entries["jet_OD"].get()) * 1e-3,
                pilot_fuel_ID=float(self.inputs.entries["pilot_fuel_ID"].get()) * 1e-3,
                pilot_fuel_OD=float(self.inputs.entries["pilot_fuel_OD"].get()) * 1e-3,
                pilot_burner_OD=float(self.inputs.entries["pilot_burner_OD"].get()) * 1e-3,
                pilot_hex_wall_th=float(self.inputs.entries["pilot_hex_wall_th"].get()) * 1e-3,
                pilot_hex_cell_size=float(self.inputs.entries["pilot_hex_cell_size"].get()) * 1e-3,
                coflow_OD=float(self.inputs.entries["coflow_OD"].get()) * 1e-3
            )

            op = OperatingParams(
                jet_equivalence_ratio=float(self.inputs.entries["jet_equivalence_ratio"].get()),
                jet_pressure=float(self.inputs.entries["jet_pressure"].get()) * 1e5,
                jet_temperature=float(self.inputs.entries["jet_temperature"].get()) + 273.15,
                jet_velocity=float(self.inputs.entries["jet_velocity"].get()),
                pilot_pressure=float(self.inputs.entries["pilot_pressure"].get()) * 1e5,
                pilot_temperature=float(self.inputs.entries["pilot_temperature"].get()) + 273.15,
                pilot_air_velocity=float(self.inputs.entries["pilot_air_velocity"].get()),
                pilot_fuel_velocity=float(self.inputs.entries["pilot_fuel_velocity"].get()),
                coflow_pressure=float(self.inputs.entries["coflow_pressure"].get()) * 1e5,
                coflow_temperature=float(self.inputs.entries["coflow_temperature"].get()) + 273.15,
                coflow_velocity=float(self.inputs.entries["coflow_velocity"].get())
            )

            jet = jb.JetBurner(geom, op)
            pilot = pb.PilotBurner(geom, op)
            coflow = cf.CoFlow(geom, op)

            jet_props = jet.get_jet_burner_properties()
            pilot_results = pilot.get_pilot_burner_properties()
            coflow_results = coflow.get_co_flow_properties()

            mixer = mt.MixedTemperature(geom, op)
            mix_results = mixer.calculate_mixed_temperature()

            self.outputs.update_tiles(jet_props, pilot_results, coflow_results, mix_results)

        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()
