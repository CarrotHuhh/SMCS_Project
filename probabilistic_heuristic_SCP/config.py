# 以下值在實驗中是固定的
N_iterations=500   # N = 迭代次數 (論文中提到這決定了演算法的執行時間與找最佳解的機率)
alpha_value=0.1   # alpha = 隨機性參數 (0 到 1 之間)。越小每一輪會選到越好的

data_filename = "data/coverage_matrix_1_3_28_73.txt"
penalty_csv_filename = "data/PoW_category.csv"

# data_filename = "data/test_v1/coverage_matrix.txt"
# penalty_csv_filename = "data/test_v1/penalty.csv"

is_row_constraint = False
row_constraint_percentage = [1.0, 0.85, 0.75, 0.6]

# 以下參數會在 batch 被改動 ----------------------------------------------#
a = 1   # a: 被選進的 columns 總量的係數
b = 2   # b: 沒有被選的 rows 的 cost 總和的係數

# Penalty mapping for converting categories to numerical values
penalty_mapping = {'CP': 9, 'CO': 3, 'NP': 3, 'NO': 1}

# exp_type = CN or PO or CNPO
exp_type = 'CNPO'