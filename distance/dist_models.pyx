# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd
import time


def getManhattanDistance(s1, s2):
    n = len(s1)
    dist_sum = 0
    # 曼哈顿距离
    for i in range(n):
        dist_sum += abs(s1[i]-s2[i])
    return dist_sum


def getEuclideanDistance(s1, s2):
    # 欧几里得距离
    n = len(s1)
    square_sum = 0
    for i in range(n):
        square_sum += (s1[i]-s2[i])**2
    return square_sum**0.5


class DtwModel:
    # 动态时间调整模型
    def __init__(self, series1, series2):
        self.s1 = series1
        self.s2 = series2
        self.n1 = len(series1)
        self.n2 = len(series2)
        self.sum = 0
        self.cost_matrix = np.zeros(shape=(self.n1, self.n2), dtype=float)
        self.dtw_distance = 0

    def get_cost_matrix(self):
        # 计算距离损失矩阵
        for i in range(1, self.n1):
            self.cost_matrix[i][0] = abs(self.s1[i] - self.s2[0]) + self.cost_matrix[i - 1][0]
        for j in range(1, self.n2):
            self.cost_matrix[0][j] = abs(self.s1[0] - self.s2[j]) + self.cost_matrix[0][j - 1]

        for i in range(1, self.n1):
            for j in range(1, self.n2):
                left_val = self.cost_matrix[i][j - 1]
                up_val = self.cost_matrix[i - 1][j]
                left_up_val = self.cost_matrix[i - 1][j - 1]
                self.cost_matrix[i][j] = abs(self.s1[i] - self.s2[j]) + min(left_up_val, left_val, up_val)

        return self.cost_matrix

    def get_dtw_distance(self):
        # 计算最小距离
        step_i = self.n1 - 1
        step_j = self.n2 - 1

        while step_i > 0 and step_j > 0:
            self.dtw_distance += self.cost_matrix[step_i][step_j]
            print(step_i , step_j)
            left_val = self.cost_matrix[step_i][step_j - 1]
            up_val = self.cost_matrix[step_i - 1][step_j]
            left_up_val = self.cost_matrix[step_i - 1][step_j - 1]
            if left_val <= up_val and left_val <= left_up_val:
                step_j -= 1
            elif up_val <= left_val and up_val <= left_up_val:
                step_i -= 1
            else:
                step_i -= 1
                step_j -= 1

        while step_i > 0:
            self.dtw_distance += self.cost_matrix[step_i][step_j]
            print(step_i, step_j)
            step_i -= 1

        while step_j > 0:
            self.dtw_distance += self.cost_matrix[step_i][step_j]
            print(step_i, step_j)
            step_j -= 1

        return self.dtw_distance


class DistMatrix:
    def __init__(self):
        pass


if __name__ == "__main__":
    s1 = [1, 3, 4, 9, 8, 2, 1, 5, 7, 3]
    s2 = [1, 6, 2, 3, 0, 9, 4, 3, 6, 3]
    t1 = time.time()
    for _ in range(100000):
        getEuclideanDistance(s1, s2)
        getManhattanDistance(s1, s2)
    print("耗时 {}".format(time.time()-t1))

    # m2 = DtwModel(s1, s2)
    # print(m2.get_cost_matrix())
    # print(m2.get_dtw_distance())
