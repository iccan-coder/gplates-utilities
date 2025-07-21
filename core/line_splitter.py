from typing import List, Tuple
from pygplates.pygplates import PolylineOnSphere, PointOnSphere

from core.arc_geometry import get_arc_intersection

def split_lines(line_a: PolylineOnSphere, line_b: PolylineOnSphere) -> Tuple[List[PolylineOnSphere], List[PolylineOnSphere]]:
    if not line_a or not line_b:
        return [line_a], [line_b]

    intersections = []

    # Find and insert intersections
    new_a: List[PointOnSphere] = []
    new_b: List[PointOnSphere] = line_b[:]

    for i in range(len(line_a) - 1):
        a_1 = line_a[i]
        a_2 = line_a[i + 1]

        new_a.append(a_1)

        for j in range(len(line_b) - 1):
            b_1 = line_b[j]
            b_2 = line_b[j + 1]

            intersect = get_arc_intersection(
                a_1.to_lat_lon_point(),
                a_2.to_lat_lon_point(),
                b_1.to_lat_lon_point(),
                b_2.to_lat_lon_point()
            )
            if intersect:
                intersections.append(intersect.to_point_on_sphere())
                new_a.append(intersect.to_point_on_sphere())
                new_b.insert(new_b.index(b_1) + 1, intersect.to_point_on_sphere())
        
        if i == len(line_a) - 2:
            # At the end, make sure to append the last point
            new_a.append(a_2)

    # If no intersections found, return original lines here
    if len(intersections) == 0:
        return [line_a], [line_b]

    split_lines_a: List[PolylineOnSphere] = []
    split_lines_b: List[PolylineOnSphere] = []

    current_split_line: List[PointOnSphere] = []

    # Split line A by intersections
    for point in new_a:
        current_split_line.append(point)
        if point in intersections:
            split_lines_a.append(PolylineOnSphere(current_split_line))
            current_split_line = [point]
    if len(current_split_line) > 1:
        split_lines_a.append(PolylineOnSphere(current_split_line))
    
    # Split line B by intersections
    current_split_line = []
    for point in new_b:
        current_split_line.append(point)
        if point in intersections:
            split_lines_b.append(PolylineOnSphere(current_split_line))
            current_split_line = [point]
    if len(current_split_line) > 1:
        split_lines_b.append(PolylineOnSphere(current_split_line))
    
    return split_lines_a, split_lines_b