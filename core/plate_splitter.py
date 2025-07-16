from pygplates.pygplates import PolygonOnSphere, PolylineOnSphere, PointOnSphere
from core.arc_geometry import get_arc_intersection
from core.metadata import MetaPoint

def split_plate_by_line(plate: PolygonOnSphere, line: PolylineOnSphere)-> list[PolygonOnSphere]:
    plate_points = plate.get_points()
    line_points = line.get_points()
    meta_points = []
    intersections = []

    for point in line_points:
        in_plate = plate.is_point_in_polygon(point)
        meta_points.append(MetaPoint(point, in_plate))
        if in_plate:
            if point in plate:
                intersections.append(point)

    new_plate_points: list[PointOnSphere] = plate_points[:]
    
    if plate.is_point_in_polygon(meta_points[0].point):
        if not meta_points[0].point in plate:
            return [plate]
    
    if plate.is_point_in_polygon(meta_points[-1].point):
        if not meta_points[-1].point in plate:
            return [plate]

    splitting_lines = []
    current_split_line = []

    # NOTE: This is a really rough fix
    points_with_intersection = []

    for i in range(len(meta_points)):
        m1 = meta_points[i]
        m2 = meta_points[(i + 1) % len(meta_points)]

        if m1.is_inside:
            current_split_line.append(m1.point)

        if m1.point in intersections:
            pass
        elif m2.point in intersections:
            if len(current_split_line) >= 1:
                current_split_line.append(m2.point)
                splitting_lines.append(current_split_line)
                current_split_line = []
        elif m1.is_inside != m2.is_inside:
            for j in range(len(plate_points)):
                p1 = plate_points[j]
                p2 = plate_points[(j+1) % len(plate_points)]
                intersect = get_arc_intersection(
                    m1.point.to_lat_lon_point(),
                    m2.point.to_lat_lon_point(),
                    p1.to_lat_lon_point(),
                    p2.to_lat_lon_point()
                )
                if intersect:
                    offset = points_with_intersection.count(p1)
                    points_with_intersection.append(p1)

                    new_plate_points.insert(new_plate_points.index(p1) + 1 + offset, intersect.to_point_on_sphere())
                    current_split_line.append(intersect.to_point_on_sphere())
                    if len(current_split_line) > 1:
                        splitting_lines.append(current_split_line)
                        current_split_line = []
                    intersections.append(intersect.to_point_on_sphere())
    
    if len(intersections) == 0:
        return [plate]

    points_traversed = []
    
    finished_plates = []
    plates_in_progress = []
    current_plate = []
    
    if len(current_split_line) != 0:
        splitting_lines.append(current_split_line)
    
    for point in new_plate_points:
        if point in intersections:
            splitting_line = next(filter(lambda l: point in l, splitting_lines))
            if point == splitting_line[0]:
                current_plate.extend(splitting_line)
            else:
                current_plate.extend(reversed(splitting_line))
            points_traversed.extend(splitting_line)

            # Change to another plate
            if current_plate[0] != current_plate[-1]:
                plates_in_progress.append(current_plate)
            else:
                finished_plates.append(current_plate)
            current_plate = next(filter(lambda plate: plate[-1] == point, plates_in_progress), [ point ])
            if current_plate in plates_in_progress:
                plates_in_progress.remove(current_plate)
        elif not point in points_traversed:
            current_plate.append(point)
            points_traversed.append(point)
    finished_plates.append(current_plate)

    for p in plates_in_progress:
        finished_plates.append(p)

    output_plates = []
    for plate in finished_plates:
        output_plates.append(PolygonOnSphere(plate))

    return output_plates