# -*- coding: UTF-8 -*-

import time
import numpy as np
import pandas as pd


def searchAllPattern():
    """
    工作模式
    1.跑出所有子窗的pip_arr
    2.对所有pip_arr匹配pattern模式
    3.对所有股票执行上述操作
    只需执行一遍可获得所有数据，存数据库
    """
    from pattern_recognition.pip_arr import PipArrDetector
    from pattern_recognition.pattern import is_pattern, name_dict
    from utils.postgre_db import initEngine, DBSession, getStockDayBars, getStockBuckets
    from utils.postgre_db import Pattern
    engine = initEngine()
    Pattern.__table__.drop(engine)
    Pattern.__table__.create(engine)
    # codes = ["600618.SH"]
    codes = getStockBuckets(engine)

    t1 = time.time()
    counter = {pattern_name: 0 for pattern_name in name_dict}
    for code in codes:
        print("开始处理 {}".format(code))
        t2 = time.time()
        bar_series = getStockDayBars(code, engine)

        p_series = bar_series["close"].values
        date_series = bar_series["trade_date"].values

        d = PipArrDetector(p_series)
        d.findPipMap()
        print("获得pip映射表 {}".format(time.time() - t2))

        pip_arr_series = d.findAllPipArr()
        print("获得pip序列集 {}".format(time.time() - t2))

        for pip_arr in pip_arr_series:
            i_l = pip_arr[0]
            i_r = pip_arr[1]
            for n in range(6, 9):
                pip_link = sorted(pip_arr[:n])
                pip_p_series = [p_series[pip] for pip in pip_link]
                for pattern_name in name_dict:
                    if is_pattern(pattern_name, n, pip_link, pip_p_series):
                        start_date = date_series[i_l]
                        end_date = date_series[i_r]
                        counter[pattern_name] += 1
                        pattern_obj = [{"ts_code": code, "start_date": start_date, "end_date": end_date,
                                        "i_start": i_l, "i_end": i_r,
                                        "pip_arr": pip_link, "pip_p_arr": pip_p_series,
                                        "pattern_name": pattern_name, "n_fluctuation": n}]
                        print("出现{}".format(pattern_obj))
                        DBSession.bulk_insert_mappings(Pattern, pattern_obj)
                        DBSession.commit()
        print("完成模式样本筛选 {}".format(time.time() - t2))
        print("{} 完成，耗时 {}".format(code, time.time()-t2))
        print("总耗时 {}".format(time.time()-t1))
    print(counter)
    print("最大样本集存储完毕！")


def selectAllPurePattern():
    """
    工作模式
    去重获得提纯样本
    """
    recreateTable(table_name="pure_pattern")
    pattern_names = ["triangles_ascending_up", "triangles_ascending_down", "triangles_descending_up",
                     "triangles_descending_down", "triangles_symmetrical_up", "triangles_symmetrical_dow"]
    n_fluctuations = [6, 7, 8]
    for pattern_name in pattern_names:
        for n in n_fluctuations:
            selectOnePurePattern(pattern_name, n)


def selectOnePurePattern(pattern_name, n_fluctuation):
    """
    去重模式
    去除pattern表中重复的样本
    """
    from utils.postgre_db import initEngine, DBSession
    from utils.postgre_db import PurePattern
    engine = initEngine()
    print("开始处理 {} 形态 {} 次波动".format(pattern_name, n_fluctuation))
    df = pd.read_sql_query(sql="select * from pattern "
                               "where pattern_name=\'{}\' and n_fluctuation=\'{}\' "
                           .format(pattern_name, n_fluctuation), con=engine)
    print("原样本数量 {}".format(len(df)))
    ts_codes = set(df.ts_code.values)
    for ts_code in ts_codes:
        windows = []
        pattern_df = df[df.ts_code == ts_code]
        n = len(pattern_df)
        i_start_arr = pattern_df.i_start.values.tolist()
        i_end_arr = pattern_df.i_end.values.tolist()
        start_date_arr = pattern_df.start_date.values.tolist()
        end_date_arr = pattern_df.end_date.values.tolist()
        pip_arr_arr = pattern_df.pip_arr.values.tolist()
        pip_p_arr_arr = pattern_df.pip_p_arr.values.tolist()
        print("开始处理{}的{}个样本".format(ts_code, n))
        count = 0
        not_duplicate = True
        for i in range(n):
            i_start = i_start_arr[i]
            i_end = i_end_arr[i]
            for window in windows:
                if (i_end-window[0]) * (i_start-window[1]) < 0:
                    not_duplicate = False
                    break
            if not_duplicate:
                count += 1
                windows.append((i_start, i_end))
                pure_pattern_obj = [{"ts_code": ts_code, "start_date": start_date_arr[i], "end_date": end_date_arr[i],
                                     "i_start": i_start, "i_end": i_end,
                                     "pip_arr": pip_arr_arr[i], "pip_p_arr": pip_p_arr_arr[i],
                                     "pattern_name": pattern_name, "n_fluctuation": n_fluctuation}]
                # print("出现{}".format(pure_pattern_obj))
                DBSession.bulk_insert_mappings(PurePattern, pure_pattern_obj)
                DBSession.commit()
        print("去重后剩余{}个样本".format(count))
    return


