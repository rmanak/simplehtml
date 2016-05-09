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

#-----------------------------------------------------------
#
#            WorkfileDocumentComponent
#
#-----------------------------------------------------------
class WorkfileDocumentComponent:
	def __init__(self, argType, argStartTag=""):
		self.myDocumentState = argType

		# self.myStartTag contains the whole tag, including pointy
		# brackets and attributes
		self.myStartTag = argStartTag
		
		# self.myElementName will be just the element name, e.g. "h2"
		if argStartTag == "": pass
		else:
			self.myElementName = argStartTag.replace("<", "").replace(">","").split()[0]
		self.myText = ""
		self.myEndTag   = ""
		self.myOutlineNumber = ""

		if self.myDocumentState == STATE_Heading:
			try:
				self.myHeadingLevel = int(self.myStartTag[2])
			except Exception, e:
				errorMessage(
					"Error when attempting to extract header level "
					+ " from tag: '" + self.myStartTag)
				raise e
		else:
			self.myHeadingLevel = 0

	def addText(self, argText):
		self.myText +=  argText

	def replaceText(self, argText):
		if optionVerbose: 
			print "\tCreating new table of contents"
		self.myText = argText

	def setOutlineNumber(self, argText):
		self.myOutlineNumber = argText

	def close(self, argTag=""):
		self.myEndTag = argTag

		if self.myDocumentState == STATE_Heading:
			# change all whitespace in the heading to a single space so that
			# when it is used as a Toc entry, it won't contain tabs or newlines.
			aListOfWordsInHeading = self.myText.split()

			if optionRemoveHeadingWord1 and self.myElementName != "h1":
				if len(aListOfWordsInHeading) > 0:
					if optionQuiet: pass
					else:
						print "\tRemoving", self.myStartTag, "word1:", aListOfWordsInHeading[0]
					aListOfWordsInHeading = aListOfWordsInHeading[1:]

			self.myText = " ".join(aListOfWordsInHeading)


	def toString(self):
		# for a component that is a TableOfContents, return its text
		if self.myDocumentState == STATE_Toc:
			return self.myText

		# for a component that is a Heading, return an appropriate string.
		# Except for <H1> tags, and heading tags that exceed the optionDeepestHeading,
		# this will include a target.
		if self.myDocumentState == STATE_Heading:
			if self.myHeadingLevel == 1:
				return "%s%s%s" % (self.myStartTag, self.myText, self.myEndTag)
			elif self.myHeadingLevel > optionDeepestHeading:
				return "%s%s%s" % (self.myStartTag, self.myText, self.myEndTag)
			else:
				aTarget = (""
				+ '<span class="%s"><a href="#%s_%s" id="%s_%s">\n'
				% (	CLASSNAME_FOR_Target
					, CLASSNAME_FOR_Toc , str(self.myOutlineNumber)
					, CLASSNAME_FOR_Target  , str(self.myOutlineNumber)
					)
				)
				aTarget += str(self.myOutlineNumber)
				aTarget +='</a>\n</span>'
				return "%s%s%s%s" % (self.myStartTag, aTarget, self.myText, self.myEndTag)

		# for everything else... body stuff... just return my text.
		return self.myText


	def getTextOfLineInTableOfContents(self):
		# this method will be executed for STATE_Heading components only
		if self.myDocumentState == STATE_Heading: pass # no problem
		else:  raise ("Program logic error: component.getTextOfLineInTableOfContents() method "
			+ "called for a document component that is not a header"
			)

		# Here's where we put the limit on the deepest header to use int
		# the table of contents.
		if self.myHeadingLevel > optionDeepestHeading: return ""

		indent = self.myHeadingLevel - 1
		colspan = TOTAL_COLUMNS - indent
		s = ('<tr>'
			+'<td colspan="%s">&nbsp;</td>' %  indent
			+'<td colspan="%s"><div style="text-align:left; text-indent:-3em; margin-left:3em;>' % colspan
			+'<a href="#%s_0">%s</a>' % (CLASSNAME_FOR_Target, str(self.myOutlineNumber))
			+ ' <a href="#%s_%s" id="%s_%s">'
			%
			(CLASSNAME_FOR_Target, str(self.myOutlineNumber)
			, CLASSNAME_FOR_Toc, str(self.myOutlineNumber)
			)
			+ self.myText
			+ "</a></div></td></tr>\n"
			)
		return s


