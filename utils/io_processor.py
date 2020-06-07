# -*- coding: UTF-8 -*-
import tushare as ts
import json
import os
import pandas as pd
import numpy as np
import time


from utils import postgre_db as db


def loadStockBuckets():
    """
    加载股票代码号
    """
    api = ts.pro_api('9acf13f5ec83f05b137ad7416bd2a624ed4d0c235fd096a87bc00ce2')
    df = api.stock_basic(list_status='L')
    stock_codes = df.ts_code
    return stock_codes


def saveStockDaySeriesToPostGre(code, engine):
    """
    存指定代码的股票日线数据到数据库
    """
    print('saving stock {} data'.format(code))
    api = ts.pro_api('9acf13f5ec83f05b137ad7416bd2a624ed4d0c235fd096a87bc00ce2')
    df = api.daily(ts_code=code, adj='qfq')[::-1].reset_index(drop=True)
    df["i"] = df.index
    df.to_sql(name="stock_day_bar", con=engine, index=False, if_exists="append")


def saveAllStockSeriesToPostGre(engine):
    """
    将所有股票日线数据存入 postgresql 数据库
    """
    stock_codes = loadStockBuckets()
    print("开始下载数据")
    print("所有股票代码 {}".format(stock_codes))
    for i, code in enumerate(stock_codes):
        saveStockDaySeriesToPostGre(code, engine)
        print("已存储第{}支股票 {}".format(i, code))
        time.sleep(0.301)