"""-----------------------------------------------------------------
REVISION HISTORY
 4 2004-11-10 renamed program to "pyhat.py"
--------------------------------------------------------------------"""

from HTMLParser import HTMLParser
import getopt
import sys
import os
import time
import string
import cgi
from   pyhatConstants import *

#----------------------------------------------------------
#
#         InfileDocumentComponent
#
#-----------------------------------------------------------
class InfileDocumentComponent:
	"""This is a component that will be built and written
	to the workfile by the InfileParser.
	"""
	def __init__(self, argType, argStartTag=""):
		self.myDocumentState = argType

		self.myStartTag = argStartTag
		self.myText     = ""
		self.myEndTag   = ""

	def addText(self, argText):
		self.myText +=  argText

	def close(self, argTag=""):
		self.myEndTag = argTag

	def toString(self):
		# Note that each component is smart, and knows what to return when
		# the toString() method is invoked.
		# A Toc will return TABLE_OF_CONTENTS_PLACEHOLDER.
		# A Target will return the empty string.

		if self.myDocumentState == STATE_Toc:
			return TABLE_OF_CONTENTS_PLACEHOLDER
		elif self.myDocumentState == STATE_Target:
			return "" # completely remove targets from the infile
		else:
			return self.myText

#-----------------------------------------------------------
#
#     start: class definition for InfileParser(HTMLParser)
#
#-----------------------------------------------------------

