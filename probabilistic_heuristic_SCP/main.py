import time
import os

from PHSCP import SetCover
import config

N_iterations = config.N_iterations
alpha_value = config.alpha_value
data_filename = config.data_filename
data_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_filename)

def main(data_filepath):
    # 1. 實例化演算法物件
    scp_solver = SetCover()

    # 2. 讀取資料集
    print(f"正在載入資料: {data_filepath} ...")
    try:
        scp_solver.load_data(data_filepath)
        print(f"載入成功！共有 {scp_solver.nr_atr} 個元素需要覆蓋，並有 {scp_solver.nr_subsets} 個候選集合。")
    except FileNotFoundError:
        print(f"找不到檔案 {data_filepath}，請確認檔案路徑。")
        return

    # 4. 執行演算法
    print(f"\n開始執行 Probabilistic Heuristic (N={N_iterations}, alpha={alpha_value})...")
    start_time = time.time()
    
    best_cost, best_sol = scp_solver.probabilistic_heuristic(N_iterations, alpha_value)
    
    end_time = time.time()

    # 5. 輸出結果
    print("\n" + "="*30)
    print("執行結果：")
    print(f"花費時間: {end_time - start_time:.4f} 秒")
    # 注意：這裡的 cost 已經被你改成回傳集合數量 (len) 了
    print(f"最少需要使用 {best_cost} 個集合來完成覆蓋。") 
    print(f"選用的集合編號 (Index 從 0 開始): {list(best_sol)}")
    print("="*30)

if __name__ == "__main__":
    main(data_filepath)