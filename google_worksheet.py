# -*- coding: utf-8 -*- 
import gspread
import pdb
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os
import traceback
from tqdm import tqdm

class attandencesheet():
    def __init__(self, info_path, worksheet_date, hour_4, name_tag, sheet_url, admin, slack_api, texts):
        scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
        ]
        json_file_name = os.path.join(info_path, 'attandence-check-1ff0331dc10b.json')
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
        gc = gspread.authorize(credentials)
        spreadsheet_url = sheet_url
        # 스프레스시트 문서 가져오기 
        # self.doc = gc.open_by_url(spreadsheet_url)
        self.slack = slack_api
        self.texts = texts
        self.admin = admin
        doc = gc.open_by_url(spreadsheet_url)

        # 시트 선택하기
        self.worksheet = doc.worksheet(worksheet_date)
        self.hoursheet = doc.worksheet(hour_4)
        
        self.name_tag = name_tag
        # 시트 선택하기
        
        
    # def get_worksheet(self):
    #     worksheet = self.doc(self.worksheet_date)
    #     return worksheet
            
    
    def update_cell(self, data, category = 't', update_date = None):
        """
        data: 업데이트 할 data
        category:
        'g' : 출근시간
        'l' : 퇴근시간
        't' : 총 근무 시간 
        's' : 현재 상태
        'h' : 4시간 이상 채움?
        """
        try:
            if category == 'h':
                # print('update_cell_h')
                
                row = self.get_row(update_date)
                for name in data:
                    save_cell = self.name_tag[name]+row
                    time = data[name]
                    length = len(time)
                    if time == '-':
                        hh = 0
                        mm = 0
                    if length == 4:
                        hh = int(time[0])
                        mm = int(time[-2:])
                        # print(time[-2:])
                    if length == 5:
                        hh = int(time[:2])
                        mm = int(time[-2:])
                        # print(time[-2:])
                    temp = datetime.time(hh, mm)
                    # pdb.set_trace()
                    if temp >= datetime.time(4):
                        ud = 1
                    else:
                        ud = 0
                    self.hoursheet.update_acell(save_cell, ud)
            elif category == 's':
                # print('update_cell_s')
                
                for name in tqdm(data):
                    save_cell = self.name_tag[name]+'2'
                    self.worksheet.update_acell(save_cell, data[name])
            else:
                # print('update_else')
                
                today_ = self.get_today(category, update_date)
                for name in tqdm(data):
                    # pdb.set_trace()
                    save_cell = self.name_tag[name]+today_
                    self.worksheet.update_acell(save_cell, data[name])
            
        except Exception as ex:
            print('update_cell error')
            err_msg = traceback.format_exc()
            print(err_msg)
        
        #     self.slack.caht_DM(self.admin, self.texts['error'])
        
            
    def get_today(self, category = 't', update_date = None):
        if update_date is None:
            if category != 't':
                today_date = datetime.date.today()
            else:
                today_date = datetime.date.today() - datetime.timedelta(days=1)
        else:
            year, month, day = int(update_date[:4]), int(update_date[4:6]), int(update_date[6:8])
            today_date = datetime.date(year,month,day)
        
        dates = self.worksheet.col_values(1)
        # pdb.set_trace()
        for i, date in enumerate(dates[2:]):
            # print(i, date)
            if len(date) == 0:
                continue
            year = int('20'+date[0:2])
            month = int(date[3:5])
            day = int(date[6:8])
            date_ = datetime.date(year, month, day)
            if date_ - today_date == datetime.timedelta():
                if category == 't':
                    row = i+5
                elif category == 'l':
                    row = i+4
                elif category == 'g':
                    row = i+3
                break
        # pdb.set_trace()
            
        try:
            return str(row)
        except:
            self.slack.caht_DM(self.admin, self.texts['update'])
            # print('please update')
    
    def get_row(self, update_date = None):
        if update_date is None:
            today_date = datetime.date.today() - datetime.timedelta(days=1)
        else:
            year, month, day = int(update_date[:4]), int(update_date[4:6]), int(update_date[6:8])
            today_date = datetime.date(year,month,day)
        # pdb.set_trace()
        dates = self.hoursheet.col_values(2)
        for i, date in enumerate(dates):
            # print(i, date)
            if len(date) == 0:
                continue
            year = int('20'+date[0:2])
            month = int(date[3:5])
            day = int(date[6:8])
            date_ = datetime.date(year, month, day)
            if date_ - today_date == datetime.timedelta():
                # pdb.set_trace()
                return str(i+1)