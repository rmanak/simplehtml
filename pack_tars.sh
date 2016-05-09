#!/bin/bash

theme_index_list="1 2 3 4 5 6 7 8 9 10 11 12 13 14"

for i in $theme_index_list; do
   echo "Building theme$i tarball ..."
   tar -czf theme${i}.tar.gz theme$i
   echo "=======Done!========="
done

