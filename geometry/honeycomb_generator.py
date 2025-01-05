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
        for key, value in params.__dict__.items():
            setattr(self, key, value)

        self.center_distance = self.pilot_hex_cell_size + self.pilot_hex_wall_th
        self.boundary = self.pilot_burner_ID * 1.1
        self.r_out = self.center_distance / math.sqrt(3)
        self.row_height = self.center_distance * math.sqrt(3) / 2

        self.grid = HexagonalGridGenerator(
            center_distance=self.center_distance,
            boundary=self.boundary)

        coordinates = self.grid.generate_coordinates()
        self.cartesian_coords = coordinates['cartesian_coordinates']
        self.cubic_coords = coordinates['cubic_coordinates']

        self.boundary_polygon = shapely.geometry.Point(0, 0).buffer(self.boundary / 2)

    def generate_air_holes(self, fuel_holes, central_jet):
        hexagons = []
        radius = self.pilot_air_ID / math.sqrt(3)  # Use inner radius
        burner_boundary = self.generate_burner_boundary()
        for coord in self.cubic_coords:
            cart_coord = cubic_to_cartesian(coord[0], coord[1], coord[2], self.center_distance / math.sqrt(3))
            hexagon = shapely.geometry.Polygon(self._create_hexagon(cart_coord, radius))
            if hexagon.intersects(burner_boundary):
                hexagon = hexagon.intersection(burner_boundary)
            if not any(hexagon.intersects(fuel_hole['circle']) for fuel_hole in
                       fuel_holes) and self.boundary_polygon.contains(hexagon):
                hexagons.append(hexagon)
        return hexagons

    def generate_fuel_holes(self, fuel_positions):
        circles = []
        radius = self.pilot_fuel_ID / 2
        od_radius = self.pilot_fuel_OD / 2
        burner_boundary = self.generate_burner_boundary()
        for coord in fuel_positions:
            point = shapely.geometry.Point(coord)
            circle = point.buffer(radius)
            od_circle = point.buffer(od_radius)
            if burner_boundary.contains(circle):
                circles.append({
                    'circle': circle,
                    'od_circle': od_circle,
                    'od': self.pilot_fuel_OD,
                    'id': self.pilot_fuel_ID
                })
        return circles

    def generate_burner_boundary(self):
        radius = self.pilot_burner_ID / 2
        burner_boundary = shapely.geometry.Point(0, 0).buffer(radius)
        return burner_boundary

    def _create_hexagon(self, center, radius):
        angle = math.pi / 3
        return [(center[0] + radius * math.cos(i * angle + math.pi / 6),
                 center[1] + radius * math.sin(i * angle + math.pi / 6)) for i in range(6)]

    def generate_central_jet(self):
        radius = self.jet_ID / 2
        od_radius = self.jet_OD / 2
        central_jet = shapely.geometry.Point(0, 0).buffer(radius)
        central_jet_od = shapely.geometry.Point(0, 0).buffer(od_radius)
        return {'circle': central_jet, 'od_circle': central_jet_od}

    def check_fuel_positions(self):
        fuel_positions_cubic = []
        for coord in self.cubic_coords:
            if is_fuel_position_cubic(coord[0], coord[1]):
                fuel_positions_cubic.append(coord)
        return fuel_positions_cubic

    def export_to_dxf(self, air_holes, fuel_holes, central_jet, filename):
        doc = ezdxf.new()
        msp = doc.modelspace()

        air_layer = doc.layers.new(name='AirHoles', dxfattribs={'color': 1})
        for hexagon in air_holes:
            msp.add_lwpolyline(hexagon.exterior.coords, dxfattribs={'layer': 'AirHoles'})

        fuel_layer = doc.layers.new(name='FuelHoles', dxfattribs={'color': 2})
        for fuel_hole in fuel_holes:
            circle = fuel_hole['circle']
            center = circle.centroid
            radius = center.distance(shapely.geometry.Point(circle.exterior.coords[0]))
            msp.add_circle(center=(center.x, center.y), radius=radius, dxfattribs={'layer': 'FuelHoles'})

            # Add fuel hole OD
            od_circle = fuel_hole['od_circle']
            od_center = od_circle.centroid
            od_radius = od_center.distance(shapely.geometry.Point(od_circle.exterior.coords[0]))
            msp.add_circle(center=(od_center.x, od_center.y), radius=od_radius, dxfattribs={'layer': 'FuelHoles'})

        jet_layer = doc.layers.new(name='CentralJet', dxfattribs={'color': 3})
        center = central_jet['circle'].centroid
        radius = center.distance(shapely.geometry.Point(central_jet['circle'].exterior.coords[0]))
        msp.add_circle(center=(center.x, center.y), radius=radius, dxfattribs={'layer': 'CentralJet'})

        od_layer = doc.layers.new(name='CentralJetOD', dxfattribs={'color': 4})
        center = central_jet['od_circle'].centroid
        od_radius = center.distance(shapely.geometry.Point(central_jet['od_circle'].exterior.coords[0]))
        msp.add_circle(center=(center.x, center.y), radius=od_radius, dxfattribs={'layer': 'CentralJetOD'})

        doc.saveas(filename)

    def calculate_hole_statistics(self, air_holes, fuel_holes):
        # Calculate fuel hole area
        fuel_hole_area = len(fuel_holes) * (math.pi * (self.pilot_fuel_ID / 2) ** 2)

        # Calculate total hexagon area inside the boundary, including partial hexagons
        total_hex_area = sum(hexagon.intersection(self.boundary_polygon).area for hexagon in air_holes)

        # Subtract the area of the fuel holes (using outer diameter)
        total_fuel_hole_od_area = len(fuel_holes) * (math.pi * (self.pilot_fuel_OD / 2) ** 2)
        total_hex_area -= total_fuel_hole_od_area

        # Subtract the area of the central jet (using outer diameter)
        central_jet_od_area = math.pi * (self.jet_OD / 2) ** 2
        total_hex_area -= central_jet_od_area

        # Calculate air hole area
        air_hole_area = total_hex_area

        # Calculate air to fuel area ratio
        air_to_fuel_area_ratio = air_hole_area / fuel_hole_area if fuel_hole_area > 0 else float('inf')

        # Subtract the number of fuel holes from the air hole count
        air_hole_number = len(air_holes) - len(fuel_holes) - 1 # Subtract 1 for the central jet

        return {
            'air_hole_number': air_hole_number,
            'air_hole_area': air_hole_area,
            'fuel_hole_number': len(fuel_holes),
            'fuel_hole_area': fuel_hole_area,
            'air_to_fuel_area_ratio': air_to_fuel_area_ratio
        }


