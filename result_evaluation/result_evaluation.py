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

    # 字體設定
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 11
    })

    plt.tight_layout()

    # 儲存為 PDF，建議設定 dpi 為 300 以上確保清晰度
    save_filename = "1_spatial_priority.pdf"
    plt.savefig(save_filename, format='pdf', bbox_inches='tight', dpi=300)
    print(f"圖表已成功儲存至: {save_filename}")

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


    # 字體設定
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 11
    })

    plt.tight_layout()

    # 儲存為 PDF，建議設定 dpi 為 300 以上確保清晰度
    save_filename = "2_temporal_priority.pdf"
    plt.savefig(save_filename, format='pdf', bbox_inches='tight', dpi=300)
    print(f"圖表已成功儲存至: {save_filename}")

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
        n_match = re.search(r'N(\d+)', filename)
        pct_match = re.search(r'(\d+)pct', filename)
        
        n_val = int(n_match.group(1)) if n_match else 0
        pct_label = f"{pct_match.group(1)}%" if pct_match else "Unknown"

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            mapping = data['input_config']['penalty_mapping']
            p_vector = data['input_config']['penalty_vector']
            
            totals = {
                "CP": sum(1 for p in p_vector if p == mapping.get('CP')),
                "CO": sum(1 for p in p_vector if p == mapping.get('CO')),
                "NP": sum(1 for p in p_vector if p == mapping.get('NP')),
                "NO": sum(1 for p in p_vector if p == mapping.get('NO'))
            }
            
            stats = data['output_results']['statistics_four_catagories']
            results = {"N": n_val, "X_Label": f"{pct_label}\n(N={n_val})"}
            for cat in ["CP", "CO", "NP", "NO"]:
                cancelled = stats.get(cat, 0)
                total = totals[cat]
                results[f"{cat}_Coverage"] = ((total - cancelled) / total * 100) if total > 0 else 0
            
            all_data.append(results)

    # 按人力規模排序 (由多到少)
    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    
    # --- 視覺化設定 ---
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 11
    })

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
    
    styles = {
        "CP_Coverage": {"label": "Core-Peak (CP)", "color": "#1B5E20", "marker": "s", "ls": "-"},
        "CO_Coverage": {"label": "Core-Off-peak (CO)", "color": "#4CAF50", "marker": "x", "ls": "--"},
        "NP_Coverage": {"label": "Normal-Peak (NP)", "color": "#B71C1C", "marker": "o", "ls": "-"},
        "NO_Coverage": {"label": "Normal-Off-peak (NO)", "color": "#E57373", "marker": "v", "ls": "--"}
    }

    # 繪製折線
    for col, s in styles.items():
        ax.plot(df['X_Label'], df[col], label=s['label'], color=s['color'], 
                 marker=s['marker'], linestyle=s['ls'], linewidth=2.5, markersize=8)

        # 數據標註
        for i, row in df.iterrows():
            ax.text(row['X_Label'], row[col] + 1.5, f"{row[col]:.0f}%", 
                    ha='center', fontsize=9, fontweight='bold', color=s['color'])

    # --- 座標軸優化 (解決你提到的問題) ---
    ax.set_ylim(0, 105)           # Y軸從0開始，切齊底部
    ax.set_xmargin(0.03)          # 縮減左右留白，讓圖表更緊湊
    
    ax.set_ylabel('Service Coverage Rate (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Driver Supply Percentage (Actual N)', fontsize=12, fontweight='bold')

    # 圖例：貼齊右下角邊緣
    ax.legend(loc='lower right', bbox_to_anchor=(1, 0), frameon=True, fontsize=10, shadow=False)

    ax.grid(True, axis='y', linestyle=':', alpha=0.6)
    ax.set_axisbelow(True) # 讓網格線在圖層最下方

    plt.tight_layout()

    # 儲存為 PDF，建議設定 dpi 為 300 以上確保清晰度
    save_filename = "3_synergistic.pdf"
    plt.savefig(save_filename, format='pdf', bbox_inches='tight', dpi=300)
    print(f"圖表已成功儲存至: {save_filename}")

    plt.show()

    print("--- CNPO 實驗數據詳細分析 ---")
    print(df.drop(columns=['X_Label']).to_string(index=False))

#%%
if __name__ == "__main__":
    analyze_experiment_results_cn()
    analyze_experiment_results_po()
    analyze_experiment_results_cnpo()
