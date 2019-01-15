#!/bin/sh
tm=$1

zip -r9 $tm.zip $tm
mail -A $tm.zip -t < mail.txt
