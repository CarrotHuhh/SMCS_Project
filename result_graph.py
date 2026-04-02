import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from collections import Counter

def get_total_counts():
    with open('./duty_generation/output.csv', 'r', encoding='utf-8') as f:
        line = f.read().strip()
        codes = line.split(',')
        counts = Counter(codes)
        return {
            'CP': counts.get('CP', 0),
            'CO': counts.get('CO', 0),
            'NP': counts.get('NP', 0),
            'NO': counts.get('NO', 0)
        }

def setup_plot_style(title, xlabel, ylabel):
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 11
    })
    plt.figure(figsize=(10, 6), dpi=100)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.ylim(0, 110)
    plt.grid(True, axis='y', linestyle=':', alpha=0.7)

def save_and_clear(filename):
    plt.legend(loc='lower right', frameon=True, fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, format='pdf', bbox_inches='tight')
    print(f"Chart saved to: {filename}")
    plt.close()

def analyze_experiment_results_cn(folder_path='./model/results'):
    files = glob.glob(os.path.join(folder_path, "CN_*.json"))
    baseline_files = glob.glob(os.path.join(folder_path, "N_*.json"))
    if not files: return
    
    total_counts = get_total_counts()
    total_core = total_counts['CP'] + total_counts['CO']
    total_normal = total_counts['NP'] + total_counts['NO']
    
    all_data = []
    baseline_data = []
    for file_path in files:
        filename = os.path.basename(file_path)
        n_val = int(re.search(r'N(\d+)', filename).group(1))
        pct_label = f"{re.search(r'(\d+)pct', filename).group(1)}%"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            p_vector = data['input_config']['penalty_vector']
            total_core_exp = sum(1 for p in p_vector if p == 3)
            total_normal_exp = sum(1 for p in p_vector if p == 1)
            cancleled_pow_code = data['output_results']['cancleled_pow_code']
            stats = {k: cancleled_pow_code.count(k) for k in ['CP', 'CO', 'NP', 'NO']}
            
            c_cov = ((total_core_exp - (stats.get('CP', 0) + stats.get('CO', 0))) / total_core_exp * 100)
            n_cov = ((total_normal_exp - (stats.get('NP', 0) + stats.get('NO', 0))) / total_normal_exp * 100)
            all_data.append({"N": n_val, "X": f"{pct_label}\n(N={n_val})", "Core": c_cov, "Normal": n_cov})

    for file_path in baseline_files:
        filename = os.path.basename(file_path)
        n_val = int(re.search(r'N(\d+)', filename).group(1))
        pct_label = f"{re.search(r'(\d+)pct', filename).group(1)}%"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cancleled_pow_code = data['output_results']['cancleled_pow_code']
            stats = {k: cancleled_pow_code.count(k) for k in ['CP', 'CO', 'NP', 'NO']}
            core_cov = ((total_core - (stats.get('CP', 0) + stats.get('CO', 0))) / total_core * 100)
            normal_cov = ((total_normal - (stats.get('NP', 0) + stats.get('NO', 0))) / total_normal * 100)
            baseline_data.append({"N": n_val, "X": f"{pct_label}\n(N={n_val})", "Core_Baseline": core_cov, "Normal_Baseline": normal_cov})

    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    df_baseline = pd.DataFrame(baseline_data).sort_values('N', ascending=False)
    setup_plot_style('5.1 Spatial Priority: Core vs. Normal Routes', 'Driver Supply Percentage (Actual N)', 'Coverage Rate (%)')
    
    plt.plot(df['X'], df['Core'], marker='s', label='Core Routes', color='#1F77B4', lw=2.5, ms=8)
    plt.plot(df['X'], df['Normal'], marker='o', label='Normal Routes', color='#AEC7E8', lw=2.5, ms=8)
    plt.plot(df_baseline['X'], df_baseline['Core_Baseline'], marker='^', label='Core Baseline (all routes weight = 1)', color='#FF7F0E', lw=2.5, ms=8, ls='--')
    plt.plot(df_baseline['X'], df_baseline['Normal_Baseline'], marker='v', label='Normal Baseline (all routes weight = 1)', color='#FFBB78', lw=2.5, ms=8, ls='--')
    
    for i, r in df.iterrows():
        plt.annotate(f"{r['Core']:.1f}%", 
                     (r['X'], r['Core']), 
                     textcoords="offset points", 
                     xytext=(0, 10), 
                     ha='center', 
                     fontsize=8, 
                     fontweight='normal', 
                     color='#1F77B4')
        plt.annotate(f"{r['Normal']:.1f}%", 
                     (r['X'], r['Normal']), 
                     textcoords="offset points", 
                     xytext=(0, -15), 
                     ha='center', 
                     fontsize=8, 
                     fontweight='normal', 
                     color='#AEC7E8')
    
    save_and_clear('5_1_Spatial_Priority.pdf')

