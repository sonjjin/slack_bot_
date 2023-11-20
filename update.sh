#!/bin/sh

date_list="20230626 20230627 20230628 20230629 20230630"
for date in $date_list
do
    python3 main_total.py --update_date $date
done