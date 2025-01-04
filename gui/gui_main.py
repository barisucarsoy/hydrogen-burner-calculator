import tkinter as tk
from tkinter import ttk, messagebox

from gui.styles import setup_styles


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

        # Create input sections (keep existing)
        self.entries = {}
        self.create_geometry_inputs(input_frame)
        self.create_operating_inputs(input_frame)

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



if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()
