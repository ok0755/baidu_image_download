#coding=utf-8
from time import sleep
import os
import random
from fake_useragent import UserAgent
from urllib import parse
import requests
import re
import gevent
from gevent import monkey,pool
monkey.patch_socket()

## ---------------------------------- 起止页------------------------------------------------------------------------------------  ##
def start_end(start,end,keywords):
    dic = {'tn':'baiduimage','ie':'utf-8','word':keywords}
    for pages in range(start,end+1):
        dic['pn'] = pages*20
        data = parse.urlencode(dic)
        url='http://image.baidu.com/search/flip?&{}'.format(data)
        yield url
## ---------------------------------------------------------------------------------------------------------------------------
## 图片链接地址
def get_pic_urls(url,num_retries=2):
    r_compile=re.compile('"objURL":"(.*?)"',re.S)
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    try:
        #r=requests.get(url,proxies=random_ip(),headers=header)
        r=requests.get(url,headers=header,timeout=5)
        html=r.text
        r.close()
        ths = re.findall(r_compile,html)
        return ths

    except:
        print(u'页面重试 {} 次 {}'.format(num_retries,url))
        if num_retries > 0:
            sleep(2)
            get_pic_urls(url,num_retries-1)
## ---------------------------------------------------------------------------------------------------------------------------
## 下载图片
def download(pic,num_retry=2):
    header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    try:
        r=requests.get(pic,headers=header,timeout=4)
        content=r.content
        r.close()
        fname = os.path.split(pic)[1]
        fn = re.sub('[\/:*?"<>|]','-',fname)         ## 替换为windows合法文件名
        if '.' in fname:
            with open(fn, "wb+") as jpg:
                jpg.write(content)
        print(pic)
    except:
        if num_retry > 0:
            download(pic,num_retry-1)
        elif num_retry == 0:
            print('下载失败',pic)
## ----------------------代理IP-----------------------------------------------------------------------------------------------------
def random_ip():
    f = open(r'C:\Users\zhoub\Desktop\ip2.txt','r')
    ip = random.choice(f.readlines()).replace('\n','')
    proxies = {"http": "http://"+ip, "https": "http://"+ip}  # 代理ip
    return proxies
# -------------------------------------------------------------------------------------------------------------------------------------------------#
if __name__=='__main__':
    keywords=input(u'关键词,开始页,结束页:')
    words = keywords.split()
    start = int(words[1])
    end = int(words[2])
    objurl=start_end(start,end,words[0])
    p = pool.Pool(50)
    for obj in objurl:
        th = []
        for pics in get_pic_urls(obj):
            th.append(p.spawn(download,pics))
        gevent.joinall(th)