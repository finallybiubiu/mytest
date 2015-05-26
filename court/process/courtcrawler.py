# -*- coding:utf-8 -*-

# 直接运行，加入DJANGO_SETTINGS_MODULE配置
import os,sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'court.settings'

# fix for django > 1.6
import django
django_version = django.get_version()
if django_version.startswith('1.7') \
        or django_version.startswith('1.8'):
    django.setup()

import time
import re
import random
import threading
from Queue import Queue

import requests
import redis

# from apps.log import std_logger, file_logger, both_logger

from database.models import *

def redis_conn(host, port, password, db=0):
    r = redis.StrictRedis(host=host, port=port, password=password, db=db)
    return r

class Persistence(threading.Thread):
    """
    data persistence thread
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.flag = True

        self.c = re.compile(r'\?id=(.*)')
        self.redis_conn = redis_conn('192.168.0.197', 6379, 'iamshniu31', db=4)

    def run(self):
        t0 = time.time()
        while self.flag:
            if not self.queue.empty():
                ele = self.queue.get()

                kwargs = {
                    'source': ele.text.encode('utf-8'),
                    'source_id': '' if not self.c.findall(str(ele.url)) else self.c.findall(ele.url)[0],
                    'url': ele.url.encode('utf-8'),
                    'page_type': 'json'
                }
                if insert_source_records(**kwargs) and kwargs.get('source_id', ''):
                    # both_logger.info('save %s successfully!' % kwargs.get('source_id'))
                    self.redis_conn.sadd('court.id.set', str(kwargs.get('source_id')))

                t0 = time.time()

            if time.time() - t0 > 30 * 60:
                self.stop()

    def stop(self):
        print 'i will stop.'
        self.flag = False


class NaturalMixin(object):
    """
    natural person mixin
    """

    def _download(self, session):
        print 'start download...'
        for i in range(int(self.start), int(self.end)):
            try:
                # both_logger.info('start download detail id: %d' % i)

                # 判断
                if self.redis_conn.sismember('court.id.set', str(i)):
                    # both_logger.info('detail id %d is already down.' % i)
                    continue

                r = self._send(session, self.down_url % str(i))

                if r is None or r.status_code == 500:
                    # both_logger.info('detail id of %d is not exists.' % i)
                    self.sleep(random.random() * 0.5)
                    continue

                self.save(r)

                # 间隔随机的时间
                # self.sleep(random.random() * 1)
            except Exception, e:
                print e
                # both_logger.info('Exception happened.Msg is: %s' % e.message)
                change_runtime(self.fetch, str(i), self.end, using=self.using)

        print 'for is over.'
        change_runtime(self.fetch, self.end, self.end, using=self.using)

    def sleep(self, rand):
        time.sleep(rand)

    def _send(self, session, url, times=0):
        """
        如果url访问出现错误，就每隔10秒访问一次，重试3次
        """
        if times > 2:
            return None

        try:
            r = session.get(url)
            return r
        except (Exception, RuntimeError) as err:
            # both_logger.warning('get %s raise error and err is: %s.try again...' % (url, err.message()))
            times = times + 1
            self.sleep(random.random() * 6)
            self._send(session, url, times=times)

    def save(self, response):
        self.queue.put(response)


class Fetch(object):
    homepage = ''
    down_url = ''

    def __init__(self):
        self.start, self.end, self.step = 0, 0, 0
        self.fetch = ''

    def get_session(self, is_ajax=False):
        """
        创建浏览器会话，并设置头信息
        """
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate'
        })
        session.get(self.homepage)

        if is_ajax:
            session.headers.update({'X-Requested-With': 'XMLHttpRequest'})

        return session

    def set_session(self, session, is_close_ajax=False):
        """
        设置会话是否以异步的方式请求
        """
        if is_close_ajax:
            if session.headers.has_key('X-Requested-With'):
                del session.headers['X-Requested-With']
        else:
            session.headers.update({'X-Requested-With': 'XMLHttpRequest'})

        return session

    def download(self):
        main_session = self.get_session(is_ajax=True)

        try:
            self._download(main_session)
            print 'over...'
        except Exception, err:
            print err

    def save(self):
        raise Exception('Not implement save method.')

    def _download(self, session):
        raise Exception('Not implement _download method.')


class NaturalFetch(NaturalMixin, Fetch):
    homepage = 'http://shixin.court.gov.cn/personMore.do'
    down_url = 'http://shixin.court.gov.cn/detail?id=%s'

    using = 'fetch'

    def __init__(self, fetch, queue):
        super(NaturalFetch, self).__init__()
        self.fetch = fetch
        self.start, self.end, self.step = get_runtime(fetch, using=self.using)

        if int(self.end) - int(self.start) < int(self.step):
            self.end = int(self.start) + int(self.step)

        self.queue = queue

        self.redis_conn = redis_conn('192.168.0.197', 6379, 'iamshniu31')

if __name__ == '__main__':
    save_queue = Queue()
    p = Persistence(save_queue)
    p.start()

    nf = NaturalFetch('court', save_queue)
    nf.download()
    # conn = redis_conn('192.168.0.182', 6379, 'iamshniu31', db=1)
    # conn.hset('h1', 'code', '1')
    # conn.hset('h1', 'risk_factor', 90)
    #
    # print conn.hmget('h1', 'code', 'risk_factor')
    # pass