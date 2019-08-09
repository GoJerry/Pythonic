# coding: utf-8
__author__ = 'Jerry'
"公众号：Python编程与实战,欢迎关注点赞"

import requests
import time
import re
from scrapy import Selector
from datetime import datetime, timedelta

from pyecharts.charts import Pie, Bar, Line
from pyecharts import options as opts


class NeZhaSpider:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = requests.session()
    session.headers = headers

    @classmethod
    def spider(cls):
        cls.session.get("https://piaofang.baidu.com/?sfrom=wise_film_box")
        lz_list = []
        szw_list = []

        for r in [datetime.now() - timedelta(days=i) for i in range(0, 15)]:  # 根据电源上映天数作修改
            params = {
                "pagelets[]": "index-overall",
                "reqID": "28",
                "sfrom": "wise_film_box",
                "date": r.strftime("%Y-%m-%d"),
                "attr": "3,4,5,6",
                "t": int(time.time() * 1000),
            }
            response = cls.session.get("https://piaofang.baidu.com/", params=params).text

            result = eval(re.findall("BigPipe.onPageletArrive\((.*?)\)", response)[0])

            selector = Selector(text=result.get("html"))

            li_list = selector.css(".detail-list .list dd")
            for d in range(len(li_list)):
                dic = {}
                name = li_list[d].css("h3 b ::text").extract_first()
                if '哪吒' in name or "烈火英雄" in name:
                    total_box = li_list[d].css("h3 span ::attr(data-box-office)").extract_first()  # 总票房
                    box = li_list[d].css("div span[data-index='3'] ::text").extract_first()  # 实时票房
                    ratio = li_list[d].css("div span[data-index='4'] ::text").extract_first()  # 票房占比
                    movie_ratio = li_list[d].css("div span[data-index='5'] ::text").extract_first()  # 排片占比

                    dic["date"] = r.strftime("%Y-%m-%d")
                    dic["total_box"] = float(
                        total_box.replace("亿", "")) * 10000 if "亿" in total_box else total_box.replace("万", "")
                    dic["box"] = float(box.replace("亿", "")) * 10000 if "亿" in box else box.replace("万", "")
                    dic["ratio"] = ratio
                    dic["movie_ratio"] = movie_ratio

                    lz_list.append(dic) if '哪吒' in name else szw_list.append(dic)

        return lz_list, szw_list

    @staticmethod
    def bar_base(l1, l2):
        lh_list = [y["box"] for y in l2]
        lh_list.extend([0 for _ in range(3)])  # 烈火前面三天为0

        bar = Bar(init_opts=opts.InitOpts(page_title="电影票房"))
        bar.add_xaxis([i["date"] for i in reversed(l1)])
        bar.add_yaxis("哪吒之魔童降世", [i["box"] for i in reversed(l1)])
        bar.add_yaxis("烈火英雄", [i for i in reversed(lh_list)])

        bar.set_global_opts(opts.TitleOpts(title="当日票房", subtitle="单位: 万元"))
        bar.render("bar.html")

    @staticmethod
    def line_base(l1, l2) -> Line:

        lh_list = [y["total_box"] for y in l2]
        lh_list.extend([0 for _ in range(3)])  # 前面三天为0

        c = (
            Line(init_opts=opts.InitOpts(bg_color="", page_title="总票房"))
                .add_xaxis([y["date"] for y in reversed(l1)])
                .add_yaxis("哪吒之魔童降世", [y["total_box"] for y in reversed(l1)], is_smooth=True, markpoint_opts=opts.
                           MarkPointOpts(data=[opts.MarkPointItem(type_="max")]))

                .add_yaxis("烈火英雄", reversed(lh_list), is_smooth=True, markpoint_opts=opts.
                           MarkPointOpts(data=[opts.MarkPointItem(type_="max")]))

                .set_global_opts(title_opts=opts.TitleOpts(title="总票房", subtitle_textstyle_opts={"color": "red"},
                                                           subtitle="单位: 万元"), toolbox_opts=opts.ToolboxOpts())
        )
        return c.render("line.html")

    @classmethod
    def ratio_spider(cls):
        cls.session.get("https://piaofang.baidu.com/?sfrom=wise_film_box")

        ratio_list = []
        movie_list = []

        params = {
            "pagelets[]": "index-overall",
            "reqID": "28",
            "sfrom": "wise_film_box",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "attr": "3,4,5,6",
            "t": int(time.time() * 1000),
        }

        response = cls.session.get("https://piaofang.baidu.com/", params=params).text

        result = eval(re.findall("BigPipe.onPageletArrive\((.*?)\)", response)[0])

        selector = Selector(text=result.get("html"))

        li_list = selector.css(".detail-list .list dd")

        for d in range(len(li_list) - 10):
            name = li_list[d].css("h3 b ::text").extract_first()
            ratio = li_list[d].css("div span[data-index='4'] ::text").extract_first().replace("%", "")  # 票房占比
            movie_ratio = li_list[d].css("div span[data-index='5'] ::text").extract_first().replace("%", "")  # 排片占比

            ratio_list.append((name, ratio))
            movie_list.append((name, movie_ratio))

        return ratio_list, movie_list

    @staticmethod
    def pie_base(li):

        for i in range(len(li)):
            radius = ["40%", "75%"] if i == 1 else []
            title = "排片占比" if i == 1 else "票房占比"

            c = (
                Pie()
                    .add("", [z for z in li[i]], center=(500, 280), radius=radius,)
                    .set_global_opts(title_opts=opts.TitleOpts(title="Pie-基本示例"))
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                    .set_global_opts(title_opts=opts.TitleOpts(title=title),
                                     legend_opts=opts.LegendOpts(orient="scroll", pos_left="1%", pos_top="25%"),
                                     )
            )
            c.render(f"{i}.html")


if __name__ == "__main__":
    nz = NeZhaSpider()
    result = nz.spider()
    nz.bar_base(result[0], result[1])
    nz.line_base(result[0], result[1])
    result2 = nz.ratio_spider()
    nz.pie_base(result2)