#-----------------------------------------------------------
#
#     start: class definition for WorkfileParser
#
#-----------------------------------------------------------
class WorkfileParser(HTMLParser):

	def initialize(self, argInputText):
		# we remember this, so we can go back and display lines in
		# error, if a problem occurs.
		self.myInputText = argInputText

		# initialize variables used by the parser's state machine
		self.myState = STATE_Background

		self.rebuiltArg = "" # hold reconstituted text that triggered the event
		self.myTextOfLastOpenedHeadingTag = ""
		self.myLevelOfLastOpenedHeadingTag = 0

		# initialize variables used in constructing the output document
		self.myDocument = []

		# Not used in this parser, but kept for correspondence with InfileParser
		self.myDivCount = 0

		# a list used to store the headings that I've found
		self.myListOfHeadingTags = []

		# start a new, background component
		self.myComponentUnderConstruction = WorkfileDocumentComponent(self.myState)
		self.myDocument.append(self.myComponentUnderConstruction)


	def addText(self, argText):
		self.myComponentUnderConstruction.addText(argText)


	def getConstructedDocument(self):
		s = ""
		if optionVerbose:
			print ("\n"*6)+ "Components in my document:\n"
		i = 0
		for component in self.myDocument:
			i += 1
			if optionVerbose:
				print ("\n"
				+ ("~"*70) + "\n"
				+ "   Component number "+ str(i)
				+ "   Component type: " + component.myDocumentState + "\n"
				+ ("~"*70) + "\n"
				+ component.toString()
				+ "\n"
				+ ("~"*70) + "\n"
				)
			s += component.toString()
		return s

	#------------------------------------------------------------
	#      Major function: renumber the contents items
	#------------------------------------------------------------
	def renumberContentsItems(self):
		"""Put in the multi-level numbers"""
		aNumbersForLevels = [0,0,0,0,0,0,0,0]

		if optionVerbose: 
			print "\tRenumbering content items..."
		holdLevel = 0
		for aComponent in self.myListOfHeadingTags:
			aHeadingTagLevel = aComponent.myHeadingLevel

			if aHeadingTagLevel > holdLevel:
				aNumbersForLevels[aHeadingTagLevel] = 1
			elif aHeadingTagLevel == holdLevel:
				aNumbersForLevels[aHeadingTagLevel] = aNumbersForLevels[aHeadingTagLevel] + 1
			else: # aHeadingTagLevel < lastlevel
				aNumbersForLevels[aHeadingTagLevel] = aNumbersForLevels[aHeadingTagLevel] + 1

			startLevel = 2
			aComponent.setOutlineNumber( str(aNumbersForLevels[startLevel])) # 1 = first number

			i = startLevel + 1
			while i <= aHeadingTagLevel:
				aComponent.setOutlineNumber(aComponent.myOutlineNumber + "." + str(aNumbersForLevels[i]))
				i += 1
			if optionVerbose: 
				print "\t\t", aComponent.myStartTag, aComponent.myOutlineNumber

			holdLevel = aHeadingTagLevel



	#------------------------------------------------------------
	#
	#      Major function: generate the table of contents
	#
	#------------------------------------------------------------

	def generateTableOfContents(self):
		# First, we renumber the entries
		self.renumberContentsItems()

		# create the text of the table of contents, by scanning the components
		theTableOfContentsText = '<div class="%s">\n' % CLASSNAME_FOR_Toc
		theTableOfContentsText += '<!-- %s BEGIN TABLE OF CONTENTS %s -->' %(TILDES, TILDES)
		theTableOfContentsText += PROGRAM_INFO
		theTableOfContentsText += TARGET_ANCHOR
		theTableOfContentsText += '\n<h2>Table of Contents</h2>\n'
		theTableOfContentsText += '<table width="100%" border="0" cellpadding="0" cellspacing="0">\n'
		
		# create an empty row that controls the indentation in the table
		theTableOfContentsText += '<tr>\n'

		# allocate 4% of the page width to all columns, except the last
		for i in range(TOTAL_COLUMNS - 1):
			theTableOfContentsText += '<td width="4%">&nbsp;</td>' 
		
		# the last column, which will contain the text of the headings, 
		# is not a fixed width.
		theTableOfContentsText += '<td>&nbsp;</td>\n</tr>\n'

		# for each component that is a heading (and has a level greater than 1)
		# we add a row to the text of the table of contents		
		for aComponent in self.myListOfHeadingTags:
			if aComponent.myHeadingLevel > 1:
				theTableOfContentsText += aComponent.getTextOfLineInTableOfContents()

		# now we close theTableOfContentsText
		theTableOfContentsText += '</table>\n<!-- %s _END_ TABLE OF CONTENTS %s -->\n' %(TILDES, TILDES)
		theTableOfContentsText += '</div>'

		if optionVerbose: 
			print "\n\tNumber of head <h#> entries =", str(len(self.myListOfHeadingTags))
			print INSERTING_TOC_MESSAGE
			
		# now that we've generated the table of contents text, we go looking
		# for a place to put it.
		for aComponent in self.myDocument:
			if aComponent.myDocumentState == STATE_Toc:
				aComponent.replaceText(theTableOfContentsText)
				return  # replace it only in the first location


		#-----------------------------------------------------------------
		# we couldn't find a place to put the table of contents
		#-----------------------------------------------------------------
		if optionVerbose: 
			print "Guessing where to insert TableOfContents"
			print INSERTING_TOC_MESSAGE
			
		# We insert a place to put the table of contents.
		# We try put it before the third component, which presumably
		# is immediately after the first <H1> tag is closed.
		if len(self.myDocument)>= 2: location = 3
		else: location = 0

		self.myState = STATE_Heading  # we don't need to reverse this. We'll never use it again.
		self.myComponentUnderConstruction = \
			WorkfileDocumentComponent('<div class="%s">' % CLASSNAME_FOR_Toc)
		self.myComponentUnderConstruction.myText = theTableOfContentsText
		self.myComponentUnderConstruction.close('</div>')
		self.myDocument.insert(location,self.myComponentUnderConstruction)

			
	#----------------------------------------------------------------------
	#  callbacks (event handlers) to handle parser events
	#
	# Note that the parser is a state machine. It has states and events,
	# and it responds to events by changing its state.
	#------------------------------------------------------------------

	def handle_starttag(self, argTag, argAttrs):

		self.rebuild_starttag(argTag, argAttrs)
		event = self.recognize(START_TAG, argTag, argAttrs)

		if event == EVENT_StartToc:
			self.myState = STATE_Toc

			self.myComponentUnderConstruction = \
				WorkfileDocumentComponent(self.myState, self.rebuiltArg)
			self.myDocument.append(self.myComponentUnderConstruction)

		elif event == EVENT_StartHeading:
			self.myState = STATE_Heading
			self.myTextOfLastOpenedHeadingTag = self.rebuiltArg
			self.myLevelOfLastOpenedHeadingTag = int(argTag[1])

			self.myComponentUnderConstruction = \
				WorkfileDocumentComponent(self.myState, self.rebuiltArg)
			self.myDocument.append(self.myComponentUnderConstruction)
			self.myListOfHeadingTags.append(self.myComponentUnderConstruction)

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
				WorkfileDocumentComponent(self.myState)
			self.myDocument.append(self.myComponentUnderConstruction)


		elif event == EVENT_EndHeading:
			self.myState = STATE_Background

			# close the Target
			self.myComponentUnderConstruction.close(self.rebuiltArg)

			# start some background text
			self.myComponentUnderConstruction = \
				WorkfileDocumentComponent(self.myState)
			self.myDocument.append(self.myComponentUnderConstruction)

		else:
			# just add this text to the component that we're building
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
		if (self.myState == STATE_Heading
			and argTagType == START_TAG
			and self.isHeadingTag(argTag)
			):
			# we encountered a head tag when we're already in a head tag
			# this is an error
			self.reportError(
				"I found a tag indicating the beginning of "
				+ "a heading: "
				+ self.rebuiltArg
				+ "\nBut we are already inside the scope of another heading tag :"
				+ self.myTextOfLastOpenedHeadingTag
				+ "\nThis is invalid markup in the input file."
				+ "\nSpecifically, this is invalid HTML: heading tags cannot be nested."
				, self.getpos()
				)

		if (self.myState == STATE_Toc
			and argTagType == START_TAG
			and self.isTocBeginTag(argTag)
			):
			# we encountered a TocBegin tag when we're already inside a Toc
			# this is an error
			self.reportError(
				"I found a tag indicating the beginning of "
				+ "the table of contents: "
				+ self.rebuiltArg
				+ "\nBut we are already inside the table of contents."
				+ "\nThis is invalid markup in the input file."
				, self.getpos()
				)

		if (self.myState == STATE_Heading
			and argTagType == START_TAG
			and self.isTocBeginTag(argTag, argAttrs)
			):
			# we encountered a TocBegin tag when we're already inside a Heading tag.
			# this is an error
			self.reportError(
				"I found a tag indicating the beginning of "
				+ "the table of contents: "
				+ self.rebuiltArg
				+ "\nBut we are inside the scope of a head tag: "
				+ self.myTextOfLastOpenedHeadingTag
				+ "\nThis is invalid markup in the input file."
				, self.getpos()
				)


		if (self.myState == STATE_Background
			and argTagType == START_TAG
			and self.isHeadingTag(argTag)
			):

			levelOfThisHeadingTag = int(argTag[1])
			if levelOfThisHeadingTag > (self.myLevelOfLastOpenedHeadingTag + 1):
				# we encountered a head tag that is too deeply nested,
				# it breaks the proper progression of nesting
				self.reportError(
					"There is a break in heading levels in the document."
					+"\nThe current head level in the document is: "
					+ str(self.myLevelOfLastOpenedHeadingTag)
					+"\nI found a head tag at level: "
					+ str(levelOfThisHeadingTag)
					+"\nError occurs in line " + str(self.getpos()[0])
					, self.getpos()
					)
			else: # a valid head tag, at the proper depth...
				return EVENT_StartHeading


		if (self.myState == STATE_Background
			and argTagType == START_TAG
			and self.isTocBeginTag(argTag, argAttrs)
			):
			return EVENT_StartToc


		if (self.myState == STATE_Toc
			and argTagType == END_TAG
			and self.myDivCount == 0
			and argTag == "div"
			):
			return EVENT_EndToc


		if (argTagType == END_TAG
			and self.isHeadingTag(argTag)
			):
			if self.myState == STATE_Heading:
				# verify that close head tag matches the last-opened head tag
				levelOfThisHeadingTag = int(argTag[1])
				if levelOfThisHeadingTag == self.myLevelOfLastOpenedHeadingTag:
					return EVENT_EndHeading
				else:
					self.reportError("Closing head tag"
						+ self.rebuiltArg
						+ "\ndoes not match the last-opened head tag: "
						+ self.myTextOfLastOpenedHeadingTag
						, self.getpos()
						)
			else:
				self.reportError("I encountered a "
					+ self.rebuiltArg
					+ "tag, but we are not in the scope of a "
					+ "previously-opened Heading tag."
					, self.getpos()
					)

		# else
		return TRIVIAL_EVENT


	# a helper function for the recognizer
	def isTocBeginTag(self, argTag, argAttrs):
		if argTag == "div" and getClass(argAttrs)== CLASSNAME_FOR_Toc:
			return True
		else:
			return False

	# a helper function for the recognizer
	def isHeadingTag(self, argTag):
		if argTag == "hr": return False

		if len(argTag) == 2 and argTag[0] == "h":
			for i in VALID_HEADING_NUMBERS:
				try:
					tagLevel = int(argTag[1])
					if tagLevel == i:
						return True
				except ValueError, e:
					return False
			return False
		else:
			return False





	#------------------------------------------------------------------
	#  error handling code
	#------------------------------------------------------------------

	def reportError(self, msg, argErrorPosition=None):
		if argErrorPosition != None:
			virtualPrint("****************************************************************")
			virtualPrint("NOTE!!! Line numbers are based on the state of the input file")
			virtualPrint("AFTER OLD TABLE-OF-CONTENTS INFORMATION HAS BEEN REMOVED.")
			virtualPrint("They may differ from line numbers in the input file.")
			virtualPrint("****************************************************************")
			virtualPrint("")					
			virtualPrint("Lines before the error location:" +
						self.getInputLinesPreceeding(argErrorPosition))

		errorHandler(msg)


	def getInputLinesPreceeding(self, argErrorPosition):
		result = ""
		
		toLineNumber = argErrorPosition[0]
		fromLineNumber = toLineNumber - ERROR_LINES_TO_PRINT
		fromLineNumber = max(fromLineNumber, 1)
		
		someLines = self.myInputText.split("\n")
		
		for i in range(fromLineNumber-1, toLineNumber):
			result += "\n" + ("(" + str(i+1) + ") ").rjust(8) + someLines[i]
			
		# point to the exact column where the error was discovered
		columnPosition = argErrorPosition[1]
		result += "\n" + ("(" + str(i+1) + ") ").rjust(8) + ("."* columnPosition) + "$"

		return result


#-----------------------------------------------------------
#
#     end: class definition for WorkfileParser(HTMLParser)
#
#-----------------------------------------------------------

def runPass2OnDocument(argDocument
		, argOptionQuiet=False
		, argOptionVerbose=False
		, argOptionDeepestHeading=4
		, argOptionRemoveHeadingWord1=False		
		):
			
	global optionQuiet, optionVerbose, optionRemoveHeadingWord1
	global optionDeepestHeading
	optionQuiet   = argOptionQuiet
	optionVerbose = argOptionVerbose
	optionRemoveHeadingWord1 = argOptionRemoveHeadingWord1
	optionDeepestHeading = argOptionDeepestHeading
	
	aParser = WorkfileParser()
	aParser.initialize(argDocument)
	aParser.feed(argDocument)  # parse the document

	# tell the parser to generate a new table of contents
	aParser.generateTableOfContents()

	# return the document that the parser created
	aDocument = aParser.getConstructedDocument()
	return aDocument
