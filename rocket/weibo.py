# coding: utf-8
__author__ = 'Python编程与实战'

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


class WeiboSpider(object):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Cookie": "UM_distinctid=16da58792b541-019aa5dfc678f3-8383268-1fa400-16da58792b68b4; YF-V5-G0=8a1a69dc6ba21f1cd10b039dff0f4381; _s_tentry=s.weibo.com; Apache=3718227610324.4604.1570440190010; SINAGLOBAL=3718227610324.4604.1570440190010; ULV=1570440190792:1:1:1:3718227610324.4604.1570440190010:; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhR0dWnf_kHAxZVMo4LdRTu; SUB=_2AkMqx4s3f8NxqwJRmP0QzGzjb4h0wg7EieKcm3rsJRMxHRl-yT83qhMytRB6AUel2JKbWcKwW8Jb_8RZYSuRFGlEzox4; CNZZDATA1272960323=805110475-1570436228-https%253A%252F%252Fpassport.weibo.com%252F%7C1570436228; Ugrow-G0=d52660735d1ea4ed313e0beb68c05fc5; YF-Page-G0=5161d669e1ac749e79d0f9c1904bc7bf|1570440196|1570440183",
    }

    def get_comment(self, num):
        url = "https://weibo.com/aj/v6/comment/big"
        result_list = []
        print(f"{num} start")
        for page in range(1, 20):
            params = {
                "ajwvr": "6",
                "id": num,
                "from": "singleWeiBo",
                "__rnd": int(time.time() * 1000),
                "page": page
            }
            response = requests.get(url,headers=self.headers,params=params)
            json_data = response.json()
            if json_data["code"] == "100000":
                html = json_data["data"]["html"]
                selector = Selector(text=html)
                ul_list = selector.css(".WB_text")
                for a in ul_list:
                    # 用户id
                    user_id = a.css("a ::attr(usercard)").extract_first("").replace("id=","")
                    # 评论
                    comment = ''.join(a.xpath("./text()").extract()).strip().replace("：","")
                    if comment == "等人" or "回复:" in comment:
                        continue

                    if comment:
                        result_list.append(comment.strip())
                print(f"{num}: 正在爬取第{page}页")

            time.sleep(1)

        return result_list

    def write_csv(self):
        writer = pd.ExcelWriter('result.xls')

        with ThreadPoolExecutor(max_workers=3)as t:
            task1 = t.submit(self.get_comment, "4424313073322909")
            task2 = t.submit(self.get_comment, "4424464139339663")
            task3 = t.submit(self.get_comment, "4424410163141505")

            ren_min_wang = task1.result()
            ri_bao = task2.result()
            basketball = task3.result()

            p1 = pd.DataFrame(data={"ren_min_wang_comment": ren_min_wang}, columns=["ren_min_wang_comment"])
            p2 = pd.DataFrame(data={"ri_bao_comment": ri_bao}, columns=["ri_bao_comment"])
            p3 = pd.DataFrame(data={"basketball_comment": basketball}, columns=["basketball_comment"])

            p1.to_excel(writer,sheet_name="ren_min_wang")
            p2.to_excel(writer,sheet_name="ri_bao")
            p3.to_excel(writer,sheet_name="basketball")

            writer.save()
            writer.close()

    @staticmethod
    def read_csv():
        path = os.getcwd()
        img = Image.open(path + r'\1.jpg')  # 打开图片
        img_array = np.array(img)  # 将图片装换为数组

        for name in ["ren_min_wang", "ri_bao", "basketball"]:
            d = pd.read_excel("result.xls", sheet_name=name, usecols=[1])
            df_copy = d.copy()
            df_copy[name] = df_copy["{}_comment".format(name)].apply(lambda x: x)
            df_list = df_copy.values.tolist()
            comment = jieba.cut(str(df_list),cut_all=False)
            words = ' '.join(comment)
            stop_word = {'xa0'}

            wc = WordCloud(scale=4, width=2000, height=1800,background_color='white', font_path="simfang.ttf",
                           stopwords=stop_word, contour_width=3, mask=img_array)
            wc.generate(words)
            wc.to_file('{}.png'.format(name))


if __name__ == '__main__':
    w = WeiboSpider()
    w.write_csv()
    w.read_csv()