def honeycomb_generator(generate_dxf=False):
    params = GeometryParams()
    hex_grid = HexGrid(params)

    fuel_positions_cubic = hex_grid.check_fuel_positions()
    fuel_positions_cartesian = [cubic_to_cartesian(q, r, s, hex_grid.center_distance / math.sqrt(3)) for q, r, s in
                                fuel_positions_cubic]

    central_jet = hex_grid.generate_central_jet()
    air_holes = hex_grid.generate_air_holes([], central_jet)
    fuel_holes = hex_grid.generate_fuel_holes(fuel_positions_cartesian)

    if generate_dxf:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils')
        filename = os.path.join(data_dir, f'geometry_{datetime.now().strftime("%Y%m%d_%H%M%S")}.dxf')
        hex_grid.export_to_dxf(air_holes, fuel_holes, central_jet, filename)

    stats = hex_grid.calculate_hole_statistics(air_holes, fuel_holes)
    return stats


def get_hole_coordinates():
    params = GeometryParams()
    hex_grid = HexGrid(params)

    central_jet = hex_grid.generate_central_jet()
    air_holes = hex_grid.generate_air_holes([], central_jet)
    fuel_positions_cubic = hex_grid.check_fuel_positions()
    fuel_positions_cartesian = [cubic_to_cartesian(q, r, s, hex_grid.center_distance / math.sqrt(3)) for q, r, s in
                                fuel_positions_cubic]
    fuel_holes = hex_grid.generate_fuel_holes(fuel_positions_cartesian)

    return air_holes, fuel_holes, central_jet


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate hex grid and optionally export to DXF.')
    parser.add_argument('--generate-dxf', action='store_true', help='Generate DXF file')
    args = parser.parse_args()

    stats = honeycomb_generator(generate_dxf=args.generate_dxf)

    print(stats)
