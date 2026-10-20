import json
import copy
import os

input_file = "AL-7332_99B-15848-3D_3_97-47941S_4_clean_crop2.geojson"
output_file = (
    "AL-7332_99B-15848-3D_3_97-47941S_4_clean_crop2_clean.geojson"
)

# ============================================================
# READ INPUT
# ============================================================
print("Reading:", input_file)
with open(input_file, "r") as fh:
    data = json.load(fh)

if data.get("type") != "FeatureCollection":
    raise ValueError("Input is not a GeoJSON FeatureCollection")

features = data["features"]
print("Input features:", len(features))

# ============================================================
# CONVERT MULTIPOLYGONS TO POLYGONS
# ============================================================
new_features = []
original_polygons = 0
original_multipolygons = 0
multipolygon_components = 0

for index, feature in enumerate(features):
    geometry = feature.get("geometry")
    original_id = feature.get("id", index)

    if geometry is None:
        raise ValueError(f"Feature {original_id} has no geometry")

    geometry_type = geometry.get("type")

    # --------------------------------------------------------
    # Existing Polygon
    # --------------------------------------------------------
    if geometry_type == "Polygon":
        new_features.append(copy.deepcopy(feature))
        original_polygons += 1

    # --------------------------------------------------------
    # MultiPolygon: split every component into a separate Polygon
    # --------------------------------------------------------
    elif geometry_type == "MultiPolygon":
        original_multipolygons += 1
        polygons = geometry["coordinates"]

        for component_number, polygon_coordinates in enumerate(polygons, start=1):
            new_feature = copy.deepcopy(feature)

            # Give each resulting polygon a unique ID
            new_feature["id"] = f"{original_id}_part_{component_number}"
            new_feature["geometry"] = {
                "type": "Polygon",
                "coordinates": polygon_coordinates,
            }

            new_features.append(new_feature)
            multipolygon_components += 1

    else:
        raise ValueError(
            f"Unsupported geometry type: {geometry_type} "
            f"(feature ID: {original_id})"
        )

# ============================================================
# CREATE NEW GEOJSON
# ============================================================
output_data = {
    "type": "FeatureCollection",
    "features": new_features,
}

with open(output_file, "w") as fh:
    json.dump(output_data, fh, separators=(",", ":"))

# ============================================================
# SUMMARY
# ============================================================
print("\n================================================")
print("CONVERSION SUMMARY")
print("================================================")
print("Original features:", len(features))
print("Original Polygon features:", original_polygons)
print("Original MultiPolygon features:", original_multipolygons)
print("MultiPolygon components:", multipolygon_components)
print("Output features:", len(new_features))

# ============================================================
# CHECK OUTPUT GEOMETRIES
# ============================================================
polygon_count = 0
multipolygon_count = 0
closed_rings = 0
open_rings = 0
invalid_coordinates = 0
xs = []
ys = []

for feature in new_features:
    geometry = feature["geometry"]

    if geometry["type"] == "Polygon":
        polygon_count += 1
    elif geometry["type"] == "MultiPolygon":
        multipolygon_count += 1
    else:
        raise ValueError(f"Unexpected geometry type: {geometry['type']}")

    # --------------------------------------------------------
    # Polygon validation
    # --------------------------------------------------------
    if geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]:
            if len(ring) < 4:
                raise ValueError(
                    f"Polygon {feature.get('id')} has fewer than 4 coordinates"
                )

            if ring[0] == ring[-1]:
                closed_rings += 1
            else:
                open_rings += 1

            for point in ring:
                if (
                    not isinstance(point, list)
                    or len(point) < 2
                    or not isinstance(point[0], (int, float))
                    or not isinstance(point[1], (int, float))
                ):
                    invalid_coordinates += 1
                else:
                    xs.append(point[0])
                    ys.append(point[1])

# ============================================================
# FINAL REPORT
# ============================================================
print("\n================================================")
print("OUTPUT VALIDATION")
print("================================================")
print("Polygon:", polygon_count)
print("MultiPolygon:", multipolygon_count)
print("Closed rings:", closed_rings)
print("Open rings:", open_rings)
print("Invalid coordinates:", invalid_coordinates)

if xs and ys:
    print("\nCoordinate range:")
    print("X:", min(xs), "to", max(xs))
    print("Y:", min(ys), "to", max(ys))
else:
    print("\nNo valid coordinates found.")

# ============================================================
# FINAL CHECK
# ============================================================
expected_features = original_polygons + multipolygon_components

print("\nExpected output features:", expected_features)
print("Actual output features:  ", len(new_features))

if multipolygon_count != 0:
    raise ValueError("ERROR: MultiPolygon geometries remain!")

if len(new_features) != expected_features:
    raise ValueError("ERROR: Unexpected number of output features!")

if open_rings != 0:
    raise ValueError("ERROR: Some polygon rings are not closed!")

if invalid_coordinates != 0:
    raise ValueError("ERROR: Invalid coordinates detected!")

print("\n================================================")
print("PASS")
print("================================================")
print("The output contains Polygon geometries only.")
print("All polygon rings are closed.")
print("All coordinates are numeric.")
print("Original properties were preserved.")
print("Original file was NOT modified.")
print("\nOutput file:")
print(os.path.abspath(output_file))