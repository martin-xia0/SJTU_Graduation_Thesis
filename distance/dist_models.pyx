# -*- coding: UTF-8 -*-
import numpy as np

cimport numpy as np
import pandas as pd
import time


cdef double getManhattanDistance(s1, s2):
    # 曼哈顿距离
    cdef int n = len(s1)
    cdef double dist_sum = 0
    cdef int i = 0
    while i < n:
        dist_sum += abs(s1[i]-s2[i])
        i += 1
    return dist_sum


cdef double getEuclideanDistance(np.ndarray[double , ndim=1] s1, np.ndarray[double , ndim=1] s2):
    # 欧几里得距离
    cdef int n = len(s1)
    cdef double square_sum = 0
    cdef int i = 0
    while i < n:
        square_sum += (s1[i]-s2[i])**2
        i += 1
    return square_sum**0.5


# class DtwModel:
#     # 动态时间调整模型
#     def __init__(self, series1, series2):
#         self.s1 = series1
#         self.s2 = series2
#         self.n1 = len(series1)
#         self.n2 = len(series2)
#         self.sum = 0
#         self.cost_matrix = np.zeros(shape=(self.n1, self.n2), dtype=float)
#         self.dtw_distance = 0
#
#     def get_cost_matrix(self):
#         # 计算距离损失矩阵
#         for i in range(1, self.n1):
#             self.cost_matrix[i][0] = abs(self.s1[i] - self.s2[0]) + self.cost_matrix[i - 1][0]
#         for j in range(1, self.n2):
#             self.cost_matrix[0][j] = abs(self.s1[0] - self.s2[j]) + self.cost_matrix[0][j - 1]
#
#         for i in range(1, self.n1):
#             for j in range(1, self.n2):
#                 left_val = self.cost_matrix[i][j - 1]
#                 up_val = self.cost_matrix[i - 1][j]
#                 left_up_val = self.cost_matrix[i - 1][j - 1]
#                 self.cost_matrix[i][j] = abs(self.s1[i] - self.s2[j]) + min(left_up_val, left_val, up_val)
#
#         return self.cost_matrix
#
#     def get_dtw_distance(self):
#         # 计算最小距离
#         step_i = self.n1 - 1
#         step_j = self.n2 - 1
#
#         while step_i > 0 and step_j > 0:
#             self.dtw_distance += self.cost_matrix[step_i][step_j]
#             print(step_i , step_j)
#             left_val = self.cost_matrix[step_i][step_j - 1]
#             up_val = self.cost_matrix[step_i - 1][step_j]
#             left_up_val = self.cost_matrix[step_i - 1][step_j - 1]
#             if left_val <= up_val and left_val <= left_up_val:
#                 step_j -= 1
#             elif up_val <= left_val and up_val <= left_up_val:
#                 step_i -= 1
#             else:
#                 step_i -= 1
#                 step_j -= 1
#
#         while step_i > 0:
#             self.dtw_distance += self.cost_matrix[step_i][step_j]
#             print(step_i, step_j)
#             step_i -= 1
#
#         while step_j > 0:
#             self.dtw_distance += self.cost_matrix[step_i][step_j]
#             print(step_i, step_j)
#             step_j -= 1
#
#         return self.dtw_distance
#

cdef class DistMatrix:
    cdef np.ndarray sample_set
    cdef int n

    def __cinit__(self, np.ndarray[double , ndim=2] sample_set):
        self.sample_set = sample_set
        self.n = len(sample_set)

    cpdef np.ndarray[double , ndim=2] getManhattanDistMatrix(self):
        cdef np.ndarray manhattan_matrix
        manhattan_matrix = np.full(shape=(self.n, self.n) , fill_value=-1 , dtype=np.double)
        cdef int i = 1
        cdef int j
        cdef double dist
        while i < self.n:
            j = 0
            while j < i:
                manhattan_matrix[i][j] = getManhattanDistance(self.sample_set[i], self.sample_set[j])
                j += 1
            i += 1
        return manhattan_matrix

    cpdef np.ndarray[double , ndim=2] getEuclideanDistMatrix(self):
        cdef np.ndarray euclidean_matrix
        euclidean_matrix = np.full(shape=(self.n, self.n) , fill_value=-1 , dtype=np.double)
        cdef int i = 1
        cdef int j
        cdef double dist
        while i < self.n:
            j = 0
            while j < i:
                euclidean_matrix[i][j] = getEuclideanDistance(self.sample_set[i], self.sample_set[j])
                j += 1
            i += 1
        return euclidean_matrix