def analyze_experiment_results_po(folder_path='./model/results'):
    files = glob.glob(os.path.join(folder_path, "PO_*.json"))
    baseline_files = glob.glob(os.path.join(folder_path, "N_*.json"))
    if not files: return
    
    total_counts = get_total_counts()
    total_peak = total_counts['CP'] + total_counts['NP']
    total_off = total_counts['CO'] + total_counts['NO']
    
    all_data = []
    baseline_data = []
    for file_path in files:
        filename = os.path.basename(file_path)
        n_val = int(re.search(r'N(\d+)', filename).group(1))
        pct_label = f"{re.search(r'(\d+)pct', filename).group(1)}%"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            p_vector = data['input_config']['penalty_vector']
            total_peak_exp = sum(1 for p in p_vector if p == 3)
            total_off_exp = sum(1 for p in p_vector if p == 1)
            cancleled_pow_code = data['output_results']['cancleled_pow_code']
            stats = {k: cancleled_pow_code.count(k) for k in ['CP', 'CO', 'NP', 'NO']}
            
            p_cov = ((total_peak_exp - (stats.get('CP', 0) + stats.get('NP', 0))) / total_peak_exp * 100)
            o_cov = ((total_off_exp - (stats.get('CO', 0) + stats.get('NO', 0))) / total_off_exp * 100)
            all_data.append({"N": n_val, "X": f"{pct_label}\n(N={n_val})", "Peak": p_cov, "OffPeak": o_cov})

    for file_path in baseline_files:
        filename = os.path.basename(file_path)
        n_val = int(re.search(r'N(\d+)', filename).group(1))
        pct_label = f"{re.search(r'(\d+)pct', filename).group(1)}%"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cancleled_pow_code = data['output_results']['cancleled_pow_code']
            stats = {k: cancleled_pow_code.count(k) for k in ['CP', 'CO', 'NP', 'NO']}
            peak_cov = ((total_peak - (stats.get('CP', 0) + stats.get('NP', 0))) / total_peak * 100)
            off_cov = ((total_off - (stats.get('CO', 0) + stats.get('NO', 0))) / total_off * 100)
            baseline_data.append({"N": n_val, "X": f"{pct_label}\n(N={n_val})", "Peak_Baseline": peak_cov, "OffPeak_Baseline": off_cov})

    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    df_baseline = pd.DataFrame(baseline_data).sort_values('N', ascending=False)
    setup_plot_style('5.2 Temporal Priority: Peak vs. Off-Peak Hours', 'Driver Supply Percentage (Actual N)', 'Coverage Rate (%)')
    
    plt.plot(df['X'], df['Peak'], marker='s', label='Peak Hours', color='#1F77B4', lw=2.5, ms=8)
    plt.plot(df['X'], df['OffPeak'], marker='o', label='Off-Peak Hours', color='#AEC7E8', lw=2.5, ms=8)
    plt.plot(df_baseline['X'], df_baseline['Peak_Baseline'], marker='^', label='Peak Baseline (all routes weight = 1)', color='#FF7F0E', lw=2.5, ms=8, ls='--')
    plt.plot(df_baseline['X'], df_baseline['OffPeak_Baseline'], marker='v', label='Off-Peak Baseline (all routes weight = 1)', color='#FFBB78', lw=2.5, ms=8, ls='--')
    
    for i, r in df.iterrows():
        plt.annotate(f"{r['Peak']:.1f}%", 
                     (r['X'], r['Peak']), 
                     textcoords="offset points", 
                     xytext=(0, 10), 
                     ha='center', 
                     fontsize=8, 
                     fontweight='normal', 
                     color='#1F77B4')
        plt.annotate(f"{r['OffPeak']:.1f}%", 
                     (r['X'], r['OffPeak']), 
                     textcoords="offset points", 
                     xytext=(0, -15), 
                     ha='center', 
                     fontsize=8, 
                     fontweight='normal', 
                     color='#AEC7E8')
    
    save_and_clear('5_2_Temporal_Priority.pdf')

