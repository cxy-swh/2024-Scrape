# 网站地址  https://spa6.scrape.center/
import json
import os
import time
import requests
from pathlib import Path
import execjs
import re
from openpyxl import Workbook
from tqdm import tqdm
# 获取当前工作目录
job_path = Path.cwd()
# 获取动态token
token = execjs.compile(Path('token.js').read_text()).eval('token')
# 请求
Page = 0
wb = Workbook()
ws = wb.active
# 表头
dh = ['uid', '名字', '类型', '发布日期', '时长', '得分', '地区', '图片']
ws.append(dh)
while True:
    response = requests.get(
        url='https://spa6.scrape.center/api/movie/?limit=10&offset=%d&token=%s' % (Page,token),
    ).json()
    print('当前:',Page)
    response = json.dumps(response['results'],ensure_ascii=False).replace("'"," ").replace(" ","").replace("null",'"null"')
    # print(response)
    if response.count('null') >= 12:
        print("获取完毕--------------------------------------------------------")
        break
    Page += 10
    # "id":(.*?),.*?:"(.*?)".*?:"(.*?)".*?:"(.*?)".*?:(.*?]),.*?:"(.*?)".*?:(.*?),.*?:(.*?),.*?:(.*?])
    re_guiz = re.compile('"id":(?P<uid>.*?),.*?:"(?P<name>.*?)".*?:"(?P<name2>.*?)".*?:"(?P<img_url>.*?)".*?:(?P<categories>.*?]),.*?:"(?P<published_at>.*?)".*?:(?P<minute>.*?),.*?:(?P<score>.*?),.*?:(?P<regions>.*?])')
    daee = re_guiz.finditer(response)
    for idx,a in enumerate(daee,start=Page-8):
        if not a:
            print("===========================NONONONONONONONONONONO===========================")
        uid = a.group('uid')
        name = a.group('name') + ' ' + a.group('name2')
        img_url = a.group('img_url')
        categories1 = a.group('categories')
        categories = categories1.replace(" ","").strip("[]").replace('"',"")
        published_at = a.group('published_at')
        minute = a.group('minute')
        h = int(minute) // 60
        if h < 10: h = '0' + str(h)
        min = int(minute) % 60
        if min < 10: min = '0' + str(min)
        s = int(minute) * 60 % 60
        if s < 10: s = '0' + str(s)
        minute = f'{h}:{min}:{s}'
        score = a.group('score')
        regions1 = a.group('regions')
        regions = regions1.replace(" ","").strip("[]").replace('"',"")
        fle = f'{job_path}\\images'
        Path(fle).mkdir(exist_ok=True)
        # 去除文件名字特殊字符 防止保存失败
        name = name.replace("\\", " ").replace("/"," ").replace(":"," ").replace("*"," ").replace("?"," ").replace('"'," ").replace("<"," ").replace(">"," ")
        with open(f'{job_path}\\images\\{name}.png','wb')as f:
            rqimg = requests.get(url=img_url).content
            f.write(rqimg)
        ws.append([uid,name,categories,published_at,minute,score,regions,img_url])
        print(name,img_url)
        cell = ws.cell(row=idx,column=8)
        cell.value = '点击查看'
        cell.hyperlink = f'{fle}\\{name}.png'
        time.sleep(0.4)
    wb.save('dataset.xlsx')