Simple HTML
===========

This is a quick webpage generator and content management system 
powered by Perl that combines all the good stuff from:

* Markdown
* code2html (for code highlighting)
* PyHat (for table of content generator)

with my own addition of: 

* References (similar to Wikipedia) 
* Latex (needed some hacking to markdown script) to get it to work with MathJax
* Quick centered/right floating images with caption
* Include other HTML files
* All fonts included
* All scripts are included, no need to download anything beside the project


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
generated describe how the template works. For example see ``Template.txt`` for the source code 
of ``Template.html`` to get an idea of what are the additions to markdown syntax.

Here is a quick summary of how-to's: 

**1.3.1 Including a table of content** to document, just put: 

    [TOC]

wherever you like the TOC to appear, (uses ``<h1>`` ``<h2>`` tags, needs h1 to work)


**1.3.2 Creating a reference**

    A new reference here %%myreftag1%%. Another sentence...
    {myreftag1: See for example: <http://somelinktootherplace.com>}
    
**1.3.3 Inserting a right floating image with caption**

    {{my image caption}}((path/to/img/src.img))

**1.3.4 Inserting a center floating image with caption**

    {{my image caption}}[[path/to/img/src.img]]

**1.3.5 Including source code that will be highlighted**

    <PYTHON>
    import numpy as np
    </PYTHON>

**1.3.6 Including an external HTML file**

    <FILE="myotherhtmlfile.html">

**1.3.7 Writing LaTeX in the text**

    \\( x^2 + z_1 = 5 \\)

**1.3.8 Writing a large LaTeX content**

    <div>
    $$
    g_{\mu \nu} = 8 \pi T_{\mu \nu}
    $$
    </div>


#### 1.4 Editing the template

Edit the file ``template``.


2. Requirements
----------------

- Python
- Perl
- Linux make

(all the markdown, code2html and PyHat scripts are included in the folder)


3. Credit
---------

* [Markdown](http://daringfireball.net/projects/markdown/)
* [Code2Html](https://www.palfrader.org/code/code2html/)
* [PyHat](http://www.ferg.org/pyhat/)