def analyze_experiment_results_cnpo(folder_path='./model/results'):
    files = glob.glob(os.path.join(folder_path, "CNPO_*.json"))
    baseline_files = glob.glob(os.path.join(folder_path, "N_*.json"))
    if not files: return
    
    total_counts = get_total_counts()
    
    all_data = []
    baseline_data = []
    for file_path in files:
        filename = os.path.basename(file_path)
        n_val = int(re.search(r'N(\d+)', filename).group(1))
        pct_label = f"{re.search(r'(\d+)pct', filename).group(1)}%"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            mapping = data['input_config']['penalty_mapping']
            p_vector = data['input_config']['penalty_vector']
            cancleled_pow_code = data['output_results']['cancleled_pow_code']
            stats = {k: cancleled_pow_code.count(k) for k in ['CP', 'CO', 'NP', 'NO']}
            
            res = {"N": n_val, "X": f"{pct_label}\n(N={n_val})"}
            for cat in ["CP", "CO", "NP", "NO"]:
                total = sum(1 for p in p_vector if p == mapping.get(cat))
                res[f"{cat}_Cov"] = ((total - stats.get(cat, 0)) / total * 100) if total > 0 else 0
            all_data.append(res)

    for file_path in baseline_files:
        filename = os.path.basename(file_path)
        n_val = int(re.search(r'N(\d+)', filename).group(1))
        pct_label = f"{re.search(r'(\d+)pct', filename).group(1)}%"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cancleled_pow_code = data['output_results']['cancleled_pow_code']
            stats = {k: cancleled_pow_code.count(k) for k in ['CP', 'CO', 'NP', 'NO']}
            res = {"N": n_val, "X": f"{pct_label}\n(N={n_val})"}
            for cat in ["CP", "CO", "NP", "NO"]:
                total = total_counts[cat]
                res[f"{cat}_Baseline"] = ((total - stats.get(cat, 0)) / total * 100) if total > 0 else 0
            baseline_data.append(res)

    df = pd.DataFrame(all_data).sort_values('N', ascending=False)
    df_baseline = pd.DataFrame(baseline_data).sort_values('N', ascending=False)
    
    # Peak Hours Graph
    setup_plot_style('5.3a Peak Hours', 'Driver Supply Percentage (Actual N)', 'Coverage Rate (%)')
    
    peak_styles = {
        "CP_Cov": ("Core-Peak", "#1F77B4", "s", "-"),
        "NP_Cov": ("Normal-Peak", "#AEC7E8", "o", "-")
    }
    peak_baseline_styles = {
        "CP_Baseline": ("Core-Peak Baseline (all routes weight = 1)", "#FF7F0E", "^", "--"),
        "NP_Baseline": ("Normal-Peak Baseline (all routes weight = 1)", "#FFBB78", "D", "--")
    }
    
    for col, (lbl, clr, mkr, ls) in peak_styles.items():
        plt.plot(df['X'], df[col], label=lbl, color=clr, marker=mkr, linestyle=ls, lw=2, ms=7)
        for i, r in df.iterrows():
            plt.annotate(f"{r[col]:.1f}%", 
                         (r['X'], r[col]), 
                         textcoords="offset points", 
                         xytext=(0, 10), 
                         ha='center', 
                         fontsize=8, 
                         fontweight='normal', 
                         color=clr)
    for col, (lbl, clr, mkr, ls) in peak_baseline_styles.items():
        plt.plot(df_baseline['X'], df_baseline[col], label=lbl, color=clr, marker=mkr, linestyle=ls, lw=2, ms=7)
    
    save_and_clear('5_3a_Peak_Hours.pdf')
    
    # Off-Peak Hours Graph
    setup_plot_style('5.3b Off-Peak Hours', 'Driver Supply Percentage (Actual N)', 'Coverage Rate (%)')
    
    offpeak_styles = {
        "CO_Cov": ("Core-Off-Peak", "#1F77B4", "x", "-"),
        "NO_Cov": ("Normal-Off-Peak", "#AEC7E8", "v", "-")
    }
    offpeak_baseline_styles = {
        "CO_Baseline": ("Core-Off-Peak Baseline (all routes weight = 1)", "#FF7F0E", "v", "--"),
        "NO_Baseline": ("Normal-Off-Peak Baseline (all routes weight = 1)", "#FFBB78", "s", "--")
    }
    
    for col, (lbl, clr, mkr, ls) in offpeak_styles.items():
        plt.plot(df['X'], df[col], label=lbl, color=clr, marker=mkr, linestyle=ls, lw=2, ms=7)
        for i, r in df.iterrows():
            plt.annotate(f"{r[col]:.1f}%", 
                         (r['X'], r[col]), 
                         textcoords="offset points", 
                         xytext=(0, 10), 
                         ha='center', 
                         fontsize=8, 
                         fontweight='normal', 
                         color=clr)
    for col, (lbl, clr, mkr, ls) in offpeak_baseline_styles.items():
        plt.plot(df_baseline['X'], df_baseline[col], label=lbl, color=clr, marker=mkr, linestyle=ls, lw=2, ms=7)
    
    save_and_clear('5_3b_Off_Peak_Hours.pdf')

if __name__ == "__main__":
    # 請確保資料夾路徑正確
    path = './model/results'
    analyze_experiment_results_cn(path)
    analyze_experiment_results_po(path)
    analyze_experiment_results_cnpo(path)