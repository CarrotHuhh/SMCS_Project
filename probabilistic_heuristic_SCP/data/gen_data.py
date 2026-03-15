import os
import itertools

def generate_sts_triples(k):
    """
    遞迴生成 Steiner Triple System (STS) 的三元組 (Triples)
    k: 代表生成 3^k 個集合 (變數)
    """
    # 基礎條件：A_3 矩陣，只有 1 個三元組 (1, 2, 3)
    if k == 1:
        return [(1, 2, 3)]
    
    # 取得前一個規模 n 的三元組集合
    prev_triples = generate_sts_triples(k - 1)
    n_prev = 3 ** (k - 1)
    
    new_triples = []
    
    # 幫助函數：將 (i, j) 二維索引映射回 1 到 3n 的一維陣列索引
    def get_idx(i, r):
        return 3 * (i - 1) + r

    # 規則 1：r = s = t，且 {i, j, k} 是 A_n 的一個 triple
    for (i, j, k_idx) in prev_triples:
        for r in [1, 2, 3]:
            new_triples.append((get_idx(i, r), get_idx(j, r), get_idx(k_idx, r)))
            
    # 規則 2：i = j = k，且 {r, s, t} = {1, 2, 3}
    for i in range(1, n_prev + 1):
        new_triples.append((get_idx(i, 1), get_idx(i, 2), get_idx(i, 3)))
        
    # 規則 3：{i, j, k} 是 A_n 的一個 triple，且 {r, s, t} 包含 {1, 2, 3} 的所有排列
    perms = list(itertools.permutations([1, 2, 3]))
    for (i, j, k_idx) in prev_triples:
        for (r, s, t) in perms:
            new_triples.append((get_idx(i, r), get_idx(j, s), get_idx(k_idx, t)))
            
    return new_triples

def create_steiner_matrix_file(k, filename=None):
    """
    生成矩陣並寫入 txt 檔案 (符合 OR-Library 格式)
    """
    n_subsets = 3 ** k
    triples = generate_sts_triples(k)
    n_attributes = len(triples)
    
    if filename is None:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"A{n_subsets}_data.txt")


    with open(filename, 'w') as f:
        # 第一行：屬性數量 (限制式列數), 集合數量 (變數行數)
        f.write(f"{n_attributes} {n_subsets}\n")
        
        # 第二行：每個集合的 Cost（文獻為無權重，故全設為 1）
        costs = " ".join(["1"] * n_subsets)
        f.write(f"{costs}\n")
        
        # 第三行開始：描述每個限制條件被哪些集合覆蓋
        for triple in triples:
            f.write("3\n") # Steiner triple 每個限制條件剛好被 3 個集合覆蓋
            # 將 tuple 轉成字串並用空白隔開
            f.write(f"{triple[0]} {triple[1]} {triple[2]}\n")
            
    print(f"成功生成檔案: {filename}")
    print(f"矩陣規模: {n_attributes} 個限制式 (Rows), {n_subsets} 個集合 (Columns)")
    print("-" * 40)

# ==========================================
# 執行範例：生成文獻中提到的各種規模矩陣
# ==========================================
if __name__ == "__main__":
    try:
        # 讓使用者輸入 k，決定變數數量 (3^k)
        k_input = input("請輸入 k 值 (變數數量將為 3^k, 例如 k=2 -> 9個變數): ")
        k = int(k_input)
        create_steiner_matrix_file(k)
    except ValueError:
        print("輸入錯誤：請輸入整數 k")