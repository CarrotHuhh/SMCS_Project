"""
Batch experiment configurations.
Generates all combinations of: bound (a, b) pairs and bound (penalty_mapping, exp_type) pairs
"""

# Define parameter grids

# Bound pairs: (a, b)
ab_pairs = [
    (1, 2),
    (2, 1),
    (5, 1),
    (10, 1),
    (1, 1),
]

# Bound pairs: (penalty_mapping, exp_type)
# These are tied together - each exp_type has a specific penalty_mapping
bound_pairs = [
    # (
    #     {'CP': 9, 'CO': 3, 'NP': 3, 'NO': 1},  # penalty_mapping
    #     'CNPO'  # exp_type
    # ),
    # (
    #     {'CP': 3, 'CO': 3, 'NP': 1, 'NO': 1},
    #     'CN'
    # ),
    # (
    #     {'CP': 3, 'CO': 1, 'NP': 3, 'NO': 1},
    #     'PO'
    # ),
    (
        {'CP': 1, 'CO': 1, 'NP': 1, 'NO': 1},
        'Baseline'
    ),
    
]


def generate_experiments():
    """Generate all combinations of bound (a, b) pairs and bound (penalty_mapping, exp_type) pairs"""
    experiments = []
    
    # For each bound (a, b) pair
    for a, b in ab_pairs:
        # For each bound (penalty_mapping, exp_type) pair
        for penalty_mapping, exp_type in bound_pairs:
            config_dict = {
                'a': a,
                'b': b,
                'penalty_mapping': penalty_mapping,
                'exp_type': exp_type,
            }
            
            # Generate experiment name
            exp_name = f"{exp_type}_A{a}_B{b}"
            
            experiments.append((exp_name, config_dict))
    
    return experiments


# Generate all experiments
experiments = generate_experiments()
