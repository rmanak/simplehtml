Simple HTML
===========

This is a quick webpage generator and content management system 
powered by perl that combines all the good stuff from:
* Markdown
* code2html (for code highlighting)
* PyHat (for table of content generator)
* References (similar to wikipedia) 
* and some additional quick features, such as including 
(right or centered float) images with caption, including
other html files 

See the homepage of the project: <http://laplace.phas.ubc.ca/People/arman/sg/>
![alt tag](https://github.com/rmanak/simplehtml/blob/master/img/screenshot.png)


Quick Start
-----------

Simply clone the repository and run ``make``:

    [bash]$make

for the html pages to be generated.

### Adding a new page

Create a new file ``mynewfile.txt`` and add it to the list of pages in the ``Makefile``.

### Adding a link to the sidebar

Edit the file ``sidebar`` (it's format is the same as Markdown)

### Formatting

The template's content (either ``index.html`` or ``Template.html``) files that are
generated describe how the template work. See ``Template.txt`` for the source code 
of how to create table of content, references, including other HTML files and 
more examples.


### Editing the template

Edit the file ``template``.


Requirements
------------
- python
- perl
- linux make
(all the markdown, code2html and pyhat scripts are included in the folder)



