.IGNORE:
SHELL = /bin/bash

SOURCES = Contact.txt  Links.txt download.txt  images.txt  code.txt  page1.txt  page3.txt  Credit.txt     README.txt  Template.txt  format.txt  latex.txt  page2.txt  toc.txt index.txt License.txt

pagefiles=$(SOURCES:.txt=.html)

default: all giveaccess

all: $(pagefiles)

footbar.pm: footbar
	./Markdown.pl footbar > footbar.pm

sidebar.pm: sidebar
	./Markdown.pl sidebar > sidebar.pm

%.s: %.txt
	cat $*.txt globalauthor globalkeywords globaldescription  > $*.txt2
	./find_code.pl < $*.txt2 > $*.s
	/bin/rm -f *.txt2

%.w: %.s
	./Markdown.pl $*.s > $*.w

%.html : %.w template footbar.pm sidebar.pm globalkeywords globalauthor globaldescription
	./preppage.pl template sidebar.pm footbar.pm $*.w | inc_file.pl > $*.html
	grep 'table_of_contents' $*.html && python ./pyhat.py -d. $*.html || echo $*.html generated

	
clean:
	/bin/rm -f $(pagefiles)
	/bin/rm -f *.txt2
	
giveaccess:
	chmod -R a+r *

