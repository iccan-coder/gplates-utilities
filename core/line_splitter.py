from typing import List, Tuple
from pygplates.pygplates import PolylineOnSphere, PointOnSphere, Feature, FeatureCollection, RotationModel, ReconstructSnapshot

from core.arc_geometry import get_arc_intersection

def split_line_features(line_a: Feature, line_b: Feature, rotation_model: RotationModel, split_time: float) -> FeatureCollection:
    initial_feature_collection = FeatureCollection([line_a, line_b])
    snapshot = ReconstructSnapshot(initial_feature_collection, rotation_model, split_time)
    snapshot_lines = snapshot.get_reconstructed_geometries()

    new_collection = FeatureCollection()

    split_a, split_b = split_lines(snapshot_lines[0].get_reconstructed_geometry(), snapshot_lines[1].get_reconstructed_geometry())

    for idx, line in enumerate(split_a):
            feature = Feature.create_reconstructable_feature(
                line_a.get_feature_type(),
                line,
                f"{line_a.get_name()} [{idx}]",
                "",  # description
                (split_time, line_a.get_valid_time()[1]),
            )
            if line_a.get_reconstruction_method() == "ByPlateID":
                feature.set_reconstruction_plate_id(line_a.get_reconstruction_plate_id())
            else:
                # We are dealing with a half-stage rotation
                feature.set_left_plate(line_a.get_left_plate())
                feature.set_right_plate(line_a.get_right_plate())
            
            feature.set_reconstruction_method(line_a.get_reconstruction_method())
            new_collection.add(feature)

    for idx, line in enumerate(split_b):
        feature = Feature.create_reconstructable_feature(
            line_b.get_feature_type(),
            line,
            f"{line_b.get_name()} [{idx}]",
            "",  # description
            (split_time, line_b.get_valid_time()[1])
        )
        if line_b.get_reconstruction_method() == "ByPlateID":
            feature.set_reconstruction_plate_id(line_b.get_reconstruction_plate_id())
        else:
            # We are dealing with a half-stage rotation
            feature.set_left_plate(line_b.get_left_plate())
            feature.set_right_plate(line_b.get_right_plate())
        
        feature.set_reconstruction_method(line_b.get_reconstruction_method())
        new_collection.add(feature)
    
    return new_collection

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