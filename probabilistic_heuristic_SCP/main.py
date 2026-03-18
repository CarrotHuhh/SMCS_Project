import time
import os
import json

from PHSCP import SetCover
import config

N_iterations = config.N_iterations
alpha_value = config.alpha_value
a = config.a
b = config.b
is_row_constraint = config.is_row_constraint
row_constraint_percentage = config.row_constraint_percentage

data_filename = config.data_filename
data_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_filename)

def main(data_filepath):
    # 1. Instantiate the algorithm object
    scp_solver = SetCover()

    # 2. Load dataset
    print(f"Loading data: {data_filepath} ...")
    try:
        scp_solver.load_data(data_filepath)
        print(f"Load successful! There are {scp_solver.nr_atr} elements to cover and {scp_solver.nr_subsets} candidate subsets.")
    except FileNotFoundError:
        print(f"File not found: {data_filepath}. Please check the file path.")
        return

    # 4. Run algorithm
    print(f"\nStarting first run (no max columns limit) Probabilistic Heuristic (N={N_iterations}, alpha={alpha_value})...")
    start_time_1 = time.time()
    
    best_cost, best_sol = scp_solver.probabilistic_heuristic(N_iterations, alpha_value, a, b)
    
    end_time_1 = time.time()
    runtime_1 = end_time_1 - start_time_1

    # 5. Output results
    print("\n" + "="*30)
    print("Results:")
    print(f"Elapsed time: {runtime_1:.4f} seconds")
    # Note: cost is now returned as the number of sets (len)
    print(f"Minimum number of sets needed for coverage: {len(best_sol)}") 
    print(f"Selected set indices (0-based): {list(best_sol)}")
    print("="*30)

    # Second round, with number of selected row constraint
    row_constraint = len(best_sol) * row_constraint_percentage

    is_row_constraint = True
    
    print(f"\nStarting second run (max columns limit {int(row_constraint)}) Probabilistic Heuristic (N={N_iterations}, alpha={alpha_value})...")
    start_time_2 = time.time()
    
    best_cost_2, best_sol_2 = scp_solver.probabilistic_heuristic(N_iterations, alpha_value, a, b, is_row_constraint, row_constraint)
    
    end_time_2 = time.time()
    runtime_2 = end_time_2 - start_time_2

    print("\n" + "="*30)
    print("Results:")
    print(f"Elapsed time: {runtime_2:.4f} seconds")
    # Note: cost is now returned as the number of sets (len)
    print(f"Minimum number of sets needed for coverage: {len(best_sol_2)}") 
    print(f"Selected set indices (0-based): {list(best_sol_2)}")
    print("="*30)

    # Save experiment results
    print("\n" + "="*30)
    print("Saving experiment results...")
    
    # Generate exp_id
    row_constraint_int = int(row_constraint + 0.5)
    row_constraint_percentage_100 = int(row_constraint_percentage * 100)

    matrix_name = data_filename.split('/')[-1].replace('.txt', '')
    exp_id = f"RUN_A{a}_B{b}_N{row_constraint_int}_{row_constraint_percentage_100}pct_{matrix_name}"
    
    # Create penalty vector (all ones for this heuristic)
    penalty_vector = [1] * scp_solver.nr_atr
    
    # Save the second run results
    scp_solver.save_experiment_json(exp_id=exp_id, best_sol=best_sol_2, runtime_sec=runtime_2, alpha=alpha_value, a=a, b=b, n_iterations=N_iterations, penalty_vector=penalty_vector, matrix_file=matrix_name, row_constraint=row_constraint, best_cost=best_cost_2)
    
    print("="*30)

if __name__ == "__main__":
    main(data_filepath)