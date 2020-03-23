# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd

cimport numpy as np
from libcpp.map cimport map as cpp_map
from libcpp.string cimport string

# @cython.boundscheck(False) # turn off bounds-checking for entire function
# @cython.wraparound(False)  # turn off negative index wrapping for entire function

cdef class PipArrDetector:
    cdef np.ndarray series

    cdef np.ndarray i_start_series
    cdef np.ndarray i_end_series

    cdef int i_pip
    cdef double vd_max
    
    cdef cpp_map[int, cpp_map[int, int]] i_pip_map
    cdef cpp_map[int, cpp_map[int, double]] vd_map
    cdef n_row


    def __cinit__(self , np.ndarray[double , ndim=1] series):
        self.series = series
        self.i_pip = 0
        self.vd_max = 0


    cpdef void find_pip_map(self):
        """
        对一段时间序列，返回所有时间窗的pip
        :type series: 时间序列
        :return: 全局pip表（dataframe）
        """
        # 预生成pip容器
        cdef int min_d = 3
        cdef int max_d = 200
        cdef int n = len(self.series)

        cdef int i_l = 0
        cdef int i_r
        cdef int n_row = 0
        while i_l < n:
            i_r = i_l + min_d
            while i_r < n and i_r < i_l + max_d:
                i_r += 1
                n_row += 1
            i_l += 1

        cdef np.ndarray[int , ndim=1] i_start_series
        cdef np.ndarray[int , ndim=1] i_end_series
        i_start_series = np.full(shape=n_row , fill_value=-1 , dtype=np.intc)
        i_end_series = np.full(shape=n_row , fill_value=-1 , dtype=np.intc)
        i_l = 0
        cdef i_row = 0
        while i_l < n:
            i_r = i_l + min_d
            while i_r < n and i_r < i_l + max_d:
                i_start_series[i_row] = i_l
                i_end_series[i_row] = i_r
                i_row += 1
                i_r += 1
            i_l += 1
        self.i_start_series = i_start_series
        self.i_end_series = i_end_series


        # 将pip与vd填入容器
        cdef np.ndarray[double , ndim=1] vd_series
        cdef np.ndarray[int , ndim=1] i_pip_series = np.full(shape=n_row , fill_value=-1 , dtype=np.intc)
        vd_series = np.full(shape=n_row , fill_value=-1 , dtype=np.double)
        i_l = 0
        i_row = 0
        # cdef i_pip
        # cdef vd
        while i_l < n:
            i_r = i_l + min_d
            while i_r < n and i_r < i_l + max_d:
                self.find_one_pip(i_l , i_r)
                i_pip_series[i_row] = self.i_pip
                vd_series[i_row] = self.vd_max
                i_row += 1
                i_r += 1
            i_l += 1


        # 转换为pip_map
        i_row = 0

        while i_row < n_row:
            self.i_pip_map[i_start_series[i_row]][i_end_series[i_row]] = i_pip_series[i_row]
            self.vd_map[i_start_series[i_row]][i_end_series[i_row]] = vd_series[i_row]
            i_row += 1
        self.n_row = i_row

        return 

    cpdef void find_one_pip(self , int i_l , int i_r):
        """
        对于一段时间窗，返回most important pip以及对应的vd
        :param i_l: 左界id
        :param i_r: 右界id
        :return: 
        """
        cdef np.ndarray[double , ndim=1] series = self.series
        cdef double p_l = series[i_l]
        cdef double p_r = series[i_r]
        cdef double k = (p_r - p_l) / (i_r - i_l)

        cdef double vd
        cdef int i
        cdef double p_i

        self.i_pip = i_l
        self.vd_max = 0

        for i in range(i_l + 1 , i_r):
            p_i = series[i]
            vd = abs(p_i - (p_l + k * (i - i_l)))
            if vd > self.vd_max:
                self.vd_max = vd
                self.i_pip = i
        return


    cpdef find_all_pip_arr(self):
        """
        对时间序列的所有子窗，迭代pip，直到不再找到pip或pip数达到上界
        :return:
        """
        # 读取pip_map
        cdef int max_n_pip = 10
        cdef int min_n_pip = 5
        cdef int max_win_len = 100
        cdef int min_win_len = 30
        cdef int n_row = self.n_row
        cdef cpp_map[int, cpp_map[int, int]] i_pip_map = self.i_pip_map
        cdef cpp_map[int, cpp_map[int, double]] vd_map = self.vd_map
        cdef np.ndarray[int , ndim=1] i_start_series = self.i_start_series
        cdef np.ndarray[int , ndim=1] i_end_series = self.i_end_series


        # 迭代all_pip_arr
        cdef int i_l
        cdef int i_r
        all_pip_arr = []

        i_row = 0
        while i_row < n_row:
            i_l = i_start_series[i_row]
            i_r = i_end_series[i_row]
            if min_win_len < i_r-i_l < max_win_len:
                pip_arr, n_pip = self.find_one_pip_arr(i_pip_map, vd_map, i_l, i_r, max_n_pip)
                if n_pip >= min_n_pip:
                    all_pip_arr.append(pip_arr)
            i_row += 1

        return all_pip_arr


    cpdef find_latest_pip_arr(self):
        """
        对所有右界为最新点的子窗，迭代pip，直到不再找到pip或pip数达到上界
        :return:
        """
        # 读取pip_map
        cdef int max_n_pip = 10
        cdef int min_n_pip = 5
        cdef int max_win_len = 100
        cdef int min_win_len = 30
        cdef int n_row = self.n_row
        cdef cpp_map[int, cpp_map[int, int]] i_pip_map = self.i_pip_map
        cdef cpp_map[int, cpp_map[int, double]] vd_map = self.vd_map


        # 迭代all_pip_arr
        cdef int i_r = self.i_end_series[-1]
        cdef int i_l = i_r - max_win_len + 1
        all_pip_arr_series = []

        i_row = 0
        while i_l < i_r - min_win_len:
            pip_arr, n_pip = self.find_one_pip_arr(i_pip_map, vd_map, i_l, i_r, max_n_pip)
            if n_pip >= min_n_pip:
                all_pip_arr_series.append(pip_arr)
            i_l += 1

        return all_pip_arr_series


    cpdef find_one_pip_arr(self, cpp_map[int, cpp_map[int, int]]& i_pip_map,
        cpp_map[int, cpp_map[int, double]]& vd_map, int i_l, int i_r, int max_n_pip):
        """
        给定左右界，确定截取时序内的pip_arr
        注意pip_link 与pip_series的不同：
        pip_link按时序排列
        pip_series按出现顺序排列
        return: pip队列，按迭代出现顺序排列（非时序的）
        """
        # t1 = time.time()
        # 初始化
        i_pip_series = [i_l, i_r]
        i_pip_link = [i_l, i_r]

        cdef double max_vd = 0
        cdef int pip_insert_index = -1
        cdef int max_vd_i_pip

        cdef int n_pip = 2
        cdef int i
        cdef int i_pip
        cdef int i_pip_next
        cdef int i_mid_pip
        cdef double vd

        # pip迭代
        while n_pip < max_n_pip:
            pip_insert_index = -1
            max_vd = 0

            # pip链遍历
            for i, i_pip in enumerate(i_pip_link[:-1]):
                i_pip_next = i_pip_link[i+1]

                try:
                    i_mid_pip = i_pip_map[i_pip][i_pip_next]
                    vd = vd_map[i_pip][i_pip_next]
                    if vd > max_vd:
                        max_vd = vd
                        max_vd_i_pip = i_mid_pip
                        pip_insert_index = i+1
                except:
                    pass

            # 检视
            if pip_insert_index != -1:
                i_pip_link.insert(pip_insert_index, max_vd_i_pip)
                i_pip_series.append(max_vd_i_pip)
                n_pip += 1
            else:
                return i_pip_series, n_pip
        return i_pip_series, n_pip
