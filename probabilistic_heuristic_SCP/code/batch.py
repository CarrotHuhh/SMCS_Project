#!/usr/bin/env python3
"""
Simple batch experiment runner.
Directly imports and runs main with different config combinations.
"""

import sys
import os
from datetime import datetime

import config
from config_batch import experiments
import main

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def run_experiments():
    """Run all experiments"""
    
    print("\n" + "="*70)
    print("Batch Experiment Runner")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"Total experiments: {len(experiments) * 4}\n")
    
    # Create result directory
    result_dir = os.path.join(os.path.dirname(__file__), 'result')
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    successful = 0
    failed = 0
    
    for i, (exp_name, config_dict) in enumerate(experiments, 1):
        print(f"\n[{i}/{len(experiments)}] {exp_name}")
        print("-" * 70)
        
        try:
            # Update only the specified config parameters
            # Only: a, b, penalty_mapping, exp_type
            for key, value in config_dict.items():
                setattr(config, key, value)
                print(f"  {key} = {value}")
            
            # Update main module variables for the parameters that changed
            main.a = config.a
            main.b = config.b
            main.penalty_mapping = config.penalty_mapping
            main.exp_type = config.exp_type
            
            print()
            # Run main
            main.main(main.data_filepath)
            
            print(f"✓ {exp_name} completed successfully\n")
            successful += 1
            
        except Exception as e:
            print(f"✗ Error in {exp_name}: {e}\n")
            failed += 1
            import traceback
            traceback.print_exc()
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total:      {len(experiments)}")
    print(f"Success:    {successful}")
    print(f"Failed:     {failed}")
    print(f"End time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"Results saved to: ./result/\n")


if __name__ == "__main__":
    run_experiments()