class InfileParser(HTMLParser):

	def initialize(self, argInputText):
		# we remember this, so we can go back and display lines in
		# error, if a problem occurs.
		self.myInputText = argInputText

		# initialize variables used by the parser's state machine
		self.myState = STATE_Background
		self.mySpanCount = 0
		self.myDivCount  = 0
		self.myTocCount  = 0     # page should not contain more than one Toc
		self.myStartHeading1Count = 0  # page should not contain more than one H1 tag
		self.myEndHeading1Count   = 0  # page should not contain more than one H1 tag
		self.rebuiltArg     = "" # holds reconstituted text that triggered the event

		# initialize variables used in constructing the output document
		self.myDocument = []

		# start a new, background component
		self.myComponentUnderConstruction = InfileDocumentComponent(self.myState)
		self.myDocument.append(self.myComponentUnderConstruction)


	def addText(self, argText):
		self.myComponentUnderConstruction.addText(argText)


	def getConstructedDocument(self):
		s = ""
		if optionVerbose:
			print ("\n"*6)+ "Components in my document:\n"
			dividerLine = "~"*70 + "\n"
		i = 0
		for component in self.myDocument:
			i += 1
			if optionVerbose:
				if component.myDocumentState == STATE_Toc:
					print "\n", dividerLine + "Omitting Toc\n" + dividerLine + "\n"
				elif component.myDocumentState == STATE_Target:
					print "\n", dividerLine + "Omitting Target\n" + dividerLine + "\n"
				else:
					print ("\n"
					+ dividerLine
					+ "   Component number "+ str(i)
					+ "   Component type: " + component.myDocumentState + "\n"
					+ dividerLine
					+ component.toString()
					+ "\n"
					+ dividerLine
					)

			# Note that each component is smart, and knows what to return when
			# the toString() method is invoked.
			# A Toc will return TABLE_OF_CONTENTS_PLACEHOLDER.
			# A Target will return the empty string.

			s += component.toString()
		return s

	#----------------------------------------------------------------------
	# callbacks (event handlers) to handle parser events
	#
	# Note that the parser is a state machine. It has states and events,
	# and it responds to events by changing its state.
	#------------------------------------------------------------------
	def handle_starttag(self, argTag, argAttrs):

		self.rebuild_starttag(argTag, argAttrs)
		event = self.recognize(START_TAG, argTag, argAttrs)

		if event == EVENT_StartToc:
			self.myState = STATE_Toc
			self.myDivCount = 0    #initialize the "div" counter

			self.myTocCount += 1  # count occurrences of Toc start

			self.myComponentUnderConstruction = \
				InfileDocumentComponent(self.myState, self.rebuiltArg)
			self.myDocument.append(self.myComponentUnderConstruction)

		elif event == EVENT_StartDiv:
			self.myDivCount += 1 #increment the "div" counter

		elif event == EVENT_StartTarget:
			self.myState = STATE_Target
			self.mySpanCount = 0    #initialize the "span" counter
			self.myComponentUnderConstruction = \
				InfileDocumentComponent(self.myState, self.rebuiltArg)
			self.myDocument.append(self.myComponentUnderConstruction)

		elif event == EVENT_StartSpan:
			self.mySpanCount += 1 #increment the "span" counter

		elif event == EVENT_StartHeading1:
			self.myStartHeading1Count += 1
			self.addText(self.rebuiltArg)

		else:
			self.addText(self.rebuiltArg)


	def handle_startendtag(self, argTag, argAttrs):
		self.rebuild_startendtag(argTag, argAttrs)
		self.addText(self.rebuiltArg)


	def handle_endtag(self, argTag):

		self.rebuild_endtag(argTag)
		event = self.recognize(END_TAG, argTag)

		if event == EVENT_EndToc:
			self.myState = STATE_Background

			# close the Table of Contents
			self.myComponentUnderConstruction.close(self.rebuiltArg)

			# start some background text
			self.myComponentUnderConstruction = \
				InfileDocumentComponent(self.myState)
			self.myDocument.append(self.myComponentUnderConstruction)

		elif event == EVENT_EndDiv:
			# close the div tag
			self.myDivCount -= 1 # decrement the "div" counter
			self.addText(self.rebuiltArg)

		elif event == EVENT_EndTarget:
			self.myState = STATE_Background

			# close the Target
			self.myComponentUnderConstruction.close(self.rebuiltArg)

			# start some background text
			self.myComponentUnderConstruction = \
				InfileDocumentComponent(self.myState)
			self.myDocument.append(self.myComponentUnderConstruction)

		elif event == EVENT_EndSpan:
			# close the span tag
			self.mySpanCount -= 1 # decrement the "span" counter
			self.addText(self.rebuiltArg)

		elif event == EVENT_EndHeading1:
			self.myEndHeading1Count += 1
			self.addText(self.rebuiltArg)

		else:
			# add this text to the component that we're building
			self.addText(self.rebuiltArg)


	def handle_data(self, argString):
		self.rebuild_data(argString)
		self.addText(self.rebuiltArg)

	def handle_charref(self, argString):
		self.rebuild_charref(argString)
		self.addText(self.rebuiltArg)

	def handle_entityref(self, argString):
		self.rebuild_entityref(argString)
		self.addText(self.rebuiltArg)

	def handle_comment(self, argString):
		self.rebuild_comment(argString)
		self.addText(self.rebuiltArg)

	def handle_decl(self, argString):
		self.rebuild_decl(argString)
		self.addText(self.rebuiltArg)


	#-----------------------------------------------------------------
	#   routines to re-assemble the string that caused the event
	#-----------------------------------------------------------------
	def rebuild_starttag(self, argTag, argAttrs):
		s = "<%s" %  argTag
		for attr in argAttrs:
			s = s + ' %s="%s"' % (attr[0], attr[1])
		self.rebuiltArg = s + ">"
		self.ShowEventString(self.rebuiltArg)


	def rebuild_startendtag(self, argTag, argAttrs):
		s = "<%s" %  argTag
		for attr in argAttrs:
			s = s + ' %s="%s"' % (attr[0], attr[1])
		self.rebuiltArg = s + "/>"
		self.ShowEventString(self.rebuiltArg)


	def rebuild_endtag(self, argTag):
		self.rebuiltArg = "</%s>" %  argTag
		self.ShowEventString(self.rebuiltArg)


	def rebuild_data(self, argString):
		self.rebuiltArg = argString
		self.ShowEventString(self.rebuiltArg)


	def rebuild_charref(self, argString):
		self.rebuiltArg = "&#%s;" % argString
		self.ShowEventString(self.rebuiltArg)


	def rebuild_entityref(self, argString):
		self.rebuiltArg = "&%s;" % argString
		self.ShowEventString(self.rebuiltArg)


	def rebuild_comment(self, argString):
		self.rebuiltArg = "<!--%s-->" % argString
		self.ShowEventString(self.rebuiltArg)


	def rebuild_decl(self, argString):
		self.rebuiltArg = "<!%s>" % argString
		self.ShowEventString(self.rebuiltArg)


	def ShowEventString(self, argString):
		if optionVerbose:
			print (
				str(self.getpos()[0]).rjust(5)
				+ ":"
				+ str(self.getpos()[1]).ljust(3)
				), self.myState, argString
		return


	#------------------------------------------------------------------
	#  A "recognizer" method, used by the state machine to recognize
	#  and accept significant events,
	#  and also to recognize and reject invalid events.
	#------------------------------------------------------------------

	def recognize(self, argTagType, argTag, argAttrs=None):
		if (self.myState   == STATE_Toc
			and argTagType == START_TAG
			and self.isTargetBeginTag(argTag, argAttrs)
			):
			# we encountered a target tag when we're already in a Toc
			# this is an error
			self.errorHandler(
				"I found a tag indicating the beginning of "
				+ "a target: "
				+ self.rebuiltArg
				+ "\nBut we are inside the scope of an existing table of contents."
				+ "\nThis is invalid markup in the input file."
				, self.getpos()
				)

		if (self.myState   == STATE_Target
			and argTagType == START_TAG
			and self.isTargetBeginTag(argTag, argAttrs)
			):
			# we encountered a target tag when we're already in a target tag
			# this is an error
			self.errorHandler(
				"I found a tag indicating the beginning of "
				+ "a target: "
				+ self.rebuiltArg
				+ "\nBut we are already inside the scope of another target."
				+ "\nThis is invalid markup in the input file."
				, self.getpos()
				)

		if (self.myState   == STATE_Toc
			and argTagType == START_TAG
			and self.isTocBeginTag(argTag, argAttrs)
			):
			# we encountered a TocBegin tag when we're already inside a Toc
			# this is an error
			self.errorHandler(
				"I found a tag indicating the beginning of "
				+ "the table of contents: "
				+ self.rebuiltArg
				+ "\nBut we are already inside the table of contents."
				+ "\nThis is invalid markup in the input file."
				, self.getpos()
				)

		if (self.myState   == STATE_Target
			and argTagType == START_TAG
			and self.isTocBeginTag(argTag, argAttrs)
			):
			# we encountered a TocBegin tag when we're inside a Target tag.
			# this is an error
			self.errorHandler(
				"I found a tag indicating the beginning of "
				+ "the table of contents: "
				+ self.rebuiltArg
				+ "\nBut we are inside the scope of a target tag. "
				+ "\nThis is invalid markup in the input file."
				, self.getpos()
				)

		if (self.myState   == STATE_Background
			and argTagType == START_TAG
			and self.isTargetBeginTag(argTag, argAttrs)
			):
			return EVENT_StartTarget


		if (self.myState   == STATE_Background
			and argTagType == START_TAG
			and self.isTocBeginTag(argTag, argAttrs)
			):
			# more than one Toc position is an error
			if self.myTocCount > 1:
				self.errorHandler("Input file contains more than one "
					+'\n<div class="table_of_contents"> tag.'
					, self.getpos()
					)
			else:
				return EVENT_StartToc


		if (self.myState   == STATE_Toc
			and argTagType == START_TAG
			and argTag == "div"):
				return EVENT_StartDiv

		if (self.myState   == STATE_Toc
			and argTagType == END_TAG
			and argTag == "div"):
			if self.myDivCount == 0:
				return EVENT_EndToc
			else:
				return EVENT_EndDiv


		if (self.myState   == STATE_Target
			and argTagType == END_TAG
			and argTag == "span"):
			if self.mySpanCount == 0:
				return EVENT_EndTarget
			else:
				return EVENT_EndSpan

		if (argTagType == START_TAG and argTag == "h1"):
			if self.myStartHeading1Count > 1:
				self.errorHandler("Input file contains more than one <H1> tag."
					+"\nThe page should contain  only one <H1> tag,"
					+"\ndelimiting the page title."
					, self.getpos()
					)
			# else
			return EVENT_StartHeading1


		if (argTagType == END_TAG and argTag == "h1"):
			if self.myEndHeading1Count > 1:
				self.errorHandler("Input file contains more than one </H1> tag."
					+"\nThe page should contain  only one </H1> tag,"
					+"\ndelimiting the page title."
					, self.getpos()
					)
			# else
			return EVENT_EndHeading1

		# else
		return TRIVIAL_EVENT

	# a helper function for the recognizer
	def isTocBeginTag(self, argTag, argAttrs):
		if argTag == "div" and getClass(argAttrs)== CLASSNAME_FOR_Toc:
			return True
		else:
			return False


	# a helper function for the recognizer
	def isTargetBeginTag(self, argTag, argAttrs):
		if argTag == "span" and getClass(argAttrs)== CLASSNAME_FOR_Target:
			return True
		else:
			return False




	#------------------------------------------------------------------
	#  error handling code
	#------------------------------------------------------------------
	def errorHandler(self, msg, argErrorPosition=None):
		errorMessage(msg)
		if argErrorPosition != None:
			virtualPrint("\n~~~~~~~~ [ Lines before the error location ] ~~~~~~~~\n")
			virtualPrint(self.getInputLinesPreceeding(argErrorPosition))
			virtualPrint( "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
		sys.exit(1)

	def getInputLinesPreceeding(self, argErrorPosition):
		result = ""
		toLineNumber = argErrorPosition[0]
		fromLineNumber = toLineNumber - ERROR_LINES_TO_PRINT
		fromLineNumber = max(fromLineNumber, 1)
		someLines = self.myInputText.split("\n")
		for i in xrange(fromLineNumber-1, toLineNumber):
			result +=  "(" + str(i+1) + ") " + someLines[i]
		# point to the exact column where the error was discovered
		columnPosition = argErrorPosition[1]
		result += "(" + str(i+1) + ") " + ("."* columnPosition) + "$"
		return result

#-----------------------------------------------------------
#
#     end: class definition for InfileParser(HTMLParser)
#
#-----------------------------------------------------------

def runPass1OnDocument(argDocument, argOptionQuiet=False, argOptionVerbose=False):
	global optionQuiet, optionVerbose 
	optionQuiet   = argOptionQuiet
	optionVerbose = argOptionVerbose

	
	# Parse aDocument to remove the existing
	# TableOfContents and target tags, if any are present.
	aParser = InfileParser()        # create a parser object
	aParser.initialize(argDocument) # set initial values in the parser
	aParser.feed(argDocument)       # parse the document and create a new document

	# return the text of the document that the parser has created.
	return aParser.getConstructedDocument()
