import pandas as pd
import os

def convert_csv_to_scp(csv_filepath, output_filepath):
    # Read CSV, skip first row and first column
    df = pd.read_csv(csv_filepath, header=0, index_col=0)
    
    # Convert to 0,1 matrix (assuming it's already 0s and 1s)
    matrix = df.values.tolist()
    
    # Get dimensions
    m = len(matrix)  # number of subsets (rows)
    n = len(matrix[0]) if m > 0 else 0  # number of elements (columns)
    
    with open(output_filepath, 'w') as f:
        # First line: m n
        f.write(f"{m} {n}\n")
        
        # Second line: costs (all 1s)
        costs = " ".join(["1"] * n)
        f.write(f"{costs}\n")
        
        # For each subset (row)
        for row in matrix:
            # Find indices where value is 1 (1-based)
            indices = [i+1 for i, val in enumerate(row) if val == 1]
            num_elements = len(indices)
            
            # Write number of elements
            f.write(f"{num_elements}\n")
            
            # Write the indices
            if indices:
                f.write(" ".join(map(str, indices)) + "\n")

if __name__ == "__main__":
    # Assuming the CSV is in the same directory
    csv_filepath = "data/coverage_matrix_1_3_28_73.csv"
    output_filepath = "data/coverage_matrix_1_3_28_73.txt"
    
    convert_csv_to_scp(csv_filepath, output_filepath)
    print(f"Converted {csv_filepath} to {output_filepath}")