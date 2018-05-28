import time
import logging
import json
import urllib.request
import datetime
import os
import sys
import random
import re
from itchat.content import *
from apscheduler.schedulers.background import BackgroundScheduler
from logging.handlers import TimedRotatingFileHandler
import sys

def wall_street_latest():
    starttime = datetime.datetime(1970, 1, 1, 8, 0, 0)
    # 读取新闻内容接口
    response = urllib.request.urlopen(
        'https://api-prod.wallstreetcn.com/apiv1/content/lives?channel=global-channel&limit=0')
    http = response.read()
    hjson = json.loads(http.decode())
    liveNew = hjson['data']['items'][0]
    time = liveNew['display_time']
    content = ''
    t = starttime + datetime.timedelta(seconds=int(time))
    content = liveNew['content_text'] + ' '
    content = content + t.strftime('%Y-%m-%d %H:%M')
    return content


print(wall_street_latest())