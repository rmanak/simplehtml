#!/bin/bash

list=`ls *.svg`

str1='<p>&nbsp;&nbsp;'
str2='<img src="'
str3='" /></p>'

for i in $list; do
echo $str1$i$str2$i$str3
done
