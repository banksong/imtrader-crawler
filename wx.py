import itchat
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
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class wechatUser:

    def __init__(self, msg_user, user_info):
        self.msg_user = msg_user
        self.user_info = user_info
        # self.id = random.randint(1, 100)

    def __key(self):
    	return (self.user_info)

    def __eq__(self, other):

        if not isinstance(other, wechatUser):
            # Don't recognise "other", so let *it* decide if we're equal
            return NotImplemented
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())


def setLog():
    logging.basicConfig(level=logging.DEBUG)
    log_file_handler = TimedRotatingFileHandler(
        filename="crawler", when="D", interval=1, backupCount=3)
    log_file_handler.suffix = "%Y-%m-%d.log"
    log_file_handler.extMatch = re.compile(
        r"^\d{4}-\d{2}-\d{2}.log$")
    log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_fmt)
    log_file_handler.setFormatter(formatter)

    log_with_handler = logging.getLogger()
    log_with_handler.addHandler(log_file_handler)
    return log_with_handler


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

def wallstreet():
    global last_update_time
    starttime = datetime.datetime(1970, 1, 1, 8, 0, 0)
    # 读取新闻内容接口
    response = urllib.request.urlopen(
        'https://api-prod.wallstreetcn.com/apiv1/content/lives?channel=global-channel&limit=0')
    http = response.read()
    hjson = json.loads(http.decode())
    liveNew = hjson['data']['items'][0]
    time = liveNew['display_time']
    content = ''
    if time == last_update_time:
        return ''
    else:
        last_update_time = time
        t = starttime + datetime.timedelta(seconds=int(time))
        content = liveNew['content_text'] + ' '
        content = content + t.strftime('%Y-%m-%d %H:%M')
        return content


def crawler():
    notify_content = wallstreet()
    global log
    global user_list
    if notify_content != '':
    	for user in user_list:
    		user.msg_user.send(u'%s %s' % (notify_content, '[by imTrader]'))
    		log.info('crawler has sent news to user:' + user.user_info)

def schedule_crawler():
    scheduler = BackgroundScheduler()
    global log
    scheduler.add_job(crawler, 'interval', seconds=15)
    scheduler.start()
    try:
        log.info('have start a schedule job')
    except (KeyboardInterrupt, SystemExit):
         # Not strictly necessary if daemonic mode is enabled but should be
         # done if possible
        scheduler.shutdown()
        itchat.logout()

def add_user(msg):
	global user_list
	user_info = itchat.search_friends(userName=msg.fromUserName)
	log.info(user_info['NickName'] + ' start listen broadcast and add user to list.')
	user_list.add(wechatUser(msg.user, user_info['NickName']))
	log.info('user list size is:' + str(len(user_list)))

def remove_user(msg):
	global user_list
	user_info = itchat.search_friends(userName=msg.fromUserName)
	remove_user = wechatUser(msg.user, user_info['NickName'])
	log.info(user_info['NickName'] + ' try stop listen broadcast')
	if remove_user in user_list:
		log.info('remove user to list:'+ user_info['NickName'])
		user_list.remove(remove_user)
	log.info('user list size is:' + str(len(user_list)))


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    global log
    global user_list

    if msg.text == crawler_help:
    	msg.user.send(u'%s\n%s\n%s\n%s' % (u'imTrader v0.1 机器人命令指南:',u'start, 收听华尔街快讯直播',u'stop, 停止收听直播', u'latest, 马上获取最新消息' ))
    elif msg.text == crawler_key:
    	msg.user.send(u'%s, %s' % (u'Hey man', '开始收听华尔街快讯!'))
    	add_user(msg)
       
    elif msg.text == crawler_stop:
        msg.user.send(u'%s: %s' % (u'停止收听直播快讯', '欢迎再会.'))
        remove_user(msg)

    elif msg.text == crawler_latest:
    	notify_content = wall_street_latest()
    	log.info('Send latest news to user')
    	msg.user.send(u'%s %s' % (notify_content, '[by imTrader]'))
    else:
    	return

def lc():
    log.info('wechat login success')

def retry_login():
    log.info('wechat logout itself')

sys.getdefaultencoding()
crawler_key = 'start'
crawler_stop = 'stop'
crawler_help = 'help'
crawler_latest = 'latest'

last_update_time = ''
user_list = set()
log = setLog()

schedule_crawler()
itchat.auto_login(loginCallback=lc, exitCallback=retry_login)
# itchat.auto_login()
itchat.run(True)
# if __name__ == '__main__':
#         # msg = {'Type': 'Text','Text': m['Content'],}
#     schedule_crawler('')
#     try:
#         while True:
#             time.sleep(1)
#         # This is here to simulate application activity (which keeps the
#         # main thread alive).

#     except (KeyboardInterrupt, SystemExit):
#             # Not strictly necessary if daemonic mode is enabled but should be
#             # done if possible
#         sys.exit('good buy')
