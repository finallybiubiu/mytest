# -*- coding:utf-8 -*-

"""
    得到detail_id
"""
import re

import os
import sys
import django
from os.path import dirname
reload(sys)
sys.path.append(dirname(dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = "court.settings"
django.setup()

from database.models import *
def get_detail_id(source_url):

    detail_id = re.findall(r'http://shixin.court.gov.cn/detail\?id=([0-9]\d+)', source_url)
    return detail_id


#update dcf_court_natural
#set detail_id = SUBSTRING(source_url,38)

def main():
    list = CourtExecutorNatural.objects.filter()[1:2]

    for item in list:
        source_url = item.source_url
        if source_url is not None:
            detail_id = get_detail_id(source_url)
            item.detail_id = detail_id[0]
            item.save()
        else:
            item.detial_id = None
            item.save()

if __name__ == '__main__':
    main()




