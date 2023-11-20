# salck bot for working
this repo is about slack bot for checking working in or leave

python 3.7.16
# start
pip install -r requirement.txt

# What?
매일 새벽 2시에 업데이트 합니당.
작동방법은 적기 너무 귀찮습니다..ㅠ

# V1.0
1. 매 30분마다 출근 및 퇴근시간을 sheet에 업데이트합니다.
2. 3월 한정, 아직 해당 시스템이 익숙하지 않기 때문에, 매일 밤 10시마다 퇴근을 하지 않은 인원에 한해서 slack에서 리마인드 DM을 보냅니다.
3. 구글 시트 상단에 현재 출근했는지 안했는지 한눈에 확인 할 수 있도록 상태바를 업데이트했습니다.
  ○: 출근안함 or 퇴근
  ●: 출근
4. 출근시간과 퇴근시간은 각각 가장 먼저 출근을 찍은 시간과 가장 늦게 퇴근을 찍은 시간을 나타냅니다.

특정날짜 업데이트할 때:
```console
date_list="
yyyymmdd
yyyymmdd"

for date in $date_list
do
    python3 main_attandence.py --update_date $date
    python3 main_total.py --update_date $date
    sleep 1m
done
```