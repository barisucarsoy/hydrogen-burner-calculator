import math
import shapely.geometry


def is_fuel_position_cubic(q, r):
    return (q, r) != (0, 0) and ((r % 4 == 0 and q % 2 == 0) or (r % 4 == 2 and q % 2 == 0))


def is_fuel_position_cartesian(self, x, y):
    i = round(y / self.row_height)
    j = round(x / self.center_distance - (0.5 if i % 2 else 0))
    return (i, j) != (0, 0) and ((i % 4 == 0 and j % 2 == 0) or (i % 4 == 2 and j % 2 == 1))


def cubic_to_cartesian(q, r, s, center_distance):
    """
    Convert cubic coordinates (q, r, s) to Cartesian coordinates (x, y) for a pointy-topped hexagonal grid.

    Parameters:
    q (int): Cubic coordinate q
    r (int): Cubic coordinate r
    s (int): Cubic coordinate s
    center_distance (float): Distance between the centers of adjacent hexagons

    Returns:
    tuple: Cartesian coordinates (x, y)
    """
    x = center_distance * (math.sqrt(3) * (q + r / 2))
    y = center_distance * (3 / 2 * r)
    return x, y


def generate_hexagon(center, radius):
    """
    Generate the vertices of a pointy-topped hexagon oriented with a vertex pointing upward.

    Parameters:
    center (tuple): The (x, y) coordinates of the center of the hexagon.
    radius (float): The radius of the hexagon.

    Returns:
    shapely.geometry.Polygon: A hexagon as a Shapely polygon.
    """
    # Start angle set to pi/2 so that the first vertex points straight up
    angle = math.pi / 2
    points = [
        (
            center[0] + radius * math.cos(angle + i * math.pi / 3),
            center[1] + radius * math.sin(angle + i * math.pi / 3)
        )
        for i in range(6)
    ]
    return shapely.geometry.Polygon(points)
