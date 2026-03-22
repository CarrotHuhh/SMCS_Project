#!/bin/bash
#SBATCH --job-name=scp_batch           # 任务名称改为 scp 相关
#SBATCH --output=result_%j.out        # 标准输出日志
#SBATCH --error=error_%j.err          # 错误日志
#SBATCH --partition=gpua6000          # GPU 分区
#SBATCH --gres=gpu:1                  # 1 张显卡
#SBATCH --cpus-per-task=16            # 16 个 CPU 核心
#SBATCH --mem=64G                     # 64GB 内存
#SBATCH --time=10-00:00:00            # 最长 10 天

# 1. 加载 Conda 环境 (切换为 scp 环境)
source ~/.bashrc
# 注意：这里路径指向你新创建的 scp 环境
conda activate /scratch/2145189/conda/envs/scp

# 2. 设置路径和环境变量
# 切换到新的工作目录
cd /scratch/2145189/tabcbm/tabcbm/probabilistic_heuristic_SCP

# 更新 PYTHONPATH，包含新的项目根目录
export PYTHONPATH=$PYTHONPATH:/scratch/2145189/tabcbm/tabcbm/probabilistic_heuristic_SCP
# 更新动态链接库路径到 scp 环境
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/scratch/2145189/conda/envs/scp/lib/

# 3. 确保输出目录存在
mkdir -p /scratch/2145189/tabcbm/tabcbm/probabilistic_heuristic_SCP/result

# 4. 运行 batch.py 脚本
# 建议加上 -u 参数以实现日志实时刷新
python -u /scratch/2145189/tabcbm/tabcbm/probabilistic_heuristic_SCP/batch.py