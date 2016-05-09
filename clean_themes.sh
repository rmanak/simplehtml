#!/bin/bash

theme_index_list="2 3 4 5 6 7 8 9 10 11 12 13 14"


for i in $theme_index_list; do
    echo "Removing theme$i ..."
    /bin/rm -rf theme$i*
    echo "=======Done!========="
done

