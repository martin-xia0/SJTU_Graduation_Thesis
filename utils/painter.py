import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType
import numpy as np
import os

import pandas as pd
import time
import sys


class Painter:
    """
    存储器，负责处理后数据的输出存储
    LOG 指存内存
    SAVE 指存本地
    """

    def __init__(self , code , series):
        self.code = code
        self.series = series

    def draw_window(self , i_l , i_r , pips , start_date , end_date , pattern_id, mode="save"):
        """
        1.画出时间序列
        2.标注感知关键点
        3.画出形态
        """
        c = (
            Line(
                init_opts=opts.InitOpts(
                    width="1500px" ,
                    height="600px" ,
                    page_title="Pattern Alpha" ,
                    theme=ThemeType.SHINE
                )
            )
                .add_xaxis(
                xaxis_data=self.series[i_l: i_r+1].index
            )
                .add_yaxis(
                series_name=self.code ,
                y_axis=self.series[i_l: i_r+1].values.tolist() ,
                symbol="circle" ,
            )
                .set_global_opts(
                yaxis_opts=opts.AxisOpts(is_scale=True) ,
                xaxis_opts=opts.AxisOpts(is_scale=True) ,
                title_opts=opts.TitleOpts(title="{} Pattern{}".format(self.code , pattern_id) ,
                                          subtitle="{}~{}".format(start_date , end_date))
            )
        )
        d = (
            Line(
                init_opts=opts.InitOpts(
                    width="1500px" ,
                    height="600px" ,
                    theme=ThemeType.SHINE
                )
            )
                .add_xaxis(
                xaxis_data=[int(dot) for dot in pips]
            )
                .add_yaxis(
                series_name="overlap" ,
                y_axis=[self.series[dot] for dot in pips] ,
                symbol="circle" ,
                symbol_size=10 ,
                markpoint_opts=opts.MarkPointOpts(
                    data=[opts.MarkPointItem(name="pip" , coord=[int(dot) , self.series[dot]] , value=self.series[dot]) for dot in
                          pips]
                ) ,
            )
        )
        c.overlap(d)
        if mode=="save":
            vis_dir = "./vis/Pattern_{}".format(pattern_id)
            if not os.path.exists(vis_dir):
                os.mkdir(vis_dir)
            filename = vis_dir + "/{} {}~{} len={} n={}.html".format(self.code , start_date , end_date , i_r-i_l , len(pips))
            c.render(filename)
            return filename
        if mode=="mock":
            vis_dir = "./templates/"
            filename = "Pattern_{} {} {}~{} len={} n={}.html".format(pattern_id, self.code , start_date , end_date , i_r-i_l , len(pips))
            c.render(vis_dir + filename)
            return filename
        
        else:
            return c
