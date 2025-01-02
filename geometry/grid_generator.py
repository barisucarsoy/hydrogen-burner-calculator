import math


class HexagonalGridGenerator:
    """Generates a hexagonal grid coordinates for a given boundary and center distance
        Grid is calculated in cubic coordinates (q,r,s) where q + r + s = 0.
        ceil,Boundary/2 is the maximum distance from the center point to outermost point in the grid.
        Center distance is the distance between two adjacent point.
    """

    def __init__(self, center_distance, boundary):
        self.center_distance = center_distance
        self.boundary = boundary

    def generate_coordinates(self):
        grid_radius = math.ceil((self.boundary / 2) / self.center_distance)
        size = self.center_distance / math.sqrt(3)  # radius of the outer circle of the hexagon

        cubic_coordinates = []
        cartesian_coordinates = []
        for q in range(-grid_radius, grid_radius + 1):
            for r in range(max(-grid_radius, -q - grid_radius), min(grid_radius, -q + grid_radius) + 1):
                s = -q - r
                cubic_coordinates.append((q, r, s))

                # convert cubic to cartesian
                cart_x = size * ((q * math.sqrt(3)) + (r * math.sqrt(3) / 2))
                cart_y = size * (3 / 2 * r)

                cartesian_coordinates.append((cart_x, cart_y))

        return {
            'cubic_coordinates': cubic_coordinates,
            'cartesian_coordinates': cartesian_coordinates
        }
