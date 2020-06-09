
cimport numpy as np
import numpy as np


cpdef np.ndarray fastSort(np.ndarray num_arr, np.ndarray index, int begin_flag, int end_flag):
    """
    带索引的快速排序
    将数组排序后同时返回调整顺序后的索引
    """
    if begin_flag >= end_flag:
        return

    cdef int i_left = begin_flag
    cdef int i_right = end_flag
    cdef double val_flag = num_arr[begin_flag]
    cdef int index_flag = index[begin_flag]

    while i_left < i_right:
        while num_arr[i_right] >= val_flag and i_left < i_right:
            i_right -= 1
        num_arr[i_left] = num_arr[i_right]
        index[i_left] = index[i_right]
        while num_arr[i_left] <= val_flag and i_left < i_right:
            i_left += 1
        num_arr[i_right] = num_arr[i_left]
        index[i_right] = index[i_left]
    num_arr[i_left] = val_flag
    index[i_left] = index_flag
    # print("完成数组划分 划分中心 {} \n 划分后数组 {} \n 划分后索引 [}".format(i_left, num_arr, index))
    fastSort(num_arr, index, begin_flag, i_left-1)
    fastSort(num_arr, index, i_right+1, end_flag)


cdef class OptimalSet:
    """
    输入 最大集的距离矩阵
    输出 最优子集
    """
    cdef np.ndarray dist_matrix
    cdef np.ndarray full_id_set
    cdef np.ndarray kernel_id_set
    cdef np.ndarray optimal_id_set
    cdef int n_full
    cdef int n_kernel
    cdef int n_optimal

    def __cinit__(self, np.ndarray dist_matrix, np.ndarray full_id_set, double shrink_factor):
        self.dist_matrix = dist_matrix
        self.full_id_set = full_id_set

        self.n_full = len(dist_matrix)
        self.n_optimal = int(self.n_full*shrink_factor) + 1
        self.optimal_id_set = np.zeros(shape=self.n_optimal, dtype=int)
        self.n_kernel = int(self.n_optimal*shrink_factor) + 1
        self.kernel_id_set = np.zeros(shape=self.n_kernel, dtype=int)

    cpdef void getKernelSet(self):
        """
        获得核心集
        """
        # 生成距离和数组
        cdef np.ndarray sum_arr
        cdef np.ndarray sum_index
        cdef int i = 0
        sum_arr = np.zeros(shape=self.n_full, dtype=np.double)
        while i < self.n_full:
            sum_arr[i] = np.sum(self.dist_matrix[i])
            i += 1
        # 距离排序
        sum_index = np.arange(self.n_full)
        print("排序开始 \n 排序前数组 \n {} \n 排序前索引 \n {}".format(sum_arr, sum_index))
        fastSort(sum_arr, sum_index, 0, self.n_full-1)
        print("排序完毕 \n 排序后数组 \n {} \n 排序后索引 \n {}".format(sum_arr, sum_index))
        i = 0
        while i < self.n_kernel:
            self.kernel_id_set[i] = sum_index[i]
            i += 1
        return

    cpdef np.ndarray getOptimalSet(self):
        """
        获得最优子集
        """
        # 生成核心距离和数组
        cdef np.ndarray sum_arr
        cdef np.ndarray sum_index
        cdef int i = 0
        cdef int j = 0
        cdef int kernel_id
        sum_arr = np.zeros(shape=self.n_full, dtype=np.double)
        while i < self.n_full:
            j = 0
            while j < self.n_kernel:
                kernel_id = self.kernel_id_set[j]
                sum_arr[i] += self.dist_matrix[i][kernel_id]
                j += 1
            i += 1

        # 内核距离排序
        sum_index = np.arange(self.n_optimal)
        print("排序开始 \n 排序前数组 \n {} \n 排序前索引 \n {}".format(sum_arr, sum_index))
        fastSort(sum_arr, sum_index, 0, self.n_optimal-1)
        print("排序完毕 \n 排序后数组 \n {} \n 排序后索引 \n {}".format(sum_arr, sum_index))
        i = 0
        while i < self.n_optimal:
            self.optimal_id_set[i] = sum_index[i]
            i += 1
        return self.optimal_id_set

    cpdef dict divideLevels(self , np.ndarray id_set , int n_levels):
        """
        最优子集的层次划分
        """
        step_size = int(len(id_set) / n_levels)
        level_dict = {}
        for i in range(1, n_levels):
            level_dict[i] = id_set[(i - 1) * step_size: i * step_size]
        level_dict[n_levels] = id_set[i * step_size:]
        return level_dict

