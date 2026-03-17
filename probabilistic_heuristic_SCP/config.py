# N = 迭代次數 (論文中提到這決定了演算法的執行時間與找最佳解的機率)
# alpha = 隨機性參數 (0 到 1 之間)。
#   - 1.0 代表完全貪婪 (每次只選最好的)
#   - 0.0 代表完全隨機 (不看好壞隨便抽)
#   - 論文中通常測試 0.5 ~ 0.9 之間的值
N_iterations = 500
alpha_value = 1


# a: 被選進的 columns 總量的係數
# b: 沒有被選的 rows 的 cost 總和的係數
a = 1
b = 1

data_filename = "data/A9_data.txt"
# data_filename = "data/A27_data.txt"
# data_filename = "data/A81_data.txt"

is_row_constraint = False
row_constraint_percentage = 0.6