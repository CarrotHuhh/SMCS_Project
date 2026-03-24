#%%
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

def analyze_experiment_results_cn(folder_path='../model/results'):
    file_pattern = os.path.join(folder_path, "CN_*.json")
    files = glob.glob(file_pattern)
    
    if not files:
        print("找不到符合 'CN_*.json' 規則的檔案。")
        return

    all_data = []

    for file_path in files:
        filename = os.path.basename(file_path)
        # 從檔名正則匹配 N 值與百分比 (例如 N124 和 60pct)
        n_match = re.search(r'N(\d+)', filename)
        pct_match = re.search(r'(\d+)pct', filename)
        
        n_val = int(n_match.group(1)) if n_match else 0
        pct_label = f"{pct_match.group(1)}%" if pct_match else "Unknown"

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 統計與計算覆蓋率
            p_vector = data['input_config']['penalty_vector']
            total_core = sum(1 for p in p_vector if p == 3)
            total_normal = sum(1 for p in p_vector if p == 1)
            
            stats = data['output_results']['statistics_four_catagories']
            # 注意：這裡 CP/CO 是被取消的 Core 數量
            cancelled_core = stats.get('CP', 0) + stats.get('CO', 0)
            cancelled_normal = stats.get('NP', 0) + stats.get('NO', 0)
            
            core_cov = ((total_core - cancelled_core) / total_core * 100)
            normal_cov = ((total_normal - cancelled_normal) / total_normal * 100)
            
            all_data.append({
                "N": n_val,
                "Pct": pct_label,
                "X_Label": f"{pct_label}\n(N={n_val})",
                "Core_Coverage": core_cov,
                "Normal_Coverage": normal_cov
            })

    # 排序：從人力少到多 (或多到少，依你喜好)
    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    
    # 2. 繪圖
    plt.figure(figsize=(10, 6), dpi=100)
    plt.plot(df['X_Label'], df['Core_Coverage'], marker='s', label='Core Routes', 
             color='#2E7D32', linewidth=2.5, markersize=8)
    plt.plot(df['X_Label'], df['Normal_Coverage'], marker='o', label='Normal Routes', 
             color='#C62828', linewidth=2.5, markersize=8, linestyle='--')

    # plt.title('6.1 Spatial Priority', fontsize=14, fontweight='bold')
    plt.xlabel('Driver Supply Percentage (Actual N)', fontsize=12)
    plt.ylabel('Coverage Rate (%)', fontsize=12)
    plt.ylim(0, 110)
    plt.grid(True, axis='y', linestyle=':', alpha=0.7)
    plt.legend(loc='lower right', frameon=True)

    # 數據標籤
    for i, row in df.iterrows():
        plt.text(row['X_Label'], row['Core_Coverage'] + 3, f"{row['Core_Coverage']:.1f}%", 
                 ha='center', color='#2E7D32', fontweight='bold')
        plt.text(row['X_Label'], row['Normal_Coverage'] - 7, f"{row['Normal_Coverage']:.1f}%", 
                 ha='center', color='#C62828', fontweight='bold')

    plt.tight_layout()
    plt.show()

    print("--- CN 實驗數據詳細分析 ---")
    print(df.drop(columns=['X_Label']).to_string(index=False))

def analyze_experiment_results_po(folder_path='../model/results'):
    file_pattern = os.path.join(folder_path, "CN_*.json")
    files = glob.glob(file_pattern)
    
    if not files:
        print("找不到符合 'PO_*.json' 規則的檔案。")
        return

    all_data = []

    for file_path in files:
        filename = os.path.basename(file_path)
        # 從檔名正則匹配 N 值與百分比 (例如 N124 和 60pct)
        n_match = re.search(r'N(\d+)', filename)
        pct_match = re.search(r'(\d+)pct', filename)
        
        n_val = int(n_match.group(1)) if n_match else 0
        pct_label = f"{pct_match.group(1)}%" if pct_match else "Unknown"

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 統計與計算覆蓋率
            p_vector = data['input_config']['penalty_vector']
            total_peak = sum(1 for p in p_vector if p == 3)
            total_non_peak = sum(1 for p in p_vector if p == 1)
            
            stats = data['output_results']['statistics_four_catagories']
            # 注意：這裡 CP/CO 是被取消的 Core 數量
            cancelled_peak = stats.get('CP', 0) + stats.get('NP', 0)
            cancelled_non_peak = stats.get('CO', 0) + stats.get('NO', 0)
            
            core_cov = ((total_peak - cancelled_peak) / total_peak * 100)
            normal_cov = ((total_non_peak - cancelled_non_peak) / total_non_peak * 100)
            
            all_data.append({
                "N": n_val,
                "Pct": pct_label,
                "X_Label": f"{pct_label}\n(N={n_val})",
                "Core_Coverage": core_cov,
                "Normal_Coverage": normal_cov
            })

    # 排序：從人力少到多 (或多到少，依你喜好)
    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    
    # 2. 繪圖
    plt.figure(figsize=(10, 6), dpi=100)
    plt.plot(df['X_Label'], df['Core_Coverage'], marker='s', label='Peak hours', 
             color='#2E7D32', linewidth=2.5, markersize=8)
    plt.plot(df['X_Label'], df['Normal_Coverage'], marker='o', label='Off-peak hours', 
             color='#C62828', linewidth=2.5, markersize=8, linestyle='--')

    # plt.title('6.2 Temporal Priority', fontsize=14, fontweight='bold')
    plt.xlabel('Driver Supply Percentage (Actual N)', fontsize=12)
    plt.ylabel('Coverage Rate (%)', fontsize=12)
    plt.ylim(0, 110)
    plt.grid(True, axis='y', linestyle=':', alpha=0.7)
    plt.legend(loc='lower right', frameon=True)

    # 數據標籤
    for i, row in df.iterrows():
        plt.text(row['X_Label'], row['Core_Coverage'] + 3, f"{row['Core_Coverage']:.1f}%", 
                 ha='center', color='#2E7D32', fontweight='bold')
        plt.text(row['X_Label'], row['Normal_Coverage'] - 7, f"{row['Normal_Coverage']:.1f}%", 
                 ha='center', color='#C62828', fontweight='bold')

    plt.tight_layout()
    plt.show()

    print("--- PO 實驗數據詳細分析 ---")
    print(df.drop(columns=['X_Label']).to_string(index=False))

