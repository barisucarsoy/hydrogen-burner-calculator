import plotly.graph_objs as go
from input_parameters.parameters import GeometryParams
from geometry.grid_generator import HexagonalGridGenerator
import shapely.geometry

class HexGrid:
    def __init__(self, params: GeometryParams):
        # Dynamically set attributes from the params instance
        for key, value in params.__dict__.items():
            setattr(self, key, value)

        # Initialize grid
        self.grid = HexagonalGridGenerator(
            center_distance=self.pilot_hex_cell_size + self.pilot_hex_wall_th,
            boundary=self.pilot_burner_ID * 1.2)

        # Generate coordinates
        coordinates = self.grid.generate_coordinates()
        self.cartesian_coords = coordinates['cartesian_coordinates']
        self.cubic_coords = coordinates['cubic_coordinates']

    def generate_circles(self):
        circles = []
        radius = self.pilot_air_ID / 2
        for coord in self.cartesian_coords:
            point = shapely.geometry.Point(coord)
            circle = point.buffer(radius)
            circles.append(circle)
        return circles

    def plot_circles(self):
        circles = self.generate_circles()
        fig = go.Figure()

        for circle in circles:
            x, y = circle.exterior.xy
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                mode='lines',
                fill='toself'
            ))

        fig.update_layout(
            title='Hexagonal Grid with Circles',
            xaxis_title='X',
            yaxis_title='Y',
            showlegend=False,
            xaxis=dict(
                scaleanchor='y',
                scaleratio=1
            ),
            yaxis=dict(
                scaleratio=1
            )
        )

        fig.show()

params = GeometryParams()
hex_grid = HexGrid(params)
hex_grid.plot_circles()
