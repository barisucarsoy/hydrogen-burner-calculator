import plotly.graph_objs as go
from input_parameters.parameters import GeometryParams
from geometry.grid_generator import HexagonalGridGenerator
import shapely.geometry
import math
from geometry.geometry_utils import is_fuel_position_cartesian, generate_hexagon


class HexGrid:
    def __init__(self, params: GeometryParams):
        # Dynamically set attributes from the params instance
        for key, value in params.__dict__.items():
            setattr(self, key, value)

        # Initialize grid parameters
        self.center_distance = self.pilot_hex_cell_size + self.pilot_hex_wall_th
        self.boundary = self.pilot_burner_ID * 1.2
        self.row_height = self.center_distance * math.sqrt(3) / 2

        # Initialize grid
        self.grid = HexagonalGridGenerator(
            center_distance=self.center_distance,
            boundary=self.boundary)

        # Generate coordinates
        coordinates = self.grid.generate_coordinates()
        self.cartesian_coords = coordinates['cartesian_coordinates']

    def generate_air_holes(self):
        hexagons = []
        radius = self.pilot_air_ID / math.sqrt(3)
        for coord in self.cartesian_coords:
            hexagon = generate_hexagon(coord, radius)
            hexagons.append(hexagon)
        return hexagons

    def check_fuel_positions(self):
        fuel_positions_cartesian = []

        for coord in self.cartesian_coords:
            if is_fuel_position_cartesian(self, coord[0], coord[1]):
                fuel_positions_cartesian.append(coord)
        return fuel_positions_cartesian

    def print_fuel_positions(self):
        fuel_positions_cartesian = self.check_fuel_positions()

        for pos in fuel_positions_cartesian:
            print(f"Fuel position at x: {pos[0]}, y: {pos[1]}")


def main():
    # Initialize geometry parameters
    params = GeometryParams()

    # Initialize hex grid
    hex_grid = HexGrid(params)

    # Generate hexagons
    hexagons = hex_grid.generate_air_holes()
    fuel_positions_cartesian = hex_grid.check_fuel_positions()

    # Plot hexagons
    fig = go.Figure()

    for hexagon in hexagons:
        x, y = hexagon.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x), y=list(y),
            mode='lines',
            fill='toself'
        ))

    # Plot Cartesian fuel positions
    fuel_x = [pos[0] for pos in fuel_positions_cartesian]
    fuel_y = [pos[1] for pos in fuel_positions_cartesian]
    fig.add_trace(go.Scatter(
        x=fuel_x, y=fuel_y,
        mode='markers',
        marker=dict(color='blue', size=5),
        name='Cartesian Fuel Positions'
    ))

    # Set the aspect ratio to be equal
    fig.update_layout(
        yaxis=dict(scaleanchor="x", scaleratio=1),
        xaxis=dict(constrain='domain'),
        showlegend=False
    )

    fig.show()


if __name__ == '__main__':
    main()
