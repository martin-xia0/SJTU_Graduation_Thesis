import time
import numpy as np
import pandas as pd


def testDistMatrix():
    """
    测试模式
    测试不同距离模型生成的距离矩阵
    """
    from pattern_concentration.dist_matrix import DistMatrix
    s1 = np.array([1, 3, 4, 9, 8, 2, 1, 5, 7, 3], dtype=float)
    s2 = np.array([0, 6, 2, 3, 0, 10, 4, 3, 6, 3], dtype=float)
    sample_set = {"1": s1, "2": s2}
    t1 = time.time()
    matrix = DistMatrix(sample_set)
    matrix.normalizeSeries()
    for _ in range(1):
        matrix.getEuclideanDistMatrix()
        matrix.getManhattanDistMatrix()
        matrix.getDtwDistMatrix()
    # print(matrix.getEuclideanDistMatrix())
    # print(matrix.getManhattanDistMatrix())
    # print(matrix.getDtwDistMatrix())
    print("耗时 {}".format(time.time()-t1))


def testSampleConcentration():
    """
    测试模式
    测试样本集的提取
    """
    from pattern_concentration.optimal_set import fastSort
    sum_arr = np.array([5, 7, 1, 6, 9, 4, 8, 3, 2, 2])
    index = np.arange(len(sum_arr))
    fastSort(sum_arr, index, 0, len(sum_arr)-1)
    print(sum_arr, index)


def testSamplePainting():
    """
    测试模式
    画出单个k线样本
    """
    from utils.painter import paintChart, paintCandlestick
    from utils.postgre_db import initEngine
    from utils.postgre_db import Pattern

    engine = initEngine()

    pattern = "triangles_ascending_up"
    n = 6
    code = "300085.SZ"
    print("开始处理 {} 次波动 {} 形态".format(pattern, n))
    df = pd.read_sql_query(sql="select * from pattern "
                               "where ts_code=\'{}\' and pattern_name=\'{}\' and n_fluctuation=\'{}\' "
                           .format(code, pattern, n), con=engine)
    sample = df.loc[0, :]
    print(sample.id)
    bar_df = pd.read_sql_query(sql="select open, high, low, close from stock_day_bar "
                                   "where ts_code=\'{}\' and i>={} and i<={}"
                               .format(sample.ts_code, sample.i_start, sample.i_end), con=engine)
    open_series = bar_df.open.values
    high_series = bar_df.high.values
    low_series = bar_df.low.values
    close_series = bar_df.close.values
    n = len()
    bar_series = [[]]
    print(len(bar_series))
    paintCandlestick(bar_series, sample)


if __name__ == "__main__":
    testSampleConcentration()
    testSamplePainting()