"""
Cluster behavioral profiles derived from federated learning analysis.
Each cluster exhibits distinct power output, volatility, downtime, and ramp characteristics.
"""

# Cluster characteristics from analysis.md - behavior profiles for each cluster
CLUSTER_PROFILES = {
    0: {
        "power_level": 2.34,
        "volatility": 2.34,
        "downtime": 0.067,
        "ramp": 2.35,
        "name": "High Power",
        "description": "High power output, high volatility, minimal downtime"
    },
    2: {
        "power_level": 1.71,
        "volatility": 1.81,
        "downtime": 0.110,
        "ramp": 4.77,
        "name": "Ramp-Dominated",
        "description": "Strong power changes, ramp-dominated behavior"
    },
    3: {
        "power_level": -0.30,
        "volatility": -0.29,
        "downtime": 0.147,
        "ramp": 0.02,
        "name": "Stable Baseline",
        "description": "Most reliable, stable baseline performance"
    },
    4: {
        "power_level": -0.63,
        "volatility": -0.70,
        "downtime": 0.316,
        "ramp": 0.25,
        "name": "Mid-Risk",
        "description": "Lower output, frequent downtime, mid-risk"
    },
    5: {
        "power_level": 0.53,
        "volatility": 0.82,
        "downtime": 0.090,
        "ramp": 0.72,
        "name": "Promising",
        "description": "Moderate volatility, promising performance"
    },
    6: {
        "power_level": -0.33,
        "volatility": -0.29,
        "downtime": 0.240,
        "ramp": 1.17,
        "name": "Mildly Unstable",
        "description": "Frequent ramp-ups, mildly unstable"
    }
}
