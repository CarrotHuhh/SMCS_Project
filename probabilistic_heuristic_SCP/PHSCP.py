# This code is adapted from: https://github.com/miguelcocruz/set_covering_problem/tree/master
# Significant modifications were made.
# Original author: miguelcocruz
# Modified by: Yi-An Liu

import numpy as np
import random
# import time
# from itertools import combinations


class SetCover():

    def load_data(self, filepath):

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
        self.subsets_cost_np = np.array([1] * self.nr_atr)

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

    def greedy_randomized_algorithm(self, alpha, a, b, is_row_constraint=False, row_constraint=0):

        # Subsets in the solution
        Solution = set()

        # Atributes satisfied by the solution
        Solution_atr = set()

        # Candidate set
        C = set(range(self.nr_subsets))

        while not self.is_complete(Solution):            
            score = dict()

            # Calculate original_total_score for all uncovered rows
            original_total_score = self.total_cost(Solution, a, b)

            # threshold = original_total_score * alpha
            threshold = original_total_score * alpha

            # Calculate total_score when adding each column
            for i in C:
                score[i] = self.total_cost(Solution | {i}, a, b)

            # if total_socre < threshold -> store into RCL
            # (alpha 越大會選進越多組)
            RCL = [i for i in C if score[i] < threshold]

            # TODO: The RCL list might be empty
            if RCL == []:
                s_index = random.choice(list(C))
            else:
                s_index = random.choice(RCL)

            C -= {s_index}
            Solution.add(s_index)
            Solution_atr.update(self.subsets[s_index])

            if is_row_constraint:
                if len(Solution) >= row_constraint:
                    break


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
                x = self.greedy_randomized_algorithm(alpha, a, b, is_row_constraint, row_constraint)
                
                # 2. 移除多餘的元素 (對應論文中第 11 行: Remove superfluous j from J^0)
                x = self.remove_redundancy(x)

                # 評估當前解的集合數量
                cost = self.total_cost(x, a, b)

                # 3. 如果找到更少集合的組合，就更新最佳解 (對應論文中第 13 行)
                if cost < best_cost:
                    best_cost = cost
                    best_sol = x.copy()

            return best_cost, best_sol