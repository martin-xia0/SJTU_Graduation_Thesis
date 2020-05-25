# -*- coding: UTF-8 -*-
import tushare as ts
import json
import os
import pandas as pd
import numpy as np
import time


from utils import postgre_db as db


def load_stock_buckets():
    """
    加载股票代码号
    :return: 股票代码集合
    """
    api = ts.pro_api('9acf13f5ec83f05b137ad7416bd2a624ed4d0c235fd096a87bc00ce2')
    df = api.stock_basic(list_status='L')
    stock_codes = df.ts_code
    return stock_codes


def save_stock_day_series_to_excel(code):
    """
    根据股票代码，加载A股日线数据，存上市以来时间序列
    """
    print('saving stock {} data'.format(code))
    api = ts.pro_api('9acf13f5ec83f05b137ad7416bd2a624ed4d0c235fd096a87bc00ce2')
    df = api.daily(ts_code=code, adj='qfq')
    with pd.ExcelWriter("../data/stock_daily/" + code + ".xlsx") as writer:
        df.to_excel(writer, index=False)
    return df


def save_stock_day_series_to_postgre(code, engine):
    """
    用postgre存股票日线数据
    :param code:
    :param engine:
    :return:
    """
    print('saving stock {} data'.format(code))
    api = ts.pro_api('9acf13f5ec83f05b137ad7416bd2a624ed4d0c235fd096a87bc00ce2')
    df = api.daily(ts_code=code, adj='qfq')[::-1].reset_index(drop=True)
    df["i"] = df.index
    df.to_sql(name="stock_day_bar", con=engine, index=False, if_exists="append")


def save_all_stock_series(save_to="postgre"):
    """
    存所有股票日线数据到
    :return:
    """
    stock_codes = load_stock_buckets()
    print("开始下载数据")
    print(stock_codes)
    if save_to == "postgre":
        engine = db.init_engine()
        i = 0
        for i, code in enumerate(stock_codes):
            save_stock_day_series_to_postgre(code, engine)
            print("已存储第{}支股票 {}".format(i, code))
            time.sleep(0.301)
    elif save_to == "excel":
        i = 0
        for i , code in enumerate(stock_codes):
            save_stock_day_series_to_excel(code)
            print("已存储第{}支股票 {}".format(i, code))
            time.sleep(0.301)
    print("下载数据完成")
    return

    