def concentrateAllPattern():
    """
    工作模式
    提炼所有样本
    """
    recreateTable(table_name="min_sample")
    pattern_names = ["triangles_ascending_up", "triangles_ascending_down", "triangles_descending_up",
                     "triangles_descending_down", "triangles_symmetrical_up", "triangles_symmetrical_dow"]
    n_fluctuations = [6, 7, 8]
    for pattern_name in pattern_names:
        for n in n_fluctuations:
            concentrateOnePattern(pattern=pattern_name, n=n)


def concentrateOnePattern(pattern, n):
    """
    工作模式
    1.求取一阶距离矩阵
    2.求取收缩集索引
    3.求取二阶距离矩阵
    """
    from utils.postgre_db import initEngine, DBSession
    from utils.postgre_db import MinSample
    from pattern_concentration.dist_matrix import DistMatrix
    from pattern_concentration.optimal_set import OptimalSet

    engine = initEngine()

    t2 = time.time()
    # 生成最大集
    print("开始处理 {} 次波动 {} 形态".format(pattern, n))
    df = pd.read_sql_query(sql="select * from pure_pattern "
                               "where pattern_name=\'{}\' and n_fluctuation=\'{}\' "
                           .format(pattern, n), con=engine)
    # df = df.head(100)
    print("最大样本集样本容量 {}".format(len(df)))
    sample_ids = df.id.values
    pip_p_arrs = df.pip_p_arr.values
    n_max = len(sample_ids)
    raw_max_set = {sample_ids[i]: np.array(pip_p_arrs[i]) for i in range(n_max)}
    print("生成最大样本集 {}个样本：\n {}".format(n_max, raw_max_set))
    print("耗时 {}".format(time.time()-t2))
    del pip_p_arrs

    # 生成一阶距离矩阵
    matrix_1 = DistMatrix(raw_max_set)
    matrix_1.normalizeSeries()
    del raw_max_set
    lev_1_mat = matrix_1.getEuclideanDistMatrix()
    # print("生成一阶矩阵：\n {}".format(lev_1_mat))
    print("耗时 {}".format(time.time() - t2))

    # 最优缩小集提取
    optimizer_1 = OptimalSet(lev_1_mat, sample_ids, 0.5)
    del lev_1_mat
    optimizer_1.getKernelSet()
    shrink_set = optimizer_1.getOptimalSet()
    shrink_ids = np.array([sample_ids[i] for i in shrink_set])
    print("获得缩小集索引 {}个样本：\n {}".format(len(shrink_ids), shrink_ids))
    print("耗时 {}".format(time.time() - t2))

    # 生成最优缩小集
    raw_shrink_set = {}
    for sample_id in shrink_ids:
        sample_row = df.loc[df["id"] == sample_id]
        ts_code = sample_row["ts_code"].values[0]
        i_start = sample_row["i_start"].values[0]
        i_end = sample_row["i_end"].values[0]
        sample_val_series = pd.read_sql_query(sql="select close from stock_day_bar "
                                                  "where ts_code=\'{}\' and i>=\'{}\' and i<=\'{}\' ".
                                              format(ts_code, i_start, i_end), con=engine)["close"].values
        raw_shrink_set[sample_id] = sample_val_series
    print("生成收缩集：\n {}".format(raw_shrink_set))
    print("耗时 {}".format(time.time() - t2))

    # 生成二阶距离矩阵
    matrix_2 = DistMatrix(raw_shrink_set)
    matrix_2.normalizeSeries()
    lev_2_mat = matrix_2.getDtwDistMatrix()
    # print("生成二阶矩阵：\n {}".format(lev_2_mat))
    print("耗时 {}".format(time.time() - t2))

    # 最小集提取
    optimizer_2 = OptimalSet(lev_2_mat, shrink_ids, 0.5)
    optimizer_2.getKernelSet()
    min_set = optimizer_2.getOptimalSet()
    min_ids = np.array([shrink_ids[i] for i in min_set])
    print("获得最小集 {}个样本：\n {}".format(len(min_ids), min_ids))
    min_level_dict = optimizer_2.divideLevels(id_set=min_ids, n_levels=5)
    # print("生成最小集分层：\n {}".format(min_level_dict))
    print("耗时 {}".format(time.time()-t2))

    # 最小集存储
    for i_level, i_level_ids in min_level_dict.items():
        for sample_id in i_level_ids:
            sample_row = df.loc[df["id"] == sample_id]
            ts_code = sample_row["ts_code"].values[0]
            i_end = int(sample_row["i_end"].values[0])
            pattern_name = sample_row["pattern_name"].values[0]
            n_fluctuation = int(sample_row["n_fluctuation"].values[0])
            pattern_id = int(sample_row["id"].values[0])
            sample_obj = [{"ts_code": ts_code, "i_end": i_end, "pattern_name": pattern_name,
                           "pattern_id": pattern_id, "n_fluctuation": n_fluctuation, "standard_level": i_level}]
            DBSession.bulk_insert_mappings(MinSample, sample_obj)
            DBSession.commit()
    print("最小样本集筛选并存储完毕！")
    print("耗时 {}".format(time.time() - t2))


