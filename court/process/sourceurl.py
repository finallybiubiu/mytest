# -*- coding:utf-8


"""
    法院失信自然人更新 + 补充source_url
"""
import re
import os
import sys
import django
from os.path import dirname
reload(sys)
sys.path.append(dirname(dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = "court.settings"
#django.setup()

from database.models import *
import redis
import requests
import time

def redis_conn():
    r = redis.StrictRedis(host='192.168.0.197', port=6379, password ='iamshniu31', db=4)
    return r

def get_html(url):
    times = 0
    wait_time = 30

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate'}

    while times < 5:
        try:
            r2 = requests.get(url, timeout = 20, headers = headers)
            return r2
        except:
            times = times + 1
            time.sleep(wait_time)

def main():

    r = redis_conn()
    # 将已经爬取的soure_id存入内存数据库中
    # with open('e:\\crawler_collect_blacklist_n.txt', 'r') as f:
    #     for line in f:
    #         line = line.split('\n')
    #         print line[0]
    #         r.sadd('s1', line[0])
    # print "------读取结束------"

    for i in range(1481175,1654518):
        detail_id = str(i)
        print i
        if not r.sismember('s1', detail_id):
            source_url = "http://shixin.court.gov.cn/detail?id=%s"%(detail_id)
            r.sadd('s1', str(i))
            r2 = get_html(source_url)

            if r2 is None or r2.status_code == 500:
                time.sleep(5)
                continue
            else:
                kwargs = {
                    'source': r2.text.encode('utf-8'),
                    'source_id': detail_id,
                    'url': source_url.encode('utf-8'),
                    'page_type': 'json'
                }
                insert_source_records(**kwargs)
                print "oh&yes^`~"


if __name__ == '__main__':
    main()




