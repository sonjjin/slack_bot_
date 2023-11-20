# -*- coding: utf-8 -*- 
from slack_sdk import WebClient
import json
import pdb
import time
import datetime
import re

class SlackAPI:
    """
    Slack api
    """
    def __init__(self, token, channel_id, bot_id):
        self.client = WebClient(token)
        self.channel_id = channel_id
        self.bot_id = bot_id
        

    def get_message_ts(self, query):
        """
        message read
        """
        result = self.client.conversations_history(channel=self.channel_id)
        messages = result.data['messages']
        message = list(filter(lambda m: m["text"]==query, messages))[0]
        message_ts = message["ts"]
        return message_ts

    def post_thread_message(self, message_ts, text):
        """
        post thread message
        """
        result = self.client.chat_postMessage(
            channel=self.channel_id,
            text = text,
            thread_ts = message_ts
        )
        return result

    def post_message(self, text):
        """
        send meesage to channel
        """
        result = self.client.chat_postMessage(
            channel=self.channel_id,
            text=text
        )
        return result
    
    def find_users_(self, condis, update_type, update_date = None):
        """
        특정 메세지 보낸사람 찾기
        'g' : 출근시간
        'l' : 퇴근시간
        't' : 총 근무 시간 
        's' : 현재 상태
        """
        user_list_attand = {}
        # user_list
        # pdb.set_trace()
        # print(update_date)
        if update_date is None:
            if update_type is 't':
                today = datetime.datetime.now() 
                oldest = time.mktime((today - datetime.timedelta(days=1) + datetime.timedelta(minutes=30)).timetuple())
                latest = time.mktime((today).timetuple())
            else:
                today = datetime.datetime.now()
                if today.hour < 5:
                    oldest = time.mktime(datetime.datetime(today.year, today.month, today.day-1, 6).timetuple())
                else:
                    oldest = time.mktime(datetime.datetime(today.year, today.month, today.day, 6).timetuple())
                
                latest = time.mktime((today).timetuple())
        else:
            year, month, day = int(update_date[:4]), int(update_date[4:6]), int(update_date[6:8])
            today = datetime.datetime(year,month,day,5,30) + datetime.timedelta(days=1)
            oldest = time.mktime((today - datetime.timedelta(days=1) + datetime.timedelta(minutes=30)).timetuple())
            latest = time.mktime((today).timetuple())
        # print(datetime.datetime.fromtimestamp(oldest), datetime.datetime.fromtimestamp(latest))
        response = self.client.conversations_history(channel = self.channel_id, oldest = oldest, latest = latest)
        # pdb.set_trace()
        for _, message in enumerate(response['messages']):

            if message['user'] == self.bot_id:
                continue
            for condi in condis:
                find_text = re.search(condi, message['text'])
                if find_text is not None:
                    break
            if find_text is not None:
                try:
                    # last_time = float(user_list_attand[message['user']][-1])
                    last_time = datetime.datetime.fromtimestamp(float(user_list_attand[message['user']][-1]))
                    cur_time = datetime.datetime.fromtimestamp(float(message['ts']))
                    # pdb.set_trace()
                    if abs(last_time - cur_time) > datetime.timedelta(minutes=5):
                        user_list_attand[message['user']].append(message['ts'])
                        # print(message['user'], datetime.datetime.fromtimestamp(float(message['ts'])))
                    

                except:
                    user_list_attand[message['user']] = []
                    user_list_attand[message['user']].append(message['ts'])
                    # print(message['user'], datetime.datetime.fromtimestamp(float(message['ts'])))


        user_cond = {}

        for user_ in user_list_attand:
            user_name = self.client.users_info(user = user_) # user 이름 가지고 오기
            user_cond[user_name['user']['real_name']] = {'times': user_list_attand[user_],
                                                         'user_id': user_}
        return user_cond
    
    def caht_DM(self, user_id, text):
        self.client.chat_postMessage(channel=user_id,
                                     text=text,
                                     blocks = [{"type": "section",
                                                "text": {
                                                    "type": "mrkdwn",
                                                    "text": text}}])
