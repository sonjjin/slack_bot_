# -*- coding: utf-8 -*- 
from slack_api import SlackAPI
import json
import pdb
import datetime
import re
from google_worksheet import attandencesheet
import os
import time

class attandence_check():
    # init
    def __init__(self, info_path, outlier):
        self.slack_token_path = os.path.join(info_path, 'token.json')
        self.name_path = os.path.join(info_path, 'name_tag_2.json')
        self.text_path = os.path.join(info_path, 'text.json')
        with open(self.slack_token_path, 'r') as token_json:
            slack_dict = json.load(token_json)
        with open(self.name_path, 'r') as name_json:
            self.name_tag = json.load(name_json)
        with open(self.text_path, 'r') as text_json:
            self.texts = json.load(text_json) 
        self.token = slack_dict['token']
        self.channel_id = slack_dict['channel_id']
        self.attand = slack_dict['attand']
        self.leave = slack_dict['leave']
        self.sheet_url = slack_dict['google_url']
        self.bot_id = slack_dict['bot_id']
        self.log = slack_dict['log']
        self.admin = slack_dict['admin']
        self.slack = SlackAPI(self.token, self.channel_id, self.bot_id)

        self.outlier = outlier
        self.worksheet_date = self.get_updatesheet()
        self.hour_4 = slack_dict['4hour']
        self.attandence_sheet = attandencesheet(info_path, self.worksheet_date, self.hour_4, self.name_tag, self.sheet_url, self.admin, self.slack, self.texts)
           
        
    # get user information
    def update_total(self, update_date = None):
        print('update total')
        attand_list = self.slack.find_users_(self.attand, 't', update_date) # new -> old
        leave_list = self.slack.find_users_(self.leave, 't', update_date) # new -> old
        for user in attand_list:
            attand_list[user]['times'].sort() # old -> new
        # for user in leave_list:
        #     leave_list[user]['times'].sort() # old -> new
        total_ = {}
        not_leave = {}
        for user in attand_list:
                total_working_ = []
                try:
                    if len(attand_list[user]['times']) == 0:
                        continue
                    if len(attand_list[user]['times']) == len(leave_list[user]['times']):
                        time_length = min(len(attand_list[user]['times']), len(leave_list[user]['times']))
                        for i in range(time_length):
                            attand_ = datetime.datetime.fromtimestamp(float(attand_list[user]['times'][i]))
                            leave_ = datetime.datetime.fromtimestamp(float(leave_list[user]['times'][i]))
                            total_working_.append((leave_ - attand_).total_seconds()/60)
                    else:
                        time_length = min(len(attand_list[user]['times']), len(leave_list[user]['times']))
                        for i in range(time_length):
                            attand_ = datetime.datetime.fromtimestamp(float(attand_list[user]['times'][i]))
                            leave_ = datetime.datetime.fromtimestamp(float(leave_list[user]['times'][i]))
                            total_working_.append((leave_ - attand_).total_seconds()/60) # 분단위
                    total_working = round(sum(total_working_))
                    hour = total_working // 60
                    minute = total_working % 60
                    str_update = str(hour).zfill(2)+':'+str(minute).zfill(2)
                    total_[user] = str_update
                    
                    if user in self.outlier.keys():
                        total_[self.outlier[user]] = total_.pop(user)

                except KeyError:
                    try:
                        today = datetime.datetime.now()
                        log_txt = str(today.year) + '_' + str(today.month) + '_' + str(today.day) + '.txt'
                        save_path = os.path.join(self.log, log_txt)
                        with open(save_path, 'a') as f:
                            f.write(user,'는 아직 퇴근을 못 했습니다 ㅠㅠ \n')
                    except:
                        print(user,'는 아직 퇴근을 못 했습니다 ㅠㅠ \n')
                    
        # print(total_)
        # pdb.set_trace()
        sheet_update = {}
        for i, name in enumerate(self.name_tag.keys()):
            if name in total_.keys():
                sheet_update[name] = total_[name]
            else:
                sheet_update[name] = '-'
            
        self.attandence_sheet.update_cell(sheet_update, 't')
        self.attandence_sheet.update_cell(sheet_update, 'h')
        
    def update_leave_or_work(self, update_type, update_date = None):
        '''
        g: go to work
        l: leave work
        '''
        if update_type == 'g':
            print('update go to work')
            update = self.attand
        elif update_type == 'l':
            print('update leave the work')
            update = self.leave
        time_list = self.slack.find_users_(update, update_type, update_date) # new -> old
        if update_type == 'l':
            check_list = self.slack.find_users_(self.attand, update_type, update_date)
        user_ = {}
        
        for user in time_list:
            try:
                if update_type == 'g':
                    time_list[user]['times'].sort()
                if update_type == 'l':
                    len(check_list[user]['times'])
                update_time = datetime.datetime.fromtimestamp(float(time_list[user]['times'][0]))
                hour = update_time.hour
                minute = update_time.minute
                str_update = str(hour).zfill(2)+':'+str(minute).zfill(2)
                user_[user] = (str_update)
                if user in self.outlier.keys():
                    user_[self.outlier[user]] = user_.pop(user)
            except:
                continue
        sheet_update = {}
        for i, name in enumerate(self.name_tag.keys()):
            if name in user_.keys():
                sheet_update[name] = user_[name]
            else:
                sheet_update[name] = '-'
        update_info = self.attandence_sheet.update_cell(sheet_update, update_type, update_date)
        if update_info:
            print('done')
        else:
            time.sleep(20)
        return sheet_update
     
    def update_state(self, attand, leave):
        print('update state')
        sheet_update = {}
        for user in attand:
            if attand[user] == '-':
                sheet_update[user] = '○'
            elif attand[user] != '-' and leave[user] == '-':
                sheet_update[user] = '●'
            elif attand[user] != '-' and leave[user] != '-':
                sheet_update[user] = '○'
        self.attandence_sheet.update_cell(sheet_update, 's')
        
           
    def reminder(self):
        time_attand_list = self.slack.find_users_(self.attand, 'g') # new -> old
        time_leave_list = self.slack.find_users_(self.leave, 'l') # new -> old
        not_leave_list = {}
        for user in time_attand_list:
            if user not in time_leave_list.keys():
                not_leave_list[user] = time_attand_list[user]['user_id']
            elif len(time_attand_list[user]['times']) > len(time_leave_list[user]['times']):
                not_leave_list[user] = time_attand_list[user]['user_id']
        # print(not_leave_list)
        for user in not_leave_list:
            self.slack.caht_DM(not_leave_list[user], self.texts['leave'])
            
    
    def get_updatesheet(self):
        today_ = datetime.date.today()
        y = str(today_.year)
        m = str(today_.month).zfill(2)
        out = y[-2:]+'.'+m
        return out