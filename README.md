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


1. Quick Start
--------------

Simply clone the repository and run ``make``:

    [bash]$make

for the html pages to be generated.

#### 1.1 Adding a new page

Create a new file ``mynewfile.txt`` and add it to the list of pages in the ``Makefile``.

#### 1.2 Adding a link to the sidebar

Edit the file ``sidebar`` (it's format is the same as Markdown)

#### 1.3 Formatting

The template's content (either ``index.html`` or ``Template.html``) files that are
generated describe how the template work. See ``Template.txt`` for the source code 
of how to create table of content, references, including other HTML files and 
more examples. Some additional formatting (beside all markdown formatting) are as following

* Including a table of content to document, just put: (uses ``<h1>`` ``<h2>`` tags, needs h1 to work)
    [TOC]

* Creating a reference:
    A new reference here %%myreftag1%%. Another sentence...
    {myreftag1: See for example: <http://somelinktootherplace.com>}
    
* Inserting a right floating image with caption: 
    {{my image caption}}((path/to/img/src.img))

* Inserting a center floating image with caption:
    {{my image caption}}[[path/to/img/src.img]]

* Including source code that will be highlighted:
    <PYTHON>
    import panda as pd
    </PYTHON>

* Including an external HTML file:
    <FILE="myotherhtmlfile.html">

* Writing LaTeX in the text
    \\( x^2 + z_1 = 5 \\)

* Writing a large LaTeX content:
    <div>
    $$
    g_{\mu \nu} = 8 \pi T_{\mu \nu}
    $$
    </div>


#### 1.4 Editing the template

Edit the file ``template``.


2. Requirements
----------------

- python
- perl
- linux make
(all the markdown, code2html and pyhat scripts are included in the folder)


3. Credit
---------

* [Markdown](http://daringfireball.net/projects/markdown/)
* [Code2Html](https://www.palfrader.org/code/code2html/)
* [PyHat](http://www.ferg.org/pyhat/)



