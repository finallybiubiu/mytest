# -*- coding:utf-8 -*-
"""
    法院失信自然人解析程序
"""

# -*- coding:utf-8 -*-
import os
import sys

from os.path import dirname
reload(sys)
sys.path.append(dirname(dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = "court.settings"
import threading
import django
django.setup()

from database.models import *

#源码信息解析
class DatAParser(threading.Thread):
    def __init__(self, startNum, endNum):
        threading.Thread.__init__(self)
        self.s = startNum
        self.e = endNum

    def run(self):
        lines = CourtExecutorNatural.objects.using().filter(flag=0)[self.s,self.e]
        for line in lines.iterator():
            info = line.source     #取表中的rec_str字段
            print line.id
            b = info.encode('utf-8')
            line.flag = 1     #把已经解析过的记录的标志改为1
            line.save()       #保存到数据库中


#存储自然人信息
class DataTransfer1(threading.Thread):
    def __init__(self, startNum, endNum):
        """
        :param startNum: 开始数
        :param endNum: 结束数
        :return:数据保存到自然人信息表中
        """

        threading.Thread.__init__(self)
        self.startNum = startNum
        self.endNum = endNum

    def run(self):
        lines = FetchSourceOld2.objects.filter(flag=0)[self.startNum:self.endNum] #检索flag=0的记录
        #lines = FetchSourceOld2.objects.all()[self.startNum:self.endNum] #SELECT * FORM crawler_collect_blacklist_fix
        for line in lines.iterator():
            #print line
            info = line.rec_str     #取表中的rec_str字段

            line.flag = 1     #把已经解析过的记录的标志改为1
            line.save()       #保存到数据库中
            b = info.encode('utf-8')
            naturalInfoSave(b)





#将失信执行人和网爬黑名单信息指定的一些字段存放到表dcb_bad_behaviour中
class BadPeopleList(threading.Thread):
    def __init__(self, startNum, endNum):
        threading.Thread.__init__(self)
        self.startNum = startNum
        self.endNum = endNum

    def run(self):
        lines = CourtExecutorNatural.objects.filter(flag=0)[self.startNum:self.endNum]
        for line in lines.iterator():
            info = getinfo1(line)
            NaturalInfoSave(info)
            line.flag=1
            line.save()


class BlackList(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        lines = DcblackListInfo.objects.filter(flag=0)
        for line in lines.iterator():
            info = getinfo2(line)
            print line.id
            BlackInfoSave(info)
            line.flag = 1
            line.save()


def getinfo1(line):
    info = {'name':'', 'id_card':'', 'happen_time':'', 'record_id':''}

    info['name'] = line.name
    info['id_card'] = line.id_card
    info['happen_time'] = line.publish_time
    info['record_id'] = line.id

    return info


def getinfo2(line):
    info = {'name':'', 'id_card':'', 'mobile':'', 'qq':'', 'email':'',
            'happen_time':'', 'record_id':''}

    info['name'] = line.name
    info['id_card'] = line.id_card
    info['mobile'] = line.mobile
    info['qq'] = line.qq
    info['email'] = line.email
    info['record_id'] = line.id
    info['happen_time'] = line.created_on

    return info


def main():
    """
    lines = FetchSourceOld2.objects.filter(flag=0)[0:1]
    #lines = FetchSourceOld2.objects.all()[0:1]#SELECT * FORM crawler_collect_blacklist_fix
    print "hello"
    for line in lines:
        print line.flag
        print type(line.flag)
        line.flag = 1
        line.save()
        info = line.rec_str#取出表中的rec_str字段
        print info
        print type(info)
        b = info.encode('utf-8')
        print type(b)
        naturalInfoSave(b)
        print line.flag

    """

    print "线程开始工作........"

    #四个存放自然人信息的线程（总共914,198条记录）
    '''
    p0 = DataTransfer1(0, 50)
    p0.start()


    p1 = DataTransfer1(50, 50000)
    p1.start()

    p2 = DataTransfer1(50000, 100000)
    p2.start()

    p3 = DataTransfer1(100000, 150000)
    p3.start()


    p4 = DataTransfer1(151551, 914198)
    p4.start()
    '''



    #四个存放法人信息的线程（总共106，581条记录）


    L1 = DataTransfer2(0, 50)
    L1.start()

    L2 = DataTransfer2(50000, 106581)
    L2.start()

    L3 = DataTransfer2(500, 50000)
    L3.start()

    L4 = DataTransfer2(50, 500)
    L4.start()


def boot():
    print '线程开始工作.....'
    # p1 = BadPeopleList(0, 50000)
    # p1.start()
    #
    # p1 = BadPeopleList(50000, 100000)
    # p1.start()
    #
    # p1 = BadPeopleList(100000, 150000)
    # p1.start()
    #
    # p1 = BadPeopleList(150000, 881717)
    # p1.start()

    p2 = BlackList()
    p2.start()


def parse():
    print "线程开始工作........"

    #四个存放自然人信息的线程（总共914,198条记录）

    p0 = DatAParser(0, 50)
    p0.start()

    p1 = DatAParser(50, 50000)
    p1.start()

    p2 = DatAParser(50000, 100000)
    p2.start()

    p3 = DatAParser(100000, 150000)
    p3.start()

    p4 = DatAParser(151551, 265416)
    p4.start()

if __name__ == '__main__':
    # main()
    # boot()
    parse()













