import schedule
import time
from attandence_check import attandence_check
import json
import os
import argparse
import datetime

if __name__ == '__main__':

    info_path = '/home/jinsu.son/workspace/code/slack/info'
    outlier_path = os.path.join(info_path, 'outlier.json')
    with open(outlier_path, 'r') as fj:
        outlier = json.load(fj)
    attandence_check_  = attandence_check(info_path, outlier)
    schedule.every(30).seconds.do(attandence_check_.update_leave_or_work,'g')
    schedule.every(30).seconds.do(attandence_check_.update_leave_or_work,'l')
    schedule.every(30).hours.do(attandence_check_.update_state)
    # schedule.every(1).hours.do(attandence_check_.update_total)
    schedule.every().day.at("05:29").do(attandence_check_.update_total)
    schedule.every().day.at("23:00").do(attandence_check_.reminder,'11PM')
    schedule.every().day.at("01:00").do(attandence_check_.reminder,'01AM')
    schedule.every().day.at("02:00").do(attandence_check_.reminder,'02AM')
    schedule.every().day.at("03:00").do(attandence_check_.reminder,'03AM')
    
    
    while True:
        try:
            # attandence_check_.slack.caht_DM(attandence_check_.admin, attandence_check_.texts['error'])
            schedule.run_pending()
            time.sleep(30)
            
            now = datetime.datetime.now()
            hh = str(now.hour).zfill(2)
            mm = str(now.minute).zfill(2)
            tt = hh+mm
            if tt == '0530':
                break
        except:
            attandence_check_.slack.caht_DM(attandence_check_.admin, attandence_check_.texts['error'])
            