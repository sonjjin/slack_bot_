#!/bin/sh

date_list="
20230811"

for date in $date_list
do
    # python3 main_attandence.py --update_date $date
    python3 main_total.py --update_date $date
    sleep 10
done


