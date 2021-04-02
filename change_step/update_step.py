import requests
from datetime import datetime
import random
import time
import sys


def get_hour():
    return datetime.now().hour


def zhi_fu_bao_step(username: str, password: str, step: str):
    """

    :param username:
    :param password:
    :param step:
    :return:
    """
    url = "https://service-hg5j94iz-1254563013.sh.apigw.tencentcs.com/release/change_step_test"
    params = {
        "user": username,
        "password": password,
        "step": step
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Host": "service-hg5j94iz-1254563013.sh.apigw.tencentcs.com",
        "Pragma": "no-cache",
        "Referer": "https://shua.iifxs.xyz/",
    }
    for _ in range(5):
        response = requests.get(url, headers=headers, params=params)
        text_data = response.text
        if "success" in text_data:
            return 1
        else:
            time.sleep(10)
            continue
    return None


def main(username: str, password: str, step, a, b):
    """

    :param username:
    :param password:
    :param step:
    :param a:
    :param b:
    :return:
    """
    try:
        step = int(step)
        a = int(a)
        b = int(b)
    except ValueError:
        print(f"哦豁！请输入正确数字噢...")
        return None

    if a < b <= 10000:
        while True:
            hour = get_hour()
            if 8 <= hour <= 22:
                random_step = random.randint(a, b)
                print(f"当前时间是{datetime.now()}，增加步数 {random_step}")
                step += random_step
                if step >= 98800:
                    print("您的步数已达到上限，不要太贪心噢~~")
                    break

                result = zhi_fu_bao_step(username, password, str(step))
                if result == 1:
                    print(f"当前时间是{datetime.now()}，总步数为 {step}")
                time.sleep(300)

            else:
                print(f"当前时间是{datetime.now()}, 停止刷步")
                break
    else:
        print(f"您设置的变量为每 5 分钟最低增加步数{a}, 最高步数{b}, 但是最高不能超过 10000 噢!")
        return None


def complete_step(username: str, password: str, step: str):
    if int(step) >= 98800:
        step = '98800'

    res = zhi_fu_bao_step(username, password, step)
    if res == 1:
        return "刷步成功"
    else:
        return "失败了，请稍后再试"


if __name__ == '__main__':

    choice = input("请输入您版本\n"
                   "1：为一步到位\n"
                   "2：每隔 5 分钟刷步\n"
                   "请选择：")

    if choice == "1":
        name = input("请输入您的小米运动账号: ")
        pwd = input("请输入您的小米运动密码：")
        current_step = input("您想刷到多少步：")
        resp = complete_step(name, pwd, current_step)
        print(resp)
        time.sleep(5)

    elif choice == "2":
        current_step = input("请输入您要刷新的APP平台当前步数：")
        min_step = input("请输入每 5 分钟需要增加步数的最小值: ")
        max_step = input("请输入每 5 分钟的步数上限值，参考值10000：")
        name = input("请输入您的小米运动账号: ")
        pwd = input("请输入您的小米运动密码：")
        main(name, pwd, current_step, min_step, max_step)

    else:
        print("请输入 1 或者 2")
        sys.exit(1)
