# -*- coding: UTF-8 -*-
import numpy as np

cimport numpy as np
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


cdef double getDtwDistance(np.ndarray[double , ndim=1] s1, np.ndarray[double , ndim=1] s2):
    # 动态时间规划
    cdef int n1 = len(s1)
    cdef int n2 = len(s2)
    cdef double dtw_sum = 0
    cdef np.ndarray cost_matrix
    cost_matrix = np.zeros(shape=(n1, n2), dtype=np.double)

    # 计算距离损失矩阵
    cdef int i = 1
    cdef int j = 1
    cdef double left_val
    cdef double up_val
    cdef double left_up_val
    while i < n1:
        cost_matrix[i][0] = abs(s1[i] - s2[0]) + cost_matrix[i-1][0]
        i += 1
    i = 1
    while i < n2:
        cost_matrix[0][i] = abs(s1[0] - s2[i]) + cost_matrix[0][i-1]
        i += 1
    i = 1
    while i < n1:
        while j < n2:
            left_val = cost_matrix[i][j-1]
            up_val = cost_matrix[i-1][j]
            left_up_val = cost_matrix[i-1][j-1]
            cost_matrix[i][j] = abs(s1[i] - s2[j]) + min(left_up_val, left_val, up_val)
            j += 1
        i += 1
        j = 1
    # print(cost_matrix)
    # 搜索最小路径
    cdef int step_i = n1 - 1
    cdef int step_j = n2 - 1
    while step_i > 0 and step_j > 0:
        dtw_sum += cost_matrix[step_i][step_j]
        left_val = cost_matrix[step_i][step_j-1]
        up_val = cost_matrix[step_i-1][step_j]
        left_up_val = cost_matrix[step_i-1][step_j-1]
        if left_val <= up_val and left_val <= left_up_val:
            step_j -= 1
        elif up_val <= left_val and up_val <= left_up_val:
            step_i -= 1
        else:
            step_i -= 1
            step_j -= 1
    while step_i > 0:
        dtw_sum += cost_matrix[step_i][step_j]
        step_i -= 1
    while step_j > 0:
        dtw_sum += cost_matrix[step_i][step_j]
        step_j -= 1

    return dtw_sum


cdef class DistMatrix:
    cdef dict raw_sample_set
    cdef dict sample_set
    cdef np.ndarray ids
    cdef int n
    cdef int i
    cdef int j
    cdef double dist

    cdef np.ndarray euclidean_matrix
    cdef np.ndarray manhattan_matrix
    cdef np.ndarray dtw_matrix

    def __cinit__(self, dict raw_sample_set):
        self.raw_sample_set = raw_sample_set
        self.n = len(raw_sample_set.keys())
        self.ids = np.array(list(raw_sample_set.keys()))
        self.sample_set = {}

    cpdef void normalizeSeries(self):
        cdef double max_val
        cdef double min_val
        cdef np.ndarray normalized_series
        i = 0
        while i < self.n:
            max_val = max(self.raw_sample_set[self.ids[i]])
            min_val = min(self.raw_sample_set[self.ids[i]])
            normalized_series = (self.raw_sample_set[self.ids[i]] - min_val) / (max_val - min_val)
            self.sample_set[self.ids[i]] = normalized_series
            i += 1
        print("normalized series: \n {}".format(self.sample_set))

    cpdef np.ndarray[double , ndim=2] getManhattanDistMatrix(self):
        manhattan_matrix = np.zeros(shape=(self.n, self.n), dtype=np.double)
        i = 1
        while i < self.n:
            j = 0
            while j < i:
                dist = getManhattanDistance(self.sample_set[self.ids[i]] , self.sample_set[self.ids[j]])
                manhattan_matrix[i][j] = dist
                manhattan_matrix[j][i] = dist
                j += 1
            i += 1
        # print("manhattan matrix: \n {}".format(manhattan_matrix))
        return manhattan_matrix

    cpdef np.ndarray[double , ndim=2] getEuclideanDistMatrix(self):
        euclidean_matrix = np.zeros(shape=(self.n, self.n), dtype=np.double)
        i = 1
        while i < self.n:
            j = 0
            while j < i:
                dist = getEuclideanDistance(self.sample_set[self.ids[i]] , self.sample_set[self.ids[j]])
                euclidean_matrix[i][j] = dist
                euclidean_matrix[j][i] = dist
                j += 1
            i += 1
        # print("euclidean matrix: \n {}".format(euclidean_matrix))
        return euclidean_matrix

    cpdef np.ndarray[double , ndim=2] getDtwDistMatrix(self):
        dtw_matrix = np.zeros(shape=(self.n, self.n), dtype=np.double)
        i = 1
        while i < self.n:
            j = 0
            while j < i:
                dist = getDtwDistance(self.sample_set[self.ids[i]] , self.sample_set[self.ids[j]])
                dtw_matrix[i][j] = dist
                dtw_matrix[j][i] = dist
                j += 1
            i += 1
        # print("dtw_matrix: \n {}".format(dtw_matrix))
        return  dtw_matrix