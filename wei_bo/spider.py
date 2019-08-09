# coding: utf-8
__author__ = 'Jerry'
"公众号：Python编程与实战,欢迎关注点赞"

import requests
from scrapy import Selector
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import jieba
from wordcloud import WordCloud
from PIL import Image
import os
import numpy as np

from wei_bo.base import WeiBo


class Spider(object):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Cookie": "",
    }

    def get_comment(self, num):
        url = "https://weibo.com/aj/v6/comment/big"
        result_list = []
        print(f"{num} start")
        for page in range(1, WeiBo.pages.value):
            params = {
                "ajwvr": "6",
                "id": num,
                "from": "singleWeiBo",
                "__rnd": int(time.time() * 1000),
                "page": page

            }
            response = requests.get(url, headers=self.headers, params=params)
            json_data = response.json()
            if json_data["code"] == "100000":
                html = json_data["data"]["html"]
                selector = Selector(text=html)
                ul_list = selector.css(".WB_text")
                for a in ul_list:
                    # 用户id
                    user_id = a.css("a ::attr(usercard)").extract_first("").replace("id=", "")
                    # 评论
                    comment = ''.join(a.xpath("./text()").extract()).strip().replace("：", "")
                    if comment == "等人" or "回复:" in comment:
                        continue

                    if comment:
                        result_list.append(comment.strip())
                print(f"{num}: 正在爬取第{page}页")

            time.sleep(2)

        return result_list

    def write_csv(self):
        writer = pd.ExcelWriter('result.xls')

        with ThreadPoolExecutor(max_workers=3)as t:
            task1 = t.submit(self.get_comment, WeiBo.ma_yi_li.value)
            task2 = t.submit(self.get_comment, WeiBo.wen_zhang.value)
            task3 = t.submit(self.get_comment, WeiBo.yao_di.value)

            ma_yi_li = task1.result()
            wen_zhang = task2.result()
            yao_di = task3.result()

            p1 = pd.DataFrame(data={"ma_yi_li_dict": ma_yi_li}, columns=["ma_yi_li_dict"])
            p2 = pd.DataFrame(data={"wen_zhang_dict": wen_zhang}, columns=["wen_zhang_dict"])
            p3 = pd.DataFrame(data={"yao_di_dict": yao_di}, columns=["yao_di_dict"])

            p1.to_excel(writer, sheet_name="ma_yi_li")
            p3.to_excel(writer, sheet_name="yao_di")
            p2.to_excel(writer, sheet_name="wen_zhang")

            writer.save()
            writer.close()

    @staticmethod
    def read_csv():
        path = os.getcwd()
        img = Image.open(path + r'\1.jpg')  # 打开图片
        img_array = np.array(img)  # 将图片装换为数组

        for name in ["ma_yi_li", "yao_di", "wen_zhang"]:
            d = pd.read_excel("result.xls", sheet_name=name, usecols=[1])
            df_copy = d.copy()
            df_copy[name] = df_copy['{}_dict'.format(name)].apply(lambda x: x)
            df_list = df_copy.values.tolist()
            comment = jieba.cut(str(df_list), cut_all=False)
            words = ' '.join(comment)
            stop_word = {'xa0'}

            wc = WordCloud(scale=4, width=2000, height=1800, background_color='white', font_path="simfang.ttf",
                           stopwords=stop_word, contour_width=3, mask=img_array)
            wc.generate(words)
            wc.to_file('{}.png'.format(name))

def test():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Cookie": "UM_distinctid=16c26d1c88f613-0e29065675a44b-3f385c06-1fa400-16c26d1c890af9; SUB=_2AkMqZYWBf8NxqwJRmP0WyGjgbol0yQHEieKcOXRaJRMxHRl-yT83qnUmtRB6AeWrbow0rqpPVMF-mUNbQE8i1EsJ7x_4; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhOU_g2kwGf44CamO.lYHnE; SINAGLOBAL=6979551182803.141.1564019394030; login_sid_t=2783cc69b5d8dd448c01e949cadde58a; cross_origin_proto=SSL; Ugrow-G0=9ec894e3c5cc0435786b4ee8ec8a55cc; YF-V5-G0=f5a079faba115a1547149ae0d48383dc; WBStorage=edfd723f2928ec64|undefined; CNZZDATA1272960323=748731859-1554977182-https%253A%252F%252Fwww.jianshu.com%252F%7C1564541649; _s_tentry=www.baidu.com; UOR=tech.ifeng.com,widget.weibo.com,www.baidu.com; wb_view_log=1920*10802.5; Apache=7122639924634.817.1564543105512; ULV=1564543105519:2:2:1:7122639924634.817.1564543105512:1564019394050; YF-Page-G0=536a03a0e34e2b3b4ccd2da6946dab22|1564543183|1564543115",
    }

    url = "https://weibo.com/aj/v6/comment/big"
    params = {
        "ajwvr": "6",
        "id": "4399042089738682",
        "from": "singleWeiBo",
        "__rnd": int(time.time() * 1000),
        "page": "2"

    }
    response = requests.get(url, headers=headers, params=params)
    json_data = response.json()
    print(json_data)


if __name__ == "__main__":
    s = Spider()
    s.read_csv()
