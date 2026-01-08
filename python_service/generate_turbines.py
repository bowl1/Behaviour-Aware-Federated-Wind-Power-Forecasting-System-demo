import json
import os
import random
from datetime import datetime

def generate_turbines():
    """
    Generate 400 wind turbines distributed across 7 clusters with geographic distribution.
    """
    
    # Define cluster distributions and geographic regions
    # All turbines on Zealand (Sjælland), Denmark
    # Zealand coordinates: lat 54.5-56.5°N, lon 11.5-15.5°E
    clusters_config = {
        0: {"count": 49, "name": "Zealand North", "lon": (12.0, 13.5), "lat": (55.8, 56.4)},
        1: {"count": 12, "name": "Zealand Northeast", "lon": (13.5, 15.2), "lat": (55.5, 56.3)},
        2: {"count": 4, "name": "Zealand East", "lon": (14.5, 15.2), "lat": (54.9, 55.5)},
        3: {"count": 246, "name": "Zealand Central", "lon": (11.8, 14.2), "lat": (54.8, 55.7)},
        4: {"count": 74, "name": "Zealand West", "lon": (11.5, 12.5), "lat": (55.1, 56.1)},
        5: {"count": 6, "name": "Zealand Southwest", "lon": (11.5, 12.3), "lat": (54.6, 55.2)},
        6: {"count": 9, "name": "Zealand South", "lon": (12.3, 14.0), "lat": (54.5, 55.1)},
    }
    
    turbines = []
    turbine_id = 0
    
    # Generate turbines for each cluster
    for cluster_id in range(7):
        config = clusters_config[cluster_id]
        count = config["count"]
        lon_min, lon_max = config["lon"]
        lat_min, lat_max = config["lat"]
        
        for _ in range(count):
            turbine = {
                "turbineId": f"T{turbine_id:03d}",
                "clusterId": cluster_id,
                "latitude": round(random.uniform(lat_min, lat_max), 6),
                "longitude": round(random.uniform(lon_min, lon_max), 6),
                "capacity": round(random.uniform(2.0, 4.5), 2)
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
        "capacity_range_mw": [2.0, 4.5]
    }
    
    # Create output structure
    output_data = {
        "metadata": metadata,
        "turbines": turbines
    }
    
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
