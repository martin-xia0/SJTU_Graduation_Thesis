# -*- coding: UTF-8 -*-

import numpy as np

import time
cimport numpy as np
from libcpp.string cimport string


def pattern_1(n , pip_link , pip_p_series):
    if n % 2 == 0 and n >= 6:
        return is_local_min_max(n , pip_p_series , 1) \
               and is_uniform_series(pip_p_series , range(1 , n , 2)) \
               and is_increase_series(pip_p_series , range(0 , n , 2))
    elif n % 2 == 1 and n >= 7:
        return is_local_min_max(n , pip_p_series , 0) \
               and is_uniform_series(pip_p_series , range(0 , n , 2)) \
               and is_increase_series(pip_p_series , range(1 , n , 2))
    else:
        return False


def pattern_2(n , pip_link , pip_p_series):
    if n % 2 == 0 and n >= 6:
        return is_local_min_max(n , pip_p_series , 0) \
               and is_uniform_series(pip_p_series , range(0 , n , 2)) \
               and is_increase_series(pip_p_series , range(1 , n , 2))
    elif n % 2 == 1 and n >= 7:
        return is_local_min_max(n , pip_p_series , 1) \
               and is_uniform_series(pip_p_series , range(1 , n , 2)) \
               and is_increase_series(pip_p_series , range(0 , n , 2))
    else:
        return False


def pattern_3(n , pip_link , pip_p_series):
    if n % 2 == 0 and n >= 6:
        return is_local_min_max(n , pip_p_series , 1) \
               and is_uniform_series(pip_p_series , range(0 , n , 2)) \
               and is_decrease_series(pip_p_series , range(1 , n , 2))
    elif n % 2 == 1 and n >= 7:
        return is_local_min_max(n , pip_p_series , 0) \
               and is_uniform_series(pip_p_series , range(1 , n , 2)) \
               and is_decrease_series(pip_p_series , range(0 , n , 2))
    else:
        return False


def pattern_4(n , pip_link , pip_p_series):
    if n % 2 == 0 and n >= 6:
        return is_local_min_max(n , pip_p_series , 0) \
               and is_uniform_series(pip_p_series , range(1 , n , 2)) \
               and is_decrease_series(pip_p_series , range(0 , n , 2))
    elif n % 2 == 1 and n >= 7:
        return is_local_min_max(n , pip_p_series , 1) \
               and is_uniform_series(pip_p_series , range(0 , n , 2)) \
               and is_decrease_series(pip_p_series , range(1 , n , 2))
    else:
        return False


def pattern_5(n , pip_link , pip_p_series):
    if n % 2 == 0 and n >= 6:
        return is_local_min_max(n , pip_p_series , 1) \
               and is_increase_series(pip_p_series , range(0 , n , 2)) \
               and is_decrease_series(pip_p_series , range(1 , n , 2))
    elif n % 2 == 1 and n >= 7:
        return is_local_min_max(n , pip_p_series , 0) \
               and is_increase_series(pip_p_series , range(1 , n , 2)) \
               and is_decrease_series(pip_p_series , range(0 , n , 2))
    else:
        return False


def pattern_6(n , pip_link , pip_p_series):
    if n % 2 == 0 and n >= 6:
        return is_local_min_max(n , pip_p_series , 0) \
               and is_increase_series(pip_p_series , range(1 , n , 2)) \
               and is_decrease_series(pip_p_series , range(0 , n , 2))
    elif n % 2 == 1 and n >= 7:
        return is_local_min_max(n , pip_p_series , 1) \
               and is_increase_series(pip_p_series , range(0 , n , 2)) \
               and is_decrease_series(pip_p_series , range(1 , n , 2))
    else:
        return False



