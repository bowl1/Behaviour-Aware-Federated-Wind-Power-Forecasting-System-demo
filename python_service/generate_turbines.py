import json
import os
import random
from datetime import datetime


def point_in_polygon(lon, lat, polygon):
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) + 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def sample_distributed_points(count, island_polygon, zone_bbox, min_dist):
    """
    Sample points with minimum spacing inside a cluster zone and island polygon.
    Falls back by gradually reducing min_dist if requested count is hard to fit.
    """
    lon_min, lon_max, lat_min, lat_max = zone_bbox
    points = []
    current_min_dist = min_dist

    while len(points) < count:
        added_before = len(points)

        for _ in range(12000):
            lat = random.uniform(lat_min, lat_max)
            lon = random.uniform(lon_min, lon_max)

            if not point_in_polygon(lon, lat, island_polygon):
                continue

            ok = True
            for p_lat, p_lon in points:
                if ((lat - p_lat) ** 2 + (lon - p_lon) ** 2) < (current_min_dist ** 2):
                    ok = False
                    break

            if ok:
                points.append((round(lat, 6), round(lon, 6)))
                if len(points) >= count:
                    break

        if len(points) == added_before:
            current_min_dist *= 0.9

        if current_min_dist < 0.003:
            raise RuntimeError(f"Unable to place {count} dispersed points in zone {zone_bbox}")

    return points


def generate_turbines():
    """
    Generate 400 wind turbines distributed across 7 clusters with geographic distribution.
    """

    # Rough coastline polygon of Zealand (lon, lat), used as land mask.
    zealand_polygon = [
        (11.18, 55.67),
        (11.28, 55.95),
        (11.55, 56.10),
        (11.95, 56.16),
        (12.28, 56.11),
        (12.56, 56.02),
        (12.74, 55.88),
        (12.83, 55.66),
        (12.80, 55.42),
        (12.72, 55.18),
        (12.58, 54.98),
        (12.30, 54.87),
        (11.96, 54.88),
        (11.73, 54.97),
        (11.54, 55.13),
        (11.38, 55.34),
        (11.23, 55.53),
    ]

    random.seed(42)

    # Cluster distributions and sampling zones (lon_min, lon_max, lat_min, lat_max).
    clusters_config = {
        0: {
            "count": 49,
            "name": "Zealand North",
            "zone": (11.78, 12.67, 55.78, 56.20),
            "min_dist": 0.018,
        },
        1: {
            "count": 12,
            "name": "Zealand Northeast",
            "zone": (12.35, 12.80, 55.72, 56.03),
            "min_dist": 0.03,
        },
        2: {
            "count": 4,
            "name": "Zealand East",
            "zone": (12.18, 12.65, 55.43, 55.73),
            "min_dist": 0.04,
        },
        3: {
            "count": 246,
            "name": "Zealand Central",
            "zone": (11.45, 12.60, 55.08, 55.86),
            "min_dist": 0.012,
        },
        4: {
            "count": 74,
            "name": "Zealand West",
            "zone": (11.20, 11.95, 55.20, 55.95),
            "min_dist": 0.017,
        },
        5: {
            "count": 6,
            "name": "Zealand Southwest",
            "zone": (11.60, 12.05, 54.95, 55.30),
            "min_dist": 0.035,
        },
        6: {
            "count": 9,
            "name": "Zealand South",
            "zone": (11.78, 12.35, 54.88, 55.20),
            "min_dist": 0.03,
        },
    }

    turbines = []
    turbine_id = 0

    # Generate turbines for each cluster
    for cluster_id in range(7):
        config = clusters_config[cluster_id]
        count = config["count"]
        points = sample_distributed_points(
            count=count,
            island_polygon=zealand_polygon,
            zone_bbox=config["zone"],
            min_dist=config["min_dist"],
        )

        for lat, lon in points:
            turbine = {
                "turbineId": f"T{turbine_id:03d}",
                "clusterId": cluster_id,
                "latitude": lat,
                "longitude": lon,
                "capacity": round(random.uniform(2.0, 4.5), 2),
            }
            turbines.append(turbine)
            turbine_id += 1

    # Shuffle turbines to mix clusters
    random.shuffle(turbines)

    # Create output directory if not exists
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    # Create metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_turbines": len(turbines),
        "cluster_distribution": {str(i): clusters_config[i]["count"] for i in range(7)},
        "regions": {str(i): clusters_config[i]["name"] for i in range(7)},
        "capacity_range_mw": [2.0, 4.5],
    }

    # Create output structure
    output_data = {"metadata": metadata, "turbines": turbines}

    # Save to JSON file
    output_path = os.path.join(output_dir, "turbines.json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"✓ Generated {len(turbines)} turbines")
    print(f"✓ Saved to: {output_path}")
    print(f"\nCluster Distribution:")
    for cluster_id in range(7):
        count = clusters_config[cluster_id]["count"]
        name = clusters_config[cluster_id]["name"]
        print(f"  Cluster {cluster_id} ({name}): {count} turbines")

if __name__ == "__main__":
    generate_turbines()
