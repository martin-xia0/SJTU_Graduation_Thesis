from sqlalchemy import  Column, Integer, String, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base

# ---模型定义---

Base = declarative_base()


class StockBucket(Base):
    """
    股票代码集合
    """
    __tablename__ = 'stock_bucket'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    ts_code = Column(String(12))


class StockDayBar(Base):
    """
    股票日线
    """
    __tablename__ = 'stock_day_bar'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    ts_code = Column(String(12))
    trade_date = Column(String(10))
    i = Column(Integer())
    open = Column(Float())
    high = Column(Float())
    low = Column(Float())
    close = Column(Float())
    pre_close = Column(Float())
    change = Column(Float())
    pct_chg = Column(Float())
    vol = Column(Float())
    amount = Column(Float())


class Pattern(Base):
    """
    形态
    """
    __tablename__ = 'pattern'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    ts_code = Column(String(12))
    i_start = Column(Integer())
    i_end = Column(Integer())
    start_date = Column(String(10))
    end_date = Column(String(10))
    pip_arr = Column(ARRAY(Integer()))
    pip_p_arr = Column(ARRAY(Float()))
    pattern_name = Column(String(50))
    n_fluctuation = Column(Integer())


class PurePattern(Base):
    """
    去重形态
    """
    __tablename__ = 'pure_pattern'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    ts_code = Column(String(12))
    i_start = Column(Integer())
    i_end = Column(Integer())
    start_date = Column(String(10))
    end_date = Column(String(10))
    pip_arr = Column(ARRAY(Integer()))
    pip_p_arr = Column(ARRAY(Float()))
    pattern_name = Column(String(50))
    n_fluctuation = Column(Integer())


class MinSample(Base):
    """
    最小集样本
    """
    __tablename__ = 'min_sample'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    ts_code = Column(String(12))
    pattern_id = Column(Integer())
    i_end = Column(Integer())
    pattern_name = Column(String(50))
    n_fluctuation = Column(Integer())
    standard_level = Column(Integer())


class BackTest(Base):
    """
    回测结果
    """
    __tablename__ = 'back_test'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    pattern_name = Column(String(50))
    n_fluctuation = Column(Integer())
    standard_level = Column(Integer())
    forward_p = Column(Integer())
    mean = Column(Float())
    std = Column(Float())
    kl_div = Column(Float())


# ---引擎方法---
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
import pandas as pd

DBSession = scoped_session(sessionmaker())


def initEngine(recreate_all=False):
    """
    创建数据库
    :param recreate_all:
    """
    username = "pattern"
    password = "1234@abcd"
    server = "127.0.0.1"
    dbname = "pattern"
    engine = create_engine(
        'postgresql+psycopg2://{}:{}@{}/{}'.format(username, password, server, dbname),
        client_encoding='utf8',
        echo=False,
        isolation_level="REPEATABLE_READ")
    DBSession.remove()
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    if recreate_all:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


def insertDf(df, table, engine):
    """
    将格式对齐的df写入数据库
    :param table:
    :param df:
    :param engine:
    """
    df.to_sql(name=table, con=engine, index=False, if_exists="append")


def initStockBuckets(engine):
    """
    初始化所有股票代码集合
    """
    code_list = pd.read_sql_query(sql="select ts_code from stock_day_bar", con=engine).values.tolist()
    df = pd.DataFrame({"ts_code": list(set([x[0] for x in code_list]))})
    df.to_sql(name="stock_bucket", con=engine, index=False, if_exists="replace")


def getStockBuckets(engine):
    """
    获得所有股票代码集合
    """
    df = pd.read_sql_query(sql="select ts_code from stock_bucket", con=engine)
    return df["ts_code"].values


def getStockDayBars(code, engine):
    """
    将原始k线数据从表中读出
    """
    return pd.read_sql_query(sql="select * from stock_day_bar where ts_code=\'{}\'".format(code), con=engine)


def getStockDayClose(code, engine):
    """
    将原始k线收盘数据从表中读出
    """
    return pd.read_sql_query(sql="select close from stock_day_bar where ts_code=\'{}\'".format(code), con=engine)["close"].values


if __name__ == '__main__':
    initEngine()