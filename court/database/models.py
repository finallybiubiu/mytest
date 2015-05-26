#-*- coding:utf-8 -*-
from django.db import models


# class FetchRuntime(models.Model):
#     """
#     爬虫的运行时状态
#     """
#     name = models.CharField(u'名称', max_length=20, help_text=u'具有唯一性')
#     start = models.CharField(u'起始', max_length=64, null=True)
#     end = models.CharField(u'结束', max_length=64, null=True)
#     step = models.IntegerField(u'步长', null=True, default=500)
#
#     class Meta:
#         db_table = 'dcf_fetch_runtime'
#         verbose_name_plural = '爬虫运行时状态记录'
#         verbose_name = '爬虫运行时状态记录'


class FetchSourceRecords(models.Model):
    """
    Fetch的源码
    """
    source_id = models.CharField(u'唯一标识', max_length=64, null=True)
    source = models.TextField(u'源码', null=True)
    url = models.CharField(u'访问的url', max_length=255, null=True)
    url_md5 = models.CharField(u'url的md5加密值', max_length=40, null=True)
    page_type = models.CharField(u'源码类型', max_length=10, null=True, help_text="可选的值有：html/json")
    created_on = models.DateTimeField(u'创建时间', auto_now_add=True)
    flag = models.IntegerField(u'标志位', default = 1)

    class Meta:
        db_table = 'dcf_fetch_source_records'
        verbose_name_plural = '源码'
        verbose_name = '源码'

class CourtExecutor(models.Model):
    """
    法院信息
    """
    created_on = models.DateTimeField(u'创建时间', auto_now_add=True)
    name = models.CharField(u'被执行者名字', max_length=64, null=True)
    id_card = models.CharField(u'组织机构代码或身份证号码', max_length=25, null=True)
    court = models.CharField(u'执行法院', max_length=128, null=True)
    province = models.CharField(u'省份', max_length=20, null=True)
    perform_document_num = models.CharField(u'执行依据文号', max_length=128, null=True)
    file_time = models.DateField(u'立案时间', null=True)
    reference = models.CharField(u'案号', max_length=64, null=True)
    executor_unit = models.CharField(u'做出依据单位', max_length=128, null=True)
    obligation = models.TextField(u'法律文书确定的义务', null=True)
    execution_behavior = models.CharField(u'被执行人具体行为表现', max_length=255, null=True)
    execute_status = models.CharField(u'履行情况', null=True, max_length=20)
    publish_time = models.DateField(u'发布时间', null=True)
    follows_num = models.IntegerField(u'关注次数', null=True, default=0)
    source_url = models.CharField(u'信息来源', max_length=1024, null=True, blank=True)
    source_url_mapping = models.CharField(u'映射url', max_length=255, null=True, blank=True)
    detail_id = models.CharField(max_length = 20, null = True)
    class Meta:
        abstract = True  #抽象基类


class CourtExecutorNatural(CourtExecutor):
    """
    法院执行人信息
    """
    sex = models.CharField(u'性别', max_length=4, null=True)
    age = models.IntegerField(u'年龄', null=True)

    class Meta:
        db_table = 'dcf_court_natural'


import hashlib
def md5(content):
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()

# def get_runtime(fetch, using='default'):
#     """
#     获取运行时状态
#     """
#     try:
#         frt = FetchRuntime.objects.using(using).get(name=fetch)
#         return frt.start, frt.end, frt.step
#     except FetchRuntime.DoesNotExist:
#         raise Exception('%s runtime configure dose not exist.' % fetch)
#
#
# #@transaction.atomic(using='fetch')
# def change_runtime(fetch, start, end, using='default'):
#     """
#     改变运行状态
#     """
#     try:
#         frt = FetchRuntime.objects.using(using).get(name=fetch)
#         frt.start = start
#         frt.end = end
#         frt.save()
#     except FetchRuntime.DoesNotExist:
#         raise Exception('%s runtime configure dose not exist.' % fetch)


def insert_source_records(**kwargs):
    fsr = FetchSourceRecords()
    fsr.source_id = kwargs.get('source_id', '')
    fsr.source = kwargs.get('source', '')
    fsr.page_type = kwargs.get('page_type', 'html')
    fsr.url = kwargs.get('url', '')
    fsr.flag = 0
    fsr.url_md5 = md5(fsr.url)

    fsr.save()






