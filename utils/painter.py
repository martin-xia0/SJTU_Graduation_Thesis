import pyecharts.options as opts
from pyecharts.charts import Line, Candlestick
from pyecharts.globals import ThemeType
import numpy as np
import os

import pandas as pd
import time
import sys


def paintChart(p_series, sample, mode="save"):
    """
    k线样本绘制
    1.画出时间序列
    2.标注感知关键点
    3.画出形态
    """
    c = (
        Line(
            init_opts=opts.InitOpts(
                width="1500px",
                height="600px",
                page_title="Pattern Alpha",
                theme=ThemeType.SHINE
            )
        )
            .add_xaxis(
            xaxis_data=list(range(sample.i_start, sample.i_end))
        )
            .add_yaxis(
            series_name=sample.ts_code,
            y_axis=p_series[sample.i_start: sample.i_end],
            symbol="circle",
            is_symbol_show=True
        )
            .set_global_opts(
            yaxis_opts=opts.AxisOpts(is_scale=True),
            xaxis_opts=opts.AxisOpts(is_scale=True),
            title_opts=opts.TitleOpts(title="{} {}".format(sample.ts_code, sample.pattern_name),
                                      subtitle="{}~{}".format(sample.start_date, sample.end_date))
        )
    )
    # d = (
    #     Line(
    #         init_opts=opts.InitOpts(
    #             width="1500px",
    #             height="600px",
    #             theme=ThemeType.SHINE
    #         )
    #     )
    #         .add_xaxis(
    #         xaxis_data=[int(dot) for dot in sample.pip_arr]
    #     )
    #         .add_yaxis(
    #         series_name="overlap",
    #         y_axis=[p_series[dot] for dot in sample.pip_arr],
    #         symbol="circle",
    #         symbol_size=10,
    #         markpoint_opts=opts.MarkPointOpts(
    #             data=[opts.MarkPointItem(name="Sample Pattern", coord=[int(dot), p_series[dot]], value=p_series[dot])
    #                   for dot in sample.pip_arr]
    #         ),
    #     )
    # )
    # c.overlap(d)

    if mode == "save":
        abs_path = os.path.abspath('.')
        chart_img_dir = "{}/data/chart_img/{}".format(abs_path, sample.pattern_name)
        if not os.path.exists(chart_img_dir):
            os.mkdir(chart_img_dir)
        filename = chart_img_dir + "/{} {}~{} len={} n={}.html"\
            .format(sample.ts_code, sample.start_date, sample.end_date, sample.i_end-sample.i_start, len(sample.pip_arr))
        c.render(filename)
        return filename
    elif mode == "show":
        c.show()
        return c


def paintCandlestick(bar_series, sample):
    x_data = ["2017-10-24" , "2017-10-25" , "2017-10-26" , "2017-10-27"]
    y_data = [[20 , 30 , 10 , 35] , [40 , 35 , 30 , 55] , [33 , 38 , 33 , 40] , [40 , 40 , 32 , 42]]

    (
        Candlestick(init_opts=opts.InitOpts(width="1440px" , height="720px"))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(series_name="", y_axis=y_data)
            .set_series_opts()
            .set_global_opts(
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(
                    is_show=True , linestyle_opts=opts.LineStyleOpts(width=1)
                )
            )
        )
            .render("basic_candlestick.html")
    )


if __name__ == "__main__":
    paintCandlestick()