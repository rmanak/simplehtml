Python replacement validation
=============================

The Python scripts in this directory are intended to be drop-in replacements
for the Perl utilities used by the `theme1` build. The following checks compare
their outputs against the Perl scripts to validate equivalence.

## 1) Markdown parity

Compare the HTML output from the Perl and Python entry points:

```
./bin/Markdown.pl < Template.txt > /tmp/md-perl.html
./bin/Markdown.py < Template.txt > /tmp/md-python.html
diff -u /tmp/md-perl.html /tmp/md-python.html
```

## 2) Code block extraction parity

```
./bin/find_code.pl < code.txt > /tmp/code-perl.s
./bin/find_code.py < code.txt > /tmp/code-python.s
diff -u /tmp/code-perl.s /tmp/code-python.s
```

## 3) HTML include parity

```
./bin/inc_file.pl < Template.html > /tmp/inc-perl.html
./bin/inc_file.py < Template.html > /tmp/inc-python.html
diff -u /tmp/inc-perl.html /tmp/inc-python.html
```

## 4) Page assembly parity

```
./bin/preppage.pl template sidebar.pm footbar.pm Template.w > /tmp/page-perl.html
./bin/preppage.py template sidebar.pm footbar.pm Template.w > /tmp/page-python.html
diff -u /tmp/page-perl.html /tmp/page-python.html
```
