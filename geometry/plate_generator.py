from input_parameters.parameters import GeometryParams
from geometry.grid_generator import HexagonalGridGenerator
import shapely.geometry
import math
from geometry.geometry_utils import is_fuel_position_cubic, cubic_to_cartesian
import ezdxf
import os
from datetime import datetime


class HexGrid:
    def __init__(self, params: GeometryParams):
        # Dynamically set attributes from the params instance
        for key, value in params.__dict__.items():
            setattr(self, key, value)

        # Initialize grid parameters
        self.center_distance = self.pilot_hex_cell_size + self.pilot_hex_wall_th
        self.boundary = self.pilot_burner_ID * 1.2
        self.r_out = self.center_distance / math.sqrt(3)  # radius of the outer circle of the middle wall hexagon
        self.row_height = self.center_distance * math.sqrt(3) / 2

        # Initialize grid
        self.grid = HexagonalGridGenerator(
            center_distance=self.center_distance,
            boundary=self.boundary)

        # Generate coordinates
        coordinates = self.grid.generate_coordinates()
        self.cartesian_coords = coordinates['cartesian_coordinates']
        self.cubic_coords = coordinates['cubic_coordinates']

        # Create boundary polygon
        self.boundary_polygon = shapely.geometry.Point(0, 0).buffer(self.pilot_burner_ID * 0.95 / 2)

    def generate_air_holes(self, fuel_holes, central_jet):
        # Generate air holes avoiding overlap with fuel holes and central jet
        circles = []
        radius = self.pilot_air_ID / 2
        for coord in self.cubic_coords:
            cart_coord = cubic_to_cartesian(coord[0], coord[1], coord[2], self.center_distance / math.sqrt(3))
            point = shapely.geometry.Point(cart_coord)
            circle = point.buffer(radius)
            distance_to_boundary = self.boundary_polygon.exterior.distance(point)
            if not any(circle.intersection(fuel_hole).area > 0 for fuel_hole in fuel_holes) and (
                    self.boundary_polygon.contains(circle) or distance_to_boundary == radius):
                if central_jet.intersects(circle):
                    circle = point.buffer(radius / math.sqrt(2))  # Reduce size for intersecting circles in the middle
                if point.distance(shapely.geometry.Point(0, 0)) > radius:
                    circles.append(circle)  # Exclude the central circle
        return circles

    def generate_fuel_holes(self, fuel_positions):
        # Generate fuel holes within the boundary
        circles = []
        radius = self.pilot_fuel_ID / 2
        for coord in fuel_positions:
            point = shapely.geometry.Point(coord)
            circle = point.buffer(radius)
            if self.boundary_polygon.contains(circle):
                circles.append(circle)
        return circles

    def generate_central_jet(self):
        # Generate the central jet circle
        radius = self.jet_ID / 2
        central_jet = shapely.geometry.Point(0, 0).buffer(radius)
        return central_jet

    def check_fuel_positions(self):
        # Check and return fuel positions in cubic coordinates
        fuel_positions_cubic = []
        for coord in self.cubic_coords:
            if is_fuel_position_cubic(coord[0], coord[1]):
                fuel_positions_cubic.append(coord)
        return fuel_positions_cubic

    def export_to_dxf(self, air_holes, fuel_holes, central_jet, filename):
        # Export the geometry to a DXF file with each hole type on a different layer
        doc = ezdxf.new()
        msp = doc.modelspace()

        # Add air holes to the DXF
        air_layer = doc.layers.new(name='AirHoles', dxfattribs={'color': 1})
        for circle in air_holes:
            center = circle.centroid
            radius = center.distance(shapely.geometry.Point(circle.exterior.coords[0]))
            msp.add_circle(center=(center.x, center.y), radius=radius, dxfattribs={'layer': 'AirHoles'})

        # Add fuel holes to the DXF
        fuel_layer = doc.layers.new(name='FuelHoles', dxfattribs={'color': 2})
        for circle in fuel_holes:
            center = circle.centroid
            radius = center.distance(shapely.geometry.Point(circle.exterior.coords[0]))
            msp.add_circle(center=(center.x, center.y), radius=radius, dxfattribs={'layer': 'FuelHoles'})

        # Add central jet to the DXF
        jet_layer = doc.layers.new(name='CentralJet', dxfattribs={'color': 3})
        center = central_jet.centroid
        radius = center.distance(shapely.geometry.Point(central_jet.exterior.coords[0]))
        msp.add_circle(center=(center.x, center.y), radius=radius, dxfattribs={'layer': 'CentralJet'})

        # Save the DXF file
        doc.saveas(filename)

    def calculate_hole_statistics(self, air_holes, fuel_holes):
        # Calculate and return the air hole number, air hole area, fuel hole number, fuel hole area, and air to fuel
        # area ratio
        air_hole_number = len(air_holes)
        air_hole_area = sum(circle.area for circle in air_holes)
        fuel_hole_number = len(fuel_holes)
        fuel_hole_area = sum(circle.area for circle in fuel_holes)
        air_to_fuel_area_ratio = air_hole_area / fuel_hole_area if fuel_hole_area > 0 else float('inf')

        return {
            'air_hole_number': air_hole_number,
            'air_hole_area': air_hole_area,
            'fuel_hole_number': fuel_hole_number,
            'fuel_hole_area': fuel_hole_area,
            'air_to_fuel_area_ratio': air_to_fuel_area_ratio
        }


def plate_generator(generate_dxf=False):
    # Initialize geometry parameters
    params = GeometryParams()

    # Initialize hex grid
    hex_grid = HexGrid(params)

    # Check fuel positions
    fuel_positions_cubic = hex_grid.check_fuel_positions()
    fuel_positions_cartesian = [cubic_to_cartesian(q, r, s, hex_grid.center_distance / math.sqrt(3)) for q, r, s in
                                fuel_positions_cubic]

    # Generate fuel holes
    fuel_holes = hex_grid.generate_fuel_holes(fuel_positions_cartesian)

    # Generate central jet
    central_jet = hex_grid.generate_central_jet()

    # Generate air holes, ensuring no overlap with fuel holes
    air_holes = hex_grid.generate_air_holes(fuel_holes, central_jet)

    # Optionally export geometry to DXF
    if generate_dxf:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')

        filename = os.path.join(data_dir, f'geometry_{datetime.now().strftime("%Y%m%d_%H%M%S")}.dxf')
        hex_grid.export_to_dxf(air_holes, fuel_holes, central_jet, filename)

    # Calculate hole statistics
    stats = hex_grid.calculate_hole_statistics(air_holes, fuel_holes)
    return stats


def get_hole_coordinates():
    # Initialize geometry parameters
    params = GeometryParams()

    # Initialize hex grid
    hex_grid = HexGrid(params)

    # Check fuel positions
    fuel_positions_cubic = hex_grid.check_fuel_positions()
    fuel_positions_cartesian = [cubic_to_cartesian(q, r, s, hex_grid.center_distance / math.sqrt(3)) for q, r, s in
                                fuel_positions_cubic]

    # Generate fuel holes
    fuel_holes = hex_grid.generate_fuel_holes(fuel_positions_cartesian)

    # Generate central jet
    central_jet = hex_grid.generate_central_jet()

    # Generate air holes, ensuring no overlap with fuel holes
    air_holes = hex_grid.generate_air_holes(fuel_holes, central_jet)

    return air_holes, fuel_holes, central_jet


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate hex grid and optionally export to DXF.')
    parser.add_argument('--generate-dxf', action='store_true', help='Generate DXF file')
    args = parser.parse_args()

    stats = plate_generator(generate_dxf=args.generate_dxf)

    print(stats)
