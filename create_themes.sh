#!/bin/bash

theme_index_list="2 3 4 5 6 7 8 9 10 11 12 13 14"

/bin/cp -f ./theme1/Template.txt ./theme1/index.txt

cd theme1
make
cd ..

for i in $theme_index_list; do
    echo "Building theme$i ..."
    /bin/rm -rf theme$i
    /bin/cp -rf theme1 theme$i    
    /bin/cp -f _builts/$i/template theme$i
    /bin/cp -f _builts/$i/sidebar theme$i
    /bin/cp -f _builts/$i/footbar theme$i
    /bin/cp -f _builts/$i/pagestyle.css theme$i/css
	sedpat="s/theme1\.tar\.gz/theme${i}.tar.gz/g"
	tl="'"
	cat ./theme1/Template.txt | sed $sedpat  > ./theme$i/Template.txt
	cat ./theme1/index.txt | sed $sedpat  > ./theme$i/index.txt
	cat ./theme1/download.txt | sed $sedpat  > ./theme$i/download.txt
	cat ./theme1/Credit.txt |   sed $sedpat > ./theme$i/Credit.txt
    cd theme$i
    make 2>&1 > /dev/null
    cd ..
    echo "=======Done!========="
done

