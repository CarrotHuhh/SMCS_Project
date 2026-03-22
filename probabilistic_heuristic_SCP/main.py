import time
import os

from PHSCP import SetCover
import config

N_iterations = config.N_iterations
alpha_value = config.alpha_value
a = config.a
b = config.b
is_row_constraint = config.is_row_constraint
row_constraint_percentage = config.row_constraint_percentage
penalty_mapping = config.penalty_mapping
exp_type = config.exp_type

data_filename = config.data_filename
penalty_csv_filename = config.penalty_csv_filename
data_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_filename)
penalty_csv_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), penalty_csv_filename)

def main(data_filepath):
    # 1. Instantiate the algorithm object
    scp_solver = SetCover()

    # 2. Load dataset
    print(f"Loading data: {data_filepath} ...")
    try:
        scp_solver.load_data(data_filepath, penalty_csv_filepath, penalty_mapping)
        print(f"Load successful! There are {scp_solver.nr_atr} elements to cover and {scp_solver.nr_subsets} candidate subsets.")
    except FileNotFoundError:
        print(f"File not found: {data_filepath}. Please check the file path.")
        return

    # 4. Run algorithm
    print(f"\nStarting first run (no max columns limit) Probabilistic Heuristic (N={N_iterations}, alpha={alpha_value})...")
    start_time = time.time()
    
    best_cost, best_sol = scp_solver.probabilistic_heuristic(N_iterations, alpha_value, a, b)
    
    end_time = time.time()

    # 5. Output results
    print("\n" + "="*30)
    print("Results:")
    print(f"Elapsed time: {end_time - start_time:.4f} seconds")
    # Note: cost is now returned as the number of sets (len)
    print(f"Minimum number of sets needed for coverage: {len(best_sol)}") 
    print(f"Selected set indices (0-based): {list(best_sol)}")
    print("="*30)

    # Second round, with multiple row constraints
    # If row_constraint_percentage is a list, run for each value
    if isinstance(row_constraint_percentage, list):
        row_percentages = row_constraint_percentage
    else:
        row_percentages = [row_constraint_percentage]
    
    for idx, rc_pct in enumerate(row_percentages):
        print(f"\n--- Second run {idx+1}/{len(row_percentages)} (constraint ratio: {rc_pct}) ---")
        
        row_constraint = best_cost * rc_pct
        is_row_constraint = True
        
        print(f"Starting run with max columns limit {row_constraint} Probabilistic Heuristic (N={N_iterations}, alpha={alpha_value})...")
        start_time = time.time()
        
        best_cost_2, best_sol_2 = scp_solver.probabilistic_heuristic(N_iterations, alpha_value, a, b, is_row_constraint, row_constraint)
        
        end_time = time.time()

        print("\n" + "="*30)
        print("Results:")
        print(f"Elapsed time: {end_time - start_time:.4f} seconds")
        print(f"Minimum number of sets needed for coverage: {len(best_sol_2)}") 
        print(f"Selected set indices (0-based): {list(best_sol_2)}")
        print("="*30)

        # Save experiment results for this constraint
        print("\n" + "="*30)
        print(f"Saving experiment results (constraint: {rc_pct})...")
        
        # Generate exp_id
        matrix_name = data_filename.split('/')[-1].replace('.txt', '')
        exp_id = f"{exp_type}_A{a}_B{b}_N{int(row_constraint)}_{int(rc_pct * 100)}pct_{matrix_name}"
        
        # Create penalty vector (reading from categories if available)
        if hasattr(scp_solver, 'categories') and scp_solver.categories:
            penalty_vector = [penalty_mapping.get(cat.strip(), 1) for cat in scp_solver.categories]
        else:
            penalty_vector = [1] * scp_solver.nr_atr
        
        # Save the experiment results with penalty_mapping
        scp_solver.save_experiment_json(
            exp_id=exp_id,
            best_sol=best_sol_2,
            runtime_sec=end_time - start_time,
            alpha=alpha_value,
            a=a,
            b=b,
            n_iterations=N_iterations,
            penalty_vector=penalty_vector,
            matrix_file=matrix_name,
            row_constraint=row_constraint,
            best_cost=best_cost_2,
            penalty_mapping=penalty_mapping,
            data_filename=data_filename,
            penalty_csv_filename=penalty_csv_filename
        )
        
        print("="*30)

if __name__ == "__main__":
    main(data_filepath)