cpdef bint is_local_min_max(int n , series , bint start_direction):
    """
    验证交错性质：顶部为local_max 底部为local_min
    :param n: pip数
    :param series: pip价格序列
    :param start_direction: 起始方向，up/down
    :return:
    """
    cdef int i
    if start_direction:
        for i in range(1 , n - 1 , 2):
            # 顶部序列
            if series[i] < series[i - 1] or series[i] < series[i + 1]:
                return False
        for i in range(2 , n - 1 , 2):
            # 底部序列
            if series[i] > series[i - 1] or series[i] > series[i + 1]:
                return False
    else:
        for i in range(2 , n - 1 , 2):
            # 顶部序列
            if series[i] < series[i - 1] or series[i] < series[i + 1]:
                return False
        for i in range(1 , n - 1 , 2):
            # 底部序列
            if series[i] > series[i - 1] or series[i] > series[i + 1]:
                return False
    return True


cpdef bint is_local_min(series , index):
    """
    验证是底部
    :param series: pip价格序列
    :param index: 下标集
    :return:
    """
    cdef int i
    for i in index:
        if series[i] > series[i - 1] or series[i] > series[i + 1]:
            return False
    return True


cpdef bint is_local_max(series , index):
    """
    验证是底部
    :param series: pip价格序列
    :param index: 下标集
    :return:
    """
    cdef int i
    for i in index:
        if series[i] < series[i - 1] or series[i] < series[i + 1]:
            return False
    return True


cpdef bint is_increase_series(series , index):
    """
    验证单增
    :param series: pip价格序列
    :param index: 下标集
    :return:
    """
    cdef int i
    cdef int count = len(index)
    for i in range(count - 1):
        if series[index[i + 1]] < series[index[i]]:
            return False
    return True


cpdef bint is_decrease_series(series , index):
    """
    验证单减
    :param index: 下标集
    :param series: pip价格序列
    :return:
    """
    cdef int i
    cdef int count = len(index)
    for i in range(count - 1):
        if series[index[i + 1]] > series[index[i]]:
            return False
    return True


cpdef bint is_uniform_series(series , index):
    """
    验证平稳性
    :param index: 下标集
    :param series: pip价格序列
    :return:
    """
    cdef int i
    cdef double diff_bound = 0.1 * (max(series) - min(series))
    cdef double p_max = series[index[0]]
    cdef double p_min = series[index[0]]
    for i in index:
        if series[i] > p_max:
            p_max = series[i]
        elif series[i] < p_min:
            p_min = series[i]
        if p_max - p_min > diff_bound:
            return False
    return True


cpdef bint is_similar_price(series , int index_i , int index_j):
    """
    验证两点价格相近
    :param series:
    :param index_i:
    :param index_j:
    :return:
    """
    cdef double diff_bound = 0.06 * (max(series) - min(series))
    return abs(series[index_i] - series[index_j]) < diff_bound


cpdef bint is_similar_interval(link , i , j , k , g):
    """
    验证区间均匀分布
    :param link:
    :param i:
    :return:
    """
    cdef double diff_bound = 0.05 * (link[-1] - link[0])
    return abs((link[j] - link[i]) - (link[g] - link[k])) <= diff_bound


cpdef double trend_line_slope(series , index_l , index_r):
    """
    趋势线斜率
    :param series: 价格序列
    :param index_l: 左支撑点下标
    :param index_r: 右支撑点下标
    :return:
    """
    cdef double p_diff = series[index_r] - series[index_l]
    return p_diff / (index_r - index_l)


name_dict = {
  "triangles_ascending_up" : pattern_1,
  "triangles_ascending_down" : pattern_2,
  "triangles_descending_up": pattern_3,
  "triangles_descending_down": pattern_4,
  "triangles_symmetrical_up": pattern_5,
  "triangles_symmetrical_down": pattern_6,
}


def is_pattern(pattern_name, n , pip_link , pip_p_series):
    """
    形态过滤器，对给定的n, pips,  过滤
    继承后改写，默认全通
    :param pattern_name: 形态名，string
    :param n: pip数, int
    :param pip_link: pip在p_series上的点位序列, np.ndarray(int)
    :param pip_p_series: pip的价格序列， np.ndarray(double)
    :return:
    """
    if pattern_name not in name_dict.keys():
        return "Pattern name error!"
    return name_dict[pattern_name](n , pip_link , pip_p_series)