import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from utils.postgre_db import DBSession, BackTest


def doOneBackTest(pattern_name, n_fluctuation, standard_level, engine):
    """
    对于一个二级模式的分层进行回测及统计
    """
    # 提取最小样本集
    df = pd.read_sql_query(sql="select * from min_sample "
                               "where pattern_name=\'{}\' and n_fluctuation={} and standard_level={}".
                           format(pattern_name, n_fluctuation, standard_level), con=engine)
    # df = df.head(10)
    n_samples = len(df)
    ts_code_arr = df.ts_code.values
    i_end_arr = df.i_end.values
    relative_worth_matrix = np.zeros(shape=(6, n_samples))
    # 计算对数相对净值
    for n in range(n_samples):
        bar_df = pd.read_sql_query(sql="select close from stock_day_bar "
                                       "where ts_code=\'{}\' and i>={} and i<={} ".
                                   format(ts_code_arr[n], i_end_arr[n], i_end_arr[n]+5), con=engine)
        bar_arr = bar_df.close.values
        relative_worth_matrix[1][n] = math.log2(bar_arr[1]/bar_arr[0])
        relative_worth_matrix[2][n] = math.log2(bar_arr[2]/bar_arr[0])
        relative_worth_matrix[3][n] = math.log2(bar_arr[3]/bar_arr[0])
        relative_worth_matrix[5][n] = math.log2(bar_arr[5]/bar_arr[0])

    # 统计分布
    x = np.linspace(-2, 2, 40)
    forward_points = [1, 2, 3, 5]
    for forward_p in forward_points:
        samples_arr = relative_worth_matrix[forward_p]
        x_dist = constructXDistribution(samples_arr)
        miu = np.mean(samples_arr)
        sigma = np.std(samples_arr)
        print("均值{}, 标准差{}".format(miu, sigma))
        n_dist = constructNormalDistribution(miu, sigma)
        kl_div = countKlDiv(x_dist, n_dist)
        result_obj = [{"pattern_name": pattern_name, "n_fluctuation": n_fluctuation, "standard_level": standard_level,
                       "forward_p": forward_p, "mean": miu, "std": sigma, "kl_div": kl_div}]
        DBSession.bulk_insert_mappings(BackTest, result_obj)
        DBSession.commit()


def constructXDistribution(sample_arr):
    """
    构造样本集的分布
    输出频率分布
    """
    # 统计频数
    y = np.zeros(shape=40, dtype=np.int)
    index_arr = ((sample_arr+2)*10).astype(np.int)
    for index in index_arr:
        y[index] += 1
    # 归一化
    y = y/np.sum(y)
    return y


def constructNormalDistribution(miu, sigma):
    """
    构造离散正态分布
    输出频率分布
    """
    # 构造正态分布
    x = np.linspace(-2, 2, 40)
    y_raw = (1/(math.sqrt(2*math.pi)*sigma)) * np.exp(-(x-miu)**2/(2*sigma**2))
    # 归一化
    y = y_raw/np.sum(y_raw)
    return y


def countKlDiv(x_dist, n_dist):
    """
    计算 K-L 散度
    """
    new_x_dist = []
    new_n_dist = []
    for i in range(40):
        if n_dist[i] != 0 and x_dist[i] != 0:
            new_x_dist.append(x_dist[i])
            new_n_dist.append(n_dist[i])
        else:
            pass
    x_dist = np.array(new_x_dist) / sum(new_x_dist)
    n_dist = np.array(new_n_dist) / sum(new_n_dist)
    return np.sum(x_dist*np.log10(x_dist/n_dist))


def paintImg(x, x_dist, n_dist, filename):
    """
    绘制分布曲线
    """
    plt.plot(x, x_dist, "r-", linewidth=2)
    plt.plot(x, n_dist, "r-", linewidth=2)
    plt.grid(True)
    plt.show()
    abs_path = os.path.abspath('.')
    stat_img_name = "{}/data/stat_img/{}.png".format(abs_path, filename)
    plt.savefig(stat_img_name)
    return stat_img_name


if __name__ == "__main__":
    samples = np.random.random(1000)*4-2