def analyze_experiment_results_cnpo(folder_path='../model/results'):
    # 1. 搜尋所有 CNPO_ 開頭的 JSON 檔案
    file_pattern = os.path.join(folder_path, "CNPO_*.json")
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"找不到符合 'CNPO_*.json' 規則的檔案於路徑: {folder_path}")
        return

    all_data = []

    for file_path in files:
        filename = os.path.basename(file_path)
        # 從檔名提取 N 值與百分比
        n_match = re.search(r'N(\d+)', filename)
        pct_match = re.search(r'(\d+)pct', filename)
        
        n_val = int(n_match.group(1)) if n_match else 0
        pct_label = f"{pct_match.group(1)}%" if pct_match else "Unknown"

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 取得權重對照表 (假設 CNPO 中 CP, CO, NP, NO 權重各不相同)
            mapping = data['input_config']['penalty_mapping']
            p_vector = data['input_config']['penalty_vector']
            
            # 計算分母 (各類別原始總班次數量)
            # 透過 penalty_vector 裡面的權重值來區分該班次屬於哪一類
            totals = {
                "CP": sum(1 for p in p_vector if p == mapping.get('CP')),
                "CO": sum(1 for p in p_vector if p == mapping.get('CO')),
                "NP": sum(1 for p in p_vector if p == mapping.get('NP')),
                "NO": sum(1 for p in p_vector if p == mapping.get('NO'))
            }
            
            # 取得分子 (各類別被取消的班次數量)
            stats = data['output_results']['statistics_four_catagories']
            
            # 計算覆蓋率 (Service Level)
            results = {"N": n_val, "X_Label": f"{pct_label}\n(N={n_val})"}
            for cat in ["CP", "CO", "NP", "NO"]:
                cancelled = stats.get(cat, 0)
                total = totals[cat]
                results[f"{cat}_Coverage"] = ((total - cancelled) / total * 100) if total > 0 else 0
            
            all_data.append(results)

    # 按人力規模排序 (由少到多)
    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    
    # 2. 視覺化繪圖
    plt.figure(figsize=(12, 7), dpi=100)
    
    # 設定四條線的樣式
    styles = {
        "CP_Coverage": {"label": "Core-Peak (CP)", "color": "#1B5E20", "marker": "s", "ls": "-"},
        "CO_Coverage": {"label": "Core-Off-peak (CO)", "color": "#4CAF50", "marker": "x", "ls": "--"},
        "NP_Coverage": {"label": "Normal-Peak (NP)", "color": "#B71C1C", "marker": "o", "ls": "-"},
        "NO_Coverage": {"label": "Normal-Off-peak (NO)", "color": "#E57373", "marker": "v", "ls": "--"}
    }

    for col, style in styles.items():
        plt.plot(df['X_Label'], df[col], label=style['label'], color=style['color'], 
                 marker=style['marker'], linestyle=style['ls'], linewidth=2.5, markersize=8)

    # 圖表裝飾
    # plt.title('6.3 Synergistic Effects of Spatio-Temporal Weighting', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Driver Supply Percentage (Actual N)', fontsize=12)
    plt.ylabel('Service Coverage Rate (%)', fontsize=12)
    plt.ylim(-5, 110)
    plt.grid(True, axis='y', linestyle=':', alpha=0.7)
    plt.legend(loc='lower right', bbox_to_anchor=(1, 0.15), frameon=True, fontsize=10)

    # 數據標註 (為了畫面整潔，僅標註頭尾或重要點位)
    for col in styles.keys():
        for i, row in df.iterrows():
            plt.text(row['X_Label'], row[col] + 2, f"{row[col]:.0f}%", ha='center', fontsize=8)

    plt.tight_layout()
    plt.show()

    print("--- CNPO 實驗數據詳細分析 ---")
    print(df.drop(columns=['X_Label']).to_string(index=False))

#%%
if __name__ == "__main__":
    analyze_experiment_results_cn()
    analyze_experiment_results_po()
    analyze_experiment_results_cnpo()
