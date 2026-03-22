# This code is adapted from: https://github.com/miguelcocruz/set_covering_problem/tree/master
# Significant modifications were made.
# Original author: miguelcocruz
# Modified by: Yi-An Liu

import numpy as np
import random
# import time
# from itertools import combinations
import json
import re
import csv
import os
import cupy as cp

class SetCover():

    def load_data(self, filepath, penalty_csv_filepath=None, penalty_mapping=None):

        lines = []

        with open(filepath, 'r') as file:
            for line in file:
                lines.append(line)

        # First line
        line_0 = lines[0].strip().split()

        # Number of atributes
        self.nr_atr = int(line_0[0])

        # Number of subsets
        self.nr_subsets = int(line_0[1])

        iter_lines = iter(lines)
        next(iter_lines)

        self.subsets_cost = []
        count_lines_cost = 0

        for line in iter_lines:
            self.subsets_cost.extend(line.strip('\n').split())
            count_lines_cost += 1

            if len(self.subsets_cost) == self.nr_subsets:
                break

        # List containing the cost of each subset
        self.subsets_cost = [int(cost) for cost in self.subsets_cost]

        count_elem = -1
        count_aux = 0
        nr_subsets_in_line = 0

        line_of_size = True

        # Computing the list of subsets
        self.subsets = [set() for _ in range(self.nr_subsets)]

        for line in iter_lines:

            if line_of_size:
                nr_subsets_in_line = int(line.strip('\n').split()[0])
                line_of_size = False
                count_elem += 1
                count_aux = 0

            else:
                line_search = line.strip('\n').split()
                count_aux += len(line_search)

                for j in line_search:
                    self.subsets[int(j) - 1].add(count_elem)

                if count_aux == nr_subsets_in_line:
                    line_of_size = True

        # Creating numpy arrays for increasing performance in some operations
        self.subsets_np = np.array(self.subsets)
        # self.subsets_cost_np = np.array(self.subsets_cost)
        # self.subsets_cost_np = np.array([1] * self.nr_atr)


        # Load penalty CSV if provided
        if penalty_csv_filepath and penalty_mapping:
            with open(penalty_csv_filepath, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # 讀取第一列 (row)
                self.categories = next(reader) 
            # print(categories)

            
            if len(self.categories) == self.nr_atr:
                self.subsets_cost_np = np.array([penalty_mapping.get(cat.strip(), 1) for cat in self.categories])
            else:
                print(f"Warning: penalty CSV length {len(self.categories)} does not match nr_atr {self.nr_atr}")

        # print(self.subsets_cost_np)

        # 构建二值覆盖矩阵
        self.coverage_matrix = np.zeros((self.nr_atr, self.nr_subsets), dtype=np.float32)
        for j, subset in enumerate(self.subsets):
            for attr in subset:
                self.coverage_matrix[attr, j] = 1.0

        # 将覆盖矩阵和子集成本转换为GPU数组
        self.coverage_matrix_gpu = cp.array(self.coverage_matrix)           # shape: (nr_atr, nr_subsets)
        self.subsets_cost_gpu = cp.array(self.subsets_cost_np, dtype=cp.float32)  # shape: (nr_atr,)
        self.cov_mat_neg_gpu = 1.0 - self.coverage_matrix_gpu               # shape: (nr_atr, nr_subsets)，预计算避免重复运算


    def is_complete(self, solution):

        if len(solution) == 0:
            return False

        elif len(set.union(*self.subsets_np[list(solution)])) == self.nr_atr:
            return True

        else:
            return False

    def total_cost(self, solution, a, b):
        if not solution:
            covered_attributes = set()
        else:
            # Calculate the attributes covered by the given solution
            covered_attributes = set.union(*self.subsets_np[list(solution)])

        # Identify unselected subsets (those NOT in the current solution)
        all_subset_indices = set(range(self.nr_atr))
        unselected_subset_indices = all_subset_indices - covered_attributes

        # Sum the costs of the unselected subsets
        sum_of_unselected_subset_costs = self.subsets_cost_np[list(unselected_subset_indices)].sum()

        # Calculate the total cost based on your formula
        # 第二項：{0, 1, .... , n} - covered_attributes -> sum of cost

        # 第一項： len(solution)
        # a * len(solution) + b * sum of unselected subset costs
        total_cost = a * len(solution) + b * sum_of_unselected_subset_costs
        
        return total_cost

    def batch_total_cost(self, covered_attributes_gpu, candidate_indices, a, b, solution_size):    

        # 取候选子集的覆盖列
        cand_cols = self.coverage_matrix_gpu[:, candidate_indices]
    
        # 加入各候选后的新覆盖情况（OR 操作） = set.union(*self.subsets_np[...])
        new_covered_attributes = cp.maximum(covered_attributes_gpu[:, None], cand_cols)
        
        # 未覆盖属性的 cost
        unselected_mask = 1 - new_covered_attributes  # (nr_atr, len(candidates))
        sum_of_unselected_subset_costs = (self.subsets_cost_gpu[:, None] * unselected_mask).sum(axis=0)
        
        # total_cost = a * (solution_size + 1) + b * sum_uncovered
        total_cost = a * (solution_size + 1) + b * sum_of_unselected_subset_costs
        return total_cost
    

    # def greedy_randomized_algorithm(self, alpha, a, b, is_row_constraint=False, row_constraint=0):

    #     # Subsets in the solution
    #     Solution = set()

    #     # Atributes satisfied by the solution
    #     Solution_atr = set()

    #     # Candidate set
    #     C = set(range(self.nr_subsets))

    #     empty_RCL = 0
        
    #     while not self.is_complete(Solution):            
    #         score = dict()

    #         # Calculate total_score when adding each column
    #         for i in C:
    #             score[i] = self.total_cost(Solution | {i}, a, b)
            
    #         min_score = min(score.values())
    #         max_score = max(score.values())
    #         threshold = min_score + (max_score - min_score) * alpha

    #         # if total_socre < threshold -> store into RCL
    #         # (alpha 越大會選進越多組)
    #         RCL = [i for i in C if score[i] <= threshold]

    #         if RCL == []:
    #             # print("RCL list is empty")
    #             # print("RCL list is empty, break")
    #             # break
    #             s_index = random.choice(list(C))
    #             empty_RCL += 1
    #             # print(s_index)
    #         else:
    #             s_index = random.choice(RCL)
    #             # print(s_index)

    #         C -= {s_index}
    #         Solution.add(s_index)
    #         Solution_atr.update(self.subsets[s_index])

    #         if is_row_constraint:
    #             if len(Solution) >= row_constraint:
    #                 break

    #     print(f"number of empty RCL: {empty_RCL}")

    #     return Solution

    def greedy_randomized_algorithm_gpu(self, alpha, a, b, is_row_constraint=False, row_constraint=0):

        # Subsets in the solution
        Solution = set()

        # Atributes satisfied by the solution
        Solution_atr = set()

        # Candidate set
        C = set(range(self.nr_subsets))

        # GPU 覆盖向量  =  Solution_atr（set → 0/1 向量）
        covered_attributes_gpu = cp.zeros(self.nr_atr, dtype=cp.float32)

        empty_RCL = 0

        while not self.is_complete(Solution):

            # 批量计算将各候选加入后的 total_cost（并行计算 = for i in C Loop）
            scores_gpu = self.batch_total_cost(covered_attributes_gpu, list(C), a, b, len(Solution))
            score_values = cp.asnumpy(scores_gpu)  # 回传 CPU 用于 RCL 筛选

            min_score = score_values.min()
            max_score = score_values.max()
            threshold = min_score + (max_score - min_score) * alpha

            # if total_score < threshold -> store into RCL
            # (alpha 越大會選進越多組)
            C_list = list(C)
            RCL = [C_list[i] for i, s in enumerate(score_values) if s <= threshold]

            if RCL == []:
                # print("RCL list is empty")
                # print("RCL list is empty, break")
                # break
                s_index = random.choice(list(C))
                empty_RCL += 1
                # print(s_index)
            else:
                s_index = random.choice(RCL)
                # print(s_index)

            C -= {s_index}
            Solution.add(s_index)
            Solution_atr.update(self.subsets[s_index])

            # 同步更新 GPU 覆盖向量
            covered_attributes_gpu = cp.maximum(covered_attributes_gpu, self.coverage_matrix_gpu[:, s_index])

            if is_row_constraint:
                if len(Solution) >= row_constraint:
                    break

        print(f"number of empty RCL: {empty_RCL}")

        return Solution
    
    

    def remove_redundancy(self, solution):

        for i in solution:
            sol_aux = solution.copy()
            sol_aux.remove(i)
            if self.is_complete(sol_aux):
                solution = sol_aux.copy()

        return solution

    def probabilistic_heuristic(self, N, alpha, a, b, is_row_constraint=False, row_constraint=0):
            best_cost = float('inf')
            best_sol = set()

            # 對應論文中重複 N 次的迴圈 (do i=1,...,N)
            for i in range(N):
                # 1. 隨機構造初始解 (對應論文中 while loop 構造 J^0)
                # x = self.greedy_randomized_algorithm(alpha, a, b, is_row_constraint, row_constraint)
                x = self.greedy_randomized_algorithm_gpu(alpha, a, b, is_row_constraint, row_constraint)
                
                # 2. 移除多餘的元素 (對應論文中第 11 行: Remove superfluous j from J^0)
                x = self.remove_redundancy(x)

                # 評估當前解的集合數量
                cost = self.total_cost(x, a, b)

                # 3. 如果找到更少集合的組合，就更新最佳解 (對應論文中第 13 行)
                if cost < best_cost:
                    best_cost = cost
                    best_sol = x.copy()

            return best_cost, best_sol


    def save_experiment_json(self, exp_id, best_sol, runtime_sec, alpha, a, b, n_iterations, penalty_vector, matrix_file, row_constraint, best_cost, penalty_mapping=None, data_filename=None, penalty_csv_filename=None):
        
        # 決策結果
        selected_duty_indices = sorted(list(best_sol))  # Convert set to sorted list
        
        # 計算未被覆蓋的 rows (attributes)
        if best_sol:
            covered_attributes = set.union(*self.subsets_np[list(best_sol)])
        else:
            covered_attributes = set()
        
        all_attributes = set(range(self.nr_atr))
        unselected_attributes = all_attributes - covered_attributes
        cancelled_pow_indices = sorted(list(unselected_attributes))
        
        # 計算未被覆蓋的 attributes 的成本 (sum_of_unselected_subset_costs)
        sum_of_unselected_subset_costs = int(self.subsets_cost_np[list(unselected_attributes)].sum())
        
        # 提取cancelled_pow_indices对应的categories (cancelled_pow_code)
        cancelled_pow_code = []
        if hasattr(self, 'categories') and self.categories:
            cancelled_pow_code = [self.categories[idx].strip() for idx in cancelled_pow_indices]
        
        # 統計四種category的數量
        statistics_four_categories = {'CP': 0, 'CO': 0, 'NP': 0, 'NO': 0}
        for code in cancelled_pow_code:
            if code in statistics_four_categories:
                statistics_four_categories[code] += 1
        
        # 將輸入與輸出封裝在一起
        experiment_data = {
            "metadata": {
                "exp_id": exp_id,
                "matrix_used": matrix_file,
                "input_files_1": data_filename,
                "input_files_2": penalty_csv_filename
            },
            "input_config": {
                "threshold": alpha,
                "n_iterations": n_iterations,
                "alpha": a,
                "beta": b,
                "N_limit": int(row_constraint),
                "penalty_mapping": penalty_mapping,
                "penalty_vector": penalty_vector
            },
            "output_results": {
                "status": "Completed",
                "solver": "Probabilistic Heuristic SCP",    #ok
                "runtime_sec": round(runtime_sec, 4),   #ok
                "total_cost": float(best_cost),    # 總共的cost
                "drivers_used": len(best_sol),  #ok
                "total_penalty": sum_of_unselected_subset_costs, # sum of the cost of piece of work
                "cancelled_count": len(cancelled_pow_indices),  #ok
                "selected_duty_indices": selected_duty_indices, #ok
                "cancelled_pow_indices": cancelled_pow_indices,  #ok
                "cancelled_pow_code": cancelled_pow_code,  # cancelled indices對應的category code
                "statistics_four_categories": statistics_four_categories  # CP, CO, NP, NO的統計
            }
        }

        # 轉換為JSON字符串
        json_str = json.dumps(experiment_data, indent=4, ensure_ascii=False)
        
        # 將penalty_vector、selected_duty_indices、cancelled_pow_indices、cancelled_pow_code保持在一行
        json_str = re.sub(
            r'"penalty_vector":\s*\[\s*([^\]]+)\s*\]',
            lambda m: '"penalty_vector": [' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']',
            json_str
        )
        json_str = re.sub(
            r'"selected_duty_indices":\s*\[\s*([^\]]+)\s*\]',
            lambda m: '"selected_duty_indices": [' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']',
            json_str
        )
        json_str = re.sub(
            r'"cancelled_pow_indices":\s*\[\s*([^\]]+)\s*\]',
            lambda m: '"cancelled_pow_indices": [' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']',
            json_str
        )
        json_str = re.sub(
            r'"cancelled_pow_code":\s*\[\s*([^\]]+)\s*\]',
            lambda m: '"cancelled_pow_code": [' + ', '.join('\"' + x.strip().strip('\"') + '\"' for x in m.group(1).split(',')) + ']',
            json_str
        )

        with open(f"./result/{exp_id}_full_report.json", "w", encoding="utf-8") as f:
            f.write(json_str)
        
        print(f"\nExperiment report saved to: {exp_id}_full_report.json")
        return experiment_data
    

    def probabilistic_heuristic_gpu_parallel(self, N, alpha, a, b,
                                          is_row_constraint=False, row_constraint=0):
        """
        在 GPU 上同时运行 N 次独立迭代。
        每一步所有未完成的迭代并行推进，用 done 掩码控制终止。
        """
        nr_a = self.nr_atr
        nr_s = self.nr_subsets
        INF  = 1e9

        # ── 状态张量，全部在 GPU ──────────────────────────────────────────────
        # 各迭代的属性覆盖向量
        covered   = cp.zeros((N, nr_a), dtype=cp.float32)       # (N, nr_atr)
        # 各迭代中各子集是否仍可选
        active    = cp.ones ((N, nr_s), dtype=cp.float32)        # (N, nr_subsets)
        # 各迭代已选子集记录
        selected  = cp.zeros((N, nr_s), dtype=cp.int32)          # (N, nr_subsets)
        # 各迭代已选子集数量
        sol_sizes = cp.zeros(N,         dtype=cp.float32)        # (N,)
        # 各迭代是否已完成
        done      = cp.zeros(N,         dtype=cp.bool_)          # (N,)

        cov_mat  = self.coverage_matrix_gpu   # (nr_atr, nr_subsets)，已在 GPU
        cost_vec = self.subsets_cost_gpu      # (nr_atr,)，已在 GPU

        # ── 主循环：最多 nr_subsets 步 ────────────────────────────────────────
        for _ in range(nr_s):
            if done.all():
                break

            # 1. 计算每个 (迭代, 候选子集) 加入后的未覆盖惩罚之和
            #    数学等价：1 - max(a,b) = (1-a)*(1-b)（二值矩阵成立）
            #    sum_uncovered[k,j] = (cost*(1-covered[k])) · (1-cov_mat[:,j])
            #    → 矩阵乘法，无需构建 (N, nr_atr, nr_subsets) 3D 张量
            uncov_weighted = cost_vec[None, :] * (1.0 - covered)   # (N, nr_atr)
            sum_uncovered  = uncov_weighted @ self.cov_mat_neg_gpu  # (N, nr_subsets)

            scores = a * (sol_sizes[:, None] + 1) + b * sum_uncovered  # (N, nr_subsets)

            # 2. 屏蔽非活跃候选（令其分数为 INF / -INF）
            scores_hi = cp.where(active.astype(cp.bool_), scores,  INF)  # 用于找 min
            scores_lo = cp.where(active.astype(cp.bool_), scores, -INF)  # 用于找 max

            min_s = scores_hi.min(axis=1, keepdims=True)   # (N, 1)
            max_s = scores_lo.max(axis=1, keepdims=True)   # (N, 1)

            # 3. 构建 RCL：score <= min + (max - min) * alpha
            threshold = min_s + (max_s - min_s) * alpha    # (N, 1)
            rcl_mask  = (scores_hi <= threshold + 1e-9) & active.astype(cp.bool_)  # (N, nr_subsets)

            # 若 RCL 为空则回退到所有活跃候选
            rcl_empty    = ~rcl_mask.any(axis=1, keepdims=True)          # (N, 1)
            effective_rcl = cp.where(rcl_empty, active.astype(cp.bool_), rcl_mask)

            # 4. 每个迭代从其 RCL 中随机选一个：对 RCL 内元素加随机扰动后取 argmax
            rand      = cp.where(effective_rcl,
                                cp.random.uniform(0, 1, (N, nr_s)),
                                -1.0)
            chosen_j  = rand.argmax(axis=1)               # (N,)  每个迭代选中的子集下标

            # 5. 只更新尚未完成的迭代
            not_done = ~done                               # (N,)

            #    one-hot 编码选中的子集
            one_hot = cp.zeros((N, nr_s), dtype=cp.float32)
            one_hot[cp.arange(N), chosen_j] = 1.0

            #    更新覆盖向量
            chosen_cols = cov_mat[:, chosen_j].T           # (N, nr_atr)
            covered = cp.where(
                not_done[:, None],
                cp.maximum(covered, chosen_cols),
                covered
            )

            #    从活跃集中移除已选子集
            active = cp.where(
                not_done[:, None],
                active * (1.0 - one_hot),
                active
            )

            #    记录选中的子集
            selected = cp.where(
                not_done[:, None],
                selected + one_hot.astype(cp.int32),
                selected
            )

            sol_sizes = cp.where(not_done, sol_sizes + 1.0, sol_sizes)

            # 6. 更新 done 标志
            fully_covered = covered.sum(axis=1) >= nr_a - 0.5   # (N,)
            if is_row_constraint:
                done = done | fully_covered | (sol_sizes >= row_constraint)
            else:
                done = done | fully_covered

        # ── 回 CPU，去冗余，选最优 ────────────────────────────────────────────
        selected_cpu = cp.asnumpy(selected)   # (N, nr_subsets)

        best_cost = float('inf')
        best_sol  = set()

        for k in range(N):
            sol_k  = set(int(j) for j in np.where(selected_cpu[k] == 1)[0])
            sol_k  = self.remove_redundancy(sol_k)
            cost_k = self.total_cost(sol_k, a, b)
            if cost_k < best_cost:
                best_cost = cost_k
                best_sol  = sol_k.copy()

        return best_cost, best_sol
