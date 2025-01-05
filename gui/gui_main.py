import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import PhotoImage
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from gui.styles import setup_styles
from gui.gui_inputs import InputFields
from gui.gui_outputs import OutputTiles
from input_parameters.parameters import GeometryParams, OperatingParams

from calculations import jet_burner as jb
from calculations import pilot_burner as pb
from calculations import n2_co_flow as cf
from calculations import mixed_temperature as mt

from geometry.plate_generator import get_hole_coordinates as plate_coordinates, plate_generator
from geometry.honeycomb_generator import get_hole_coordinates as honeycomb_coordinates, HexGrid



class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title('Hydrogen Burner Toolbox')
        setup_styles()
        self.root.geometry("1300x1000")
        self.root.minsize(1200, 1000)

        # Load the logo image
        self.logo = PhotoImage(file="gui/logo.png")
        self.root.iconphoto(False, self.logo)  # Set the application icon

        input_frame = ttk.Frame(root, padding="5")
        input_frame.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)
        dashboard_frame = ttk.Frame(root, padding="5")
        dashboard_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        root.grid_columnconfigure(1, weight=3)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        self.inputs = InputFields(input_frame)
        self.outputs = OutputTiles(dashboard_frame)

        ttk.Button(input_frame, text="Calculate", command=self.calculate).grid(row=2, column=0, columnspan=2,
                                                                               sticky="ew", pady=5)

        # Add "Generate DXF file" checkbox
        self.generate_dxf_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Generate a DXF file", variable=self.generate_dxf_var).grid(row=3, column=0,
                                                                                                      columnspan=2,
                                                                                                      sticky="w",
                                                                                                      pady=5)

        # Add plate config dropdown
        ttk.Label(input_frame, text="Burner Config:").grid(row=4, column=0, sticky="w", pady=5)
        self.plate_config_var = tk.StringVar()
        self.plate_config_dropdown = ttk.Combobox(input_frame, textvariable=self.plate_config_var,
                                                  values=["Plate", "Honeycomb"])
        self.plate_config_dropdown.grid(row=4, column=1, sticky="ew", pady=5)

    def calculate(self):
        self.outputs.clear_tile(self.outputs.flow_tile)
        self.outputs.clear_tile(self.outputs.thermal_tile)
        self.outputs.clear_tile(self.outputs.performance_tile)
        self.outputs.clear_tile(self.outputs.burner_geometry_display)

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

            geometry_config = self.plate_config_var.get()

            jet = jb.JetBurner(geom, op)
            pilot = pb.PilotBurner(geom, op)
            coflow = cf.CoFlow(geom, op)

            jet_props = jet.get_jet_burner_properties()
            pilot_results = pilot.get_pilot_burner_properties(geometry_config)
            coflow_results = coflow.get_co_flow_properties()

            mixer = mt.MixedTemperature(geom, op)
            mix_results = mixer.calculate_mixed_temperature(geometry_config)

            self.outputs.update_tiles(jet_props, pilot_results, coflow_results, mix_results)

            # Plot the geometry in the burner geometry display
            self.plot_geometry(geom, geometry_config)

            # Generate DXF file if the checkbox is ticked
            if self.generate_dxf_var.get():
                plate_generator(generate_dxf=True)

        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))

    def plot_geometry(self, geom, geometry_config):
        fig, ax = plt.subplots()

        if geometry_config == "Plate":
            # Get hole coordinates for plate
            air_holes, fuel_holes, central_jet = plate_coordinates()

            # Plot air holes
            for circle in air_holes:
                x, y = circle.exterior.xy
                ax.plot(x, y, color='blue')

            # Plot fuel holes
            for circle in fuel_holes:
                x, y = circle.exterior.xy
                ax.plot(x, y, color='red')

            # Plot central jet
            x, y = central_jet.exterior.xy
            ax.plot(x, y, color='green')

            ax.set_title('Plate Generator Grid')

        elif geometry_config == "Honeycomb":
            # Generate the hexagonal grid
            hex_grid = HexGrid(geom)
            burner_boundary = hex_grid.generate_burner_boundary()
            air_holes, fuel_holes, central_jet = honeycomb_coordinates()

            # Plot burner boundary
            x, y = burner_boundary.exterior.xy
            ax.plot(x, y, color='black', linestyle='dotted')

            # Plot air holes
            for hexagon in air_holes:
                x, y = hexagon.exterior.xy
                ax.plot(x, y, color='blue')

            # Plot fuel holes
            for fuel_hole in fuel_holes:
                circle = fuel_hole['circle']
                x, y = circle.exterior.xy
                ax.plot(x, y, color='red')

                # Plot pilot fuel OD
                od_circle = fuel_hole['od_circle']
                x, y = od_circle.exterior.xy
                ax.plot(x, y, color='orange', linestyle='dashed')

            # Plot central jet
            x, y = central_jet['circle'].exterior.xy
            ax.plot(x, y, color='green')

            # Plot central jet OD
            x, y = central_jet['od_circle'].exterior.xy
            ax.plot(x, y, color='purple', linestyle='dashed')

            ax.set_title('Hexagonal Grid Geometry')

        ax.set_xlabel('X-axis (mm)')
        ax.set_ylabel('Y-axis (mm)')
        ax.set_aspect('equal', 'box')  # Set 1:1 axis ratio

        # Set tick labels to show values in millimeters
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'{val * 1000:.0f}'))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'{val * 1000:.0f}'))

        canvas = FigureCanvasTkAgg(fig, master=self.outputs.burner_geometry_display)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()
