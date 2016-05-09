#!/usr/bin/env python
"""PROGRAM : pyhat.py
FUNCTION: Add a table of contents to HTML files. 

USAGE
----------------------------------------------------

      pyhat [options] filename [filenames...]


OPTIONS
----------------------------------------------------

  -d<directoryName>
      specifies a directory where the output files are placed.
      Defaults to "pyhat_out".

  -h<integer>
      defines the deepest headingElement to be included in the table
      of contents.  If present, <integer> must be in the range 2..6.
      Defaults to 4.
      Not compatible with -x.

  -x
      removes all pyhat markup except for a tag indicating the location
      where the table of contents should be inserted.
      Does not regenerate table-of-contents markup.
      Not compatible with -w or -h. 

  -w
      removes the first word of every head tag.
      This option supports conversion from files in which table-of-contents 
      numbers are hard-coded as the first word of the header tags.
      Not compatible with -x.

  -v
      verbose mode: shows a lot of progress information. Useful for debugging.
      Not compatible with -q.

  -q
      quiet mode: suppresses normal (minimal) progress messages
      Not compatible with -v.
"""
"""-----------------------------------------------------------------
AUTHOR
 Stephen Ferg (steve@ferg.org)
 http://www.ferg.org/pyhat/index.html

REVISION HISTORY
 4 2004-11-10 modularized the code and implemented CGI support
--------------------------------------------------------------------"""

from HTMLParser import HTMLParser
import getopt
import sys
import os
import time
import string
import cgi
from   pyhatConstants import *
from   pyhatPass1     import *
from   pyhatPass2     import *

# the defaults are for CGI processing
optionOutputDir ="pyhat_out"
optionVerbose = False
optionQuiet   = True
optionRunMode = RUNMODE_REPLACE
optionDeepestHeading = 4
optionRemoveHeadingWord1 = False

def processDocument(aDocument, argRunMode):

	aDocument = runPass1OnDocument(aDocument, optionQuiet, optionVerbose)		
	if optionVerbose: print "Run mode is:", argRunMode	
	
	if argRunMode == RUNMODE_REMOVE:
		# Our job is merely to remove the old tags.
		# Since we have done that, we don't do anything more

		return aDocument
	else:
		# optionRunMode == RUNMODE_REPLACE
		# Our job also involves replacing (or regenerating) a new
		# table of contents.  So we run the document that we have
		# created through a second parser.  This parser re-creates
		# the TableOfContents and its associated links.
		if optionVerbose: print PASS2_MESSAGE
		return runPass2OnDocument(aDocument, 
			optionQuiet, 
			optionVerbose, 
			optionDeepestHeading, 
			optionRemoveHeadingWord1)

#------------------------------------------------------
#
#   mainline
#
#------------------------------------------------------
def main():
	global optionOutputDir, optionVerbose, optionQuiet, optionRunMode  
	global optionDeepestHeading, optionRemoveHeadingWord1  

	try:
		# options that require an argument are followed by a colon
		cmdlineOptions, args= getopt.getopt(sys.argv[1:],'d:h:vqwx')
	except getopt.GetoptError, e:
		raise "Error in a command-line option:\n\t" + str(e)

	optionH = False	
	for (optName,optValue) in cmdlineOptions:
		if   optName == '-h':
			try:
				optionH = True
				optionDeepestHeading = int(optValue)
				if (optionDeepestHeading < 2 or
					optionDeepestHeading > 6 ):
					print ("Invalid argument value for option "
						+ optName + ". It is: '" + optValue + "'"
						+"\nValue must be an integer in the range of 2..6"
						)
					errorEnd()
			except ValueError, e:
					print ("Invalid argument value for option "
						+ optName + ". It is: '" + optValue + "'"
						+"\nValue must be an integer in the range of 2..6"
						)
					errorEnd()
					
		elif optName == '-d': optionOutputDir = optValue
		elif optName == '-x': optionRunMode = RUNMODE_REMOVE
		elif optName == '-v': optionVerbose = True
		elif optName == '-q': optionQuiet   = True
		elif optName == '-w': optionRemoveHeadingWord1 = True
		else:
			errorHandler('Option %s not recognized' % optName)

	if optionRunMode == RUNMODE_REMOVE and optionRemoveHeadingWord1:
		raise "\nOption -x (remove ToC markup) and option -w (remove first word of headings)"\
			"\ncannot both be specified."

	if optionRunMode == RUNMODE_REMOVE and optionH:
		raise "\nOption -x (remove ToC markup) and option -h (deepest heading level)"\
			"\ncannot both be specified."
						
	if optionQuiet and optionVerbose:
		raise "\nOption -q (quiet) and option -v (verbose)"\
			"\ncannot both be specified."			
	
	if d_exists(optionOutputDir): pass
	else: 
		d_create(optionOutputDir)

	if d_exists(optionOutputDir): pass
	else: 
		raise "I couldn't find or create output directory: " + optionOutputDir
			
	if len(args) == 0:
		print __doc__
		sys.exit()
		
	
	if optionVerbose:
		print "\n\nStarting pyhat"
		print "Command-line options are:"
		for (optName,optValue) in cmdlineOptions:
			virtualPrint( "\t" + optName + ": " + optValue)
	
	
	fcount = 0
	for inFilename in args:
		fcount += 1
		head, tail = os.path.split(inFilename)
		outFilename  = os.path.normpath("%s/%s" % (optionOutputDir , tail))
	
		if optionQuiet: pass
		elif optionVerbose: print PASS1_MESSAGE
		else:
			print "    (%s) infile='%s'  outfile='%s'" \
				% (str(fcount), inFilename, outFilename)
		
		aDocument = getDocumentText(inFilename)
		aDocument = processDocument(aDocument, optionRunMode)
		writeOutputDocument(aDocument, outFilename)
	
		if optionVerbose:
			print "Ending pyhat: output file is", outFilename
	

if __name__ == "__main__": 
	optionQuiet = False
	main()	