def doBackTest():
    """
    回测实验主函数
    """
    from back_testing.back_test import doOneBackTest
    from utils.postgre_db import initEngine
    from utils.postgre_db import MinSample
    engine = initEngine()
    recreateTable(table_name="back_test")
    pattern_names = ["triangles_ascending_up", "triangles_ascending_down", "triangles_descending_up",
                     "triangles_descending_down", "triangles_symmetrical_up", "triangles_symmetrical_dow"]
    n_fluctuations = [6, 7, 8]
    standard_levels = [1, 2, 3, 4, 5]
    doOneBackTest(pattern_names[0], n_fluctuations[0], standard_levels[0], engine)


def scanDb(table):
    """
    扫描模式
    扫描数据库特定表特定字段
    """
    from utils.postgre_db import initEngine, DBSession, getStockDayBars, getStockBuckets
    from utils.postgre_db import Pattern
    engine = initEngine()
    print("当前数据表 {}".format(engine.table_names()))
    if table == "stock_day_bar":
        code = "600318.SH"
        df = pd.read_sql_query(sql="select * from stock_day_bar where ts_code=\'{}\'".format(code), con=engine)
        print(df.shape)
    elif table == "pattern":
        pattern = "triangles_ascending_up"
        n = 6
        df = pd.read_sql_query(sql="select * from pattern "
                                   "where pattern_name=\'{}\' and n_fluctuation=\'{}\' ".format(pattern, n), con=engine)
        print(df)
        print(df.shape)
        print("已扫描股票数量 {}".format(len(set(df.ts_code.values))))
    elif table == "min_sample":
        pattern = "triangles_ascending_up"
        df = pd.read_sql_query(sql="select * from min_sample "
                                   "where pattern_name=\'{}\'".format(pattern), con=engine)
        print(df)
        print(df.shape)
    elif table == "back_test":
        df = pd.read_sql_query(sql="select * from back_test", con=engine)
        # "where pattern_name=\'{}\'".format(pattern), con=engine)
        print(df)
        print(df.shape)
    elif table == "pure_pattern":
        pattern = "triangles_ascending_up"
        n = 6
        df = pd.read_sql_query(sql="select * from pure_pattern "
                                   "where pattern_name=\'{}\' and n_fluctuation=\'{}\' ".format(pattern, n), con=engine)
        print(df)
        print(df.shape)


def recreateDb():
    """
    重建数据库（慎用）
    1.删除原有数据表
    2.重建数据表
    3.更新k线原始数据
    """
    from utils.postgre_db import initEngine, DBSession, initStockBuckets
    from utils.postgre_db import Pattern
    from utils.io_processor import saveAllStockSeriesToPostGre
    engine = initEngine(recreate_all=True)
    print("当前数据表 {}".format(engine.table_names()))
    saveAllStockSeriesToPostGre(engine)
    initStockBuckets(engine)
    print("完成数据库重建")


def recreateTable(table_name):
    """
    重建数据表（慎用）
    """
    from utils.postgre_db import initEngine
    from utils.postgre_db import Pattern, PurePattern, MinSample, BackTest
    engine = initEngine()
    if table_name == "pattern":
        Pattern.__table__.drop(engine)
        Pattern.__table__.create(engine)
    elif table_name == "pure_pattern":
        PurePattern.__table__.drop(engine)
        PurePattern.__table__.create(engine)
    elif table_name == "min_sample":
        MinSample.__table__.drop(engine)
        MinSample.__table__.create(engine)
    elif table_name == "back_test":
        BackTest.__table__.drop(engine)
        BackTest.__table__.create(engine)


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
    # searchAllPattern()
    # scanDb(table="pattern")

    # selectAllPurePattern()
    # scanDb(table="pure_pattern")

    concentrateAllPattern()
    scanDb(table="min_sample")

    # doBackTest()
    # scanDb(table="back_test")

    # testSampleConcentration()
    # testSamplePainting()