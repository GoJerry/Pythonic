# coding: utf-8
__author__ = 'Jerry'
"公众号：Python编程与实战,欢迎关注"

import requests
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Timeline
from collections import defaultdict

from 胡润排行榜.enum_type import EnumType
from 胡润排行榜.model import save_db, que, Process, db_session


class HuRun:
    url_map = {
        '2015': '5',
        '2016': '1',
        '2017': '11',
        '2018': '15',
        '2019': '19',
        '2020': '22',
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }
    payload = {'search': '', 'order': 'asc'}
    industry = {
        1: "互联网",
        2: "房地产",
        3: "制造业",
        4: "饮料，食品",
        5: '基建',
        6: '金融，投资',
        7: '医疗',
        8: '教育',
        9: '电商',
    }

    industry_map = {
        "阿里巴巴、蚂蚁金服": 9,
        "万达": 2,
        "娃哈哈": 4,
        "腾讯": 1,
        "小米": 1,
        "苏太华系": 5,
        '百度': 1,
        '泛海': 6,
        '苏宁云商': 9,
        '万向': 3,
        '华彬': 6,
        '汉能': 3,
        '美的': 3,
        '恒大': 2,
        '正威': 3,
        '网易': 1,
        '复星': 7,
        '蓝思科技': 3,
        '富华': 2,
        '魏桥创业': 3,
        '阿里系': 9,
        '养生堂': 7,
        '顺丰': 3,
        '碧桂园': 2,
        '拼多多': 9,
        '牧原': 4,
        '海天味业': 4,
        '海底捞': 4,
        '美团': 1,
        '新希望': 6,
        '太平洋建设': 5,
        '恒力': 2,
        '智飞生物': 7,
        '翰森': 7,
        '京东': 9,
        '中公教育': 8,
    }

    def spider(self):
        """
        爬虫，保存数据库
        :return:
        """
        for year, value in self.url_map.items():
            url = f"http://www.hurun.net/CN/HuList/ListJson/{value}"
            response = requests.post(url, json=self.payload, headers=self.headers)
            json_data = response.json()
            for data in json_data[:500]:
                if que(data.get("NameCn"), year):
                    continue

                d = {
                    EnumType.NAME_ID: data.get("ID"),
                    EnumType.NAME: data.get("NameCn"),
                    EnumType.RANKING: data.get("Ranking"),
                    EnumType.WEALTH: data.get("Wealth"),
                    EnumType.BIRTHDAY: data.get('Birthday'),
                    EnumType.NAME_CN: data.get("CNameCn"),
                    EnumType.INDUSTRY: data.get("IndustryCn"),
                    EnumType.YEAR: year,
                }
                save_db(d)

    def pie(self):
        """
        2020年胡润排行榜前20名
        :return:
        """

        data_list = self.pie_search()
        result = defaultdict(int)

        for obj in data_list:
            obj_dict = obj.to_dict()
            result[obj_dict.get(EnumType.NAME)] = obj_dict.get(EnumType.WEALTH)

        pie = (
            Pie(init_opts=opts.InitOpts(width="1200px", height="600px"))
                .add(
                "",
                [(k, v) for k, v in dict(result).items()],
                center=["50%", "50%"],
                rosetype="radius",
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="财富占比", subtitle="胡润排行榜前20"),
                legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
                .render("pie_scroll.html")
        )

    @staticmethod
    def pie_search():
        session = db_session()
        company_list = session.query(Process).filter(Process.ranking <= 20, Process.year == 2020).all()
        session.close()
        return company_list

    def percent(self):
        """
        近五年四大富豪财富占比
        :return:
        """
        attr = ["马云家族", "马化腾", '王健林家族', '许家印']
        tl = Timeline()
        for i in range(2015, 2020):
            pie = (
                Pie()
                    .add(
                    "胡润排行榜",
                    [(name, self.percent_search(name, i)[0].to_dict().get(EnumType.WEALTH)) for name in attr],
                    rosetype="radius",
                    radius=["30%", "55%"],
                )
                    .set_global_opts(title_opts=opts.TitleOpts("{}年四大富豪财富占比".format(i)))
            )
            tl.add(pie, "{}年".format(i))

        tl.render("timeline_pie.html")

    @staticmethod
    def percent_search(name, year):
        session = db_session()
        company_list = session.query(Process).filter(Process.name == name, Process.year == year).all()
        session.close()
        return company_list

    def bar(self):
        """
        近五年首富财富变化
        柱形图
        :return:
        """
        year_data = [2015, 2016, 2017, 2018, 2019, 2020]
        c = (
            Bar()
                .add_xaxis(year_data)
                .add_yaxis("马云", [wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('马云家族')])
                .add_yaxis("马化腾", [wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('马化腾')],
                           is_selected=False)
                .add_yaxis("王健林", [wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('王健林家族')],
                           is_selected=False)
                .add_yaxis("许家印", [wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('许家印')])
                .set_global_opts(title_opts=opts.TitleOpts(title="近五年首富", subtitle="胡润排行榜"),
                                 yaxis_opts=opts.AxisOpts(name='财富(亿)'))
                .render("bar_is_selected.html")
        )

    def line(self):
        """
        折线图
        :return:
        """

        x_data = ["2015", "2016", "2017", "2018", "2019", "2020"]
        (
            Line()
                .add_xaxis(xaxis_data=x_data)
                .add_yaxis(
                series_name="马云",
                y_axis=[int(wealth.to_dict().get(EnumType.WEALTH)) for wealth in self.bar_search('马云家族')],
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                is_smooth=True
            )
                .add_yaxis(
                series_name="马化腾",
                y_axis=[wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('马化腾')],
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                is_smooth=True
            )
                .add_yaxis(
                series_name="王健林",
                y_axis=[wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('王健林家族')],
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                is_smooth=True
            )
                .add_yaxis(
                series_name="许家印",
                y_axis=[wealth.to_dict().get(EnumType.WEALTH) for wealth in self.bar_search('许家印')],
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
                is_smooth=True
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="近五年首富财富变化"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                .render("stacked_line_chart.html")
        )

    @staticmethod
    def bar_search(name):
        session = db_session()
        company_list = session.query(Process).filter(Process.name == name).all()
        session.close()
        return company_list

    def industry_percent(self):
        """
        近五年排行榜前20行业财富占比
        :return:
        """
        tl = Timeline()
        res = defaultdict(int)
        for i in [2015, 2020]:
            for result in self.industry_search(i):
                result = result.to_dict()
                name = result.get(EnumType.NAME_CN)
                res[self.industry[self.industry_map.get(name)]] += int(result.get(EnumType.WEALTH))

            pie = (
                Pie()
                    .add(
                    "胡润排行榜",
                    list(zip(res.keys(), res.values())),
                    rosetype="radius",
                    radius=["30%", "55%"],
                    center="center"
                )
                    .set_global_opts(title_opts=opts.TitleOpts("{}年行业财富".format(i)))
            )
            tl.add(pie, "{}年".format(i))

            tl.render("industry_pie.html")

    @staticmethod
    def industry_search(year):
        session = db_session()
        company_list = session.query(Process).filter(Process.ranking <= 20, Process.year == year).all()
        session.close()
        return company_list


def main():
    h = HuRun()
    h.pie()  # 2020年胡润排行榜前20名
    h.bar()  # 近五年各首富财富变化
    h.line()  # 近五年各首富财富变化 折线图
    h.percent()  # 近五年四大富豪财富占比
    h.industry_percent()  # 近五年行业财富分布变化


if __name__ == '__main__':
    main()
