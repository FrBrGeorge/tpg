
set noruntime	# the runtime is in the grammar
set magic = /usr/bin/env python

{{

###########################################################
# Toy Parser Generator generated by TPG                   #
# TPG (c) Christophe Delord - 2001-2002                   #
#                                                         #
# For further information about TPG, please visit         #
# http://christophe.delord.free.fr                        #
# or contact the author at                                #
# mailto:christophe.delord@free.fr                        #
#                                                         #
# Feel free to contact the author for any request.        #
#                                                         #
# Happy TPG'ing                                           #
#                                                         #
# Christophe Delord.                                      #
#                                                         #
###########################################################

#<import>
from __future__ import generators
import re
#</import>

__date__ = "27 march 2002"
__version__ = "0.1.7"
__author__ = "Christophe Delord <christophe.delord@free.fr>"

__all__ = ["ToyParser", "TPParser", "Node"]

###########################################################
# History                                                 #
# #######                                                 #
#                                                         #
# v 0.1.7 - 27/03/2002                                    #
#         - Some code rewriting                           #
#         - Bug fix : when an error occurs, no empty file #
#             is created                                  #
#                                                         #
# v 0.1.6 - 13/03/2002                                    #
#         - Bug fixes                                     #
#           * Remove backtracking in some regexp and use  #
#             now re (sre) instead of pre (thanks to      #
#             Fredrik Lundh) and speed improvement (thanks#
#             to Nick Mathewson)                          #
#                                                         #
# v 0.1.5 - 07/02/2002                                    #
#         - Some changes                                  #
#           * changed command line parsing (do not use    #
#             TPG anymore)                                #
#                                                         #
# v 0.1.4 - 20/01/2002                                    #
#         - Some changes                                  #
#           * changed unindent function                   #
#           * command line is now parsed by TPG           #
#                                                         #
# v 0.1.3 - 16/01/2002                                    #
#         - Some changes                                  #
#           * added __all__ definition                    #
#           * changed runtime option behaviour            #
#           * changed way to add the runtime (#<> tags)   #
#           * changed genCode/genRetVal into genLValue    #
#             and genRValue                               #
#           * string built by joining lists instead       #
#             step to step concatening strings (faster)   #
#         - Bug fixes                                     #
#           * begin mark code fixed (missing '=')         #
#                                                         #
# v 0.1.2 - 09/01/2002                                    #
#         - New features                                  #
#           * distinction between lexical and syntactic   #
#             rules                                       #
#           * mark definition and text extraction         #
#         - Bug fix                                       #
#           * code now delimited by { {...} } (otherwise  #
#             symbol < <code> > was recognise as symbol   #
#             with <code> as attribute                    #
#                                                         #
# v 0.1.1 - Some bug fixes                                #
#             a b was recognised as if b was a param of a #
#                                                         #
# v 0.1 - Initial version                                 #
#                                                         #
###########################################################

# TODO: TagParser n'accepte pas les lignes ne contenant que du commentaire dans un tag ( '[^#]...' )

###########################################################
#
# Programming rules and conventions
# #################################
#
# The grammar is stored in an AST. Each node has to follow
# these rules :
#
# * genCode(self, indent, X, Y, lex)
#       indent : indentation level (in number of tabs)
#       X, Y : position marks before and after parsing
#       lex : indicates if the context is lexical or syntactic
# * prec is the precedance of the node (for display purpose)
# * eater indicates if the node may eat some terminals
# * verb(self) returns a string representing the piece of rule
#
# Nodes representing values have two more methods :
# * genLValue : code in left position (assignable)
# * genRValue : code in right position (evaluable)
#
# Code is generated as a list (possibly nested). One line
# per item. The final string is only created by the last
# genCode in Parsers class.
#
###########################################################

import sys
import string

#<Node>
class Node(list):
	""" Base class for AST nodes

	An AST is a list. It can be seen as a term: the class name is the functor
	and the items are the arguments.

	Reserved method names :
		init : __init__ customisation
	Reserved attribute names :
		line : line of the current token in the input stream
		env  : pointer to the parser object containing global variables (global for nodes)
	"""
	def __init__(self, line, env, *args):
		""" Initialises the node and calls init with args """
		list.__init__(self)
		self.line = line
		self.env = env
		self += args
		self.init(*args)
	def init(self, *args):
		""" Default initialiser """
		pass
	def __str__(self):
		""" Prints the term """
		return "%s(%s)"%(self.__class__.__name__,','.join(map(str,self)))
#</Node>

#<ToyParser>
class ToyParser:
	""" Base class for all Toy Parsers

	Reserved method and attribute names :
		init
		setInput
		line
		error
		check
		Parse
		tgp_*
	Reserved local variable names (in methods) :
		tpg_*
	"""

	class tpg_Error:
		""" Syntax error exception """
		def __init__(self, line):
			self.line = line
		def __str__(self):
			return '%d: Syntax error'%self.line

	class tpg_Pos:
		""" Position mark. Used to store the current position of the parser """
		def __init__(self, pos=0, line=1):
			self.pos = pos
			self.line = line

	def __init__(self, *args):
		""" Initialises the parser and calls the (redefined) initialiser """
		self.tpg_regexps = {}
		self.init(*args)

	def init(self):
		""" Default initialiser """
		pass

	def setInput(self, input):
		""" Stores the string to be parsed """
		self.tpg_input = input
		self.line= 0

	def error(self, p):
		""" Raises a syntax error """
		raise self.tpg_Error(p.line)

	def tpg_eat(self, p0, regexp, split=0):
		""" Lexical scanner for syntactic rules: skip* lex_eat """
		p1, = self.tpg_lex_skip(p0)
		return self.tpg_lex_eat(p1, regexp, split)

	def tpg_lex_skip(self, p0):
		""" Lexical scanner for separators: skip* """
		try:
			skip = self.skip		# Retrieve the skip symbol if any
		except AttributeError:
			return p0,				# if none, stop scanning
		while 1:
			try:
				p1, = skip(p0)		# Scan skip symbol as many times as possible
				p0 = p1
			except self.tpg_Error:
				p1 = p0
				break
		return p1,

	def tpg_lex_eat(self, p0, regexp, split=0):
		""" Lexical scanner for lexical rules. Tries to parse a given regular expression. """
		try:
			r = self.tpg_regexps[regexp]	# Retrieve the corresponding regexp
		except KeyError:
			r = re.compile(regexp)			# or make it if necessary
			self.tpg_regexps[regexp] = r
		token = r.match(self.tpg_input, p0.pos)		# match the input ?
		if token:
			self.line = p0.line+self.tpg_input.count('\n', p0.pos, token.end())
			p1 = self.tpg_Pos(token.end(), self.line)	# store new position
			if split == 0: return p1,					# and return nothing ('re')
			if split == 1: return p1, token.group()		# or the whole text ('re'/x)
			if split == 2: return p1, token.groups()	# or all items ('re'/<x,y,z>)
		return self.error(p0)				# bad token => raise error to backtrack

	def check(self, cond):
		""" Check a condition and raise an parse error if false """
		if not cond: raise self.tpg_Error(self.line)

	def Parse(self, symbol, input, *args):
		""" Parse the string input starting from symbol """
		self.setInput(input)
		return getattr(self,symbol)(self.tpg_Pos(),*args)[1]
#</ToyParser>

def flatten(L):
	for i in L:
		if type(i) == list:
			for j in flatten(i):
				yield j
		else:
			yield i

emptyLine = re.compile(r'\s*$')
startSpaces = re.compile(r'\s*')

def unindent(lines):
	""" Remove indentation in lines that is common to each line """
	def non_blank(l):
		for c in l:
			if c not in ' \t': return 1
	def tabs(l):
		t = 0
		for c in l:
			if c not in ' \t': break
			t += 1
		return t
	t = min([tabs(l) for l in lines if non_blank(l)])
	return [line[t:] for line in lines]

def reindent(indent, lines):
	""" Reindent all lines """
	tab = '\t'*indent
	return	[tab + line for line in lines]

def if_(cond, true, false):
	if cond:
		return true
	else:
		return false

class Parsers(Node):
	""" Node for the whole file. It contains options, parsers and codes """
	def init(self, options):
		self.options = options
	def genCode(self, indent=0):
		""" Generate the code for each parser """
		return "\n".join(flatten([[parser.genCode(indent) for parser in self], [""]]))

TPG_Warning = """
#........[ TOY PARSER GENERATOR  v %s ]................!
#                                                        ! !
# Warning: This file was automatically generated by TPG ! | !
# Do not edit this file unless you know what you do.   !  |  !
#                                                     !   @   !
#....................................................!!!!!!!!!!!
#
# For further information about TPG you can visit
# http://christophe.delord.free.fr/tpg

"""%__version__

class Options(Node):
	""" Node for the options """
	def init(self):
		""" Initialise default options """
		self.options = {'runtime':None, 'magic':None}
	def set(self, opt, val):
		""" Set or replace an option """
		self.options[opt] = val
		""" Get an option (None if not existing) """
	def get(self, opt):
		try:
			return self.options[opt]
		except KeyError:
			return None
	def genCode(self, indent):
		""" Generate the code depending on options """
		code = []
		# Magic option: the first line is #!...
		magic = self.get('magic')
		if magic:
			code = [magic]
		# This warning is not an option but is placed at the beginning
		code = [ code, TPG_Warning.splitlines() ]
		# Runtime option: extract runtime tags from TPG source
		if self.get('runtime'):
			f = open(__file__, 'r')
			tagParser = TagParser()
			try:
				tags = tagParser(f.read())
			except tagParser.tpg_Error:
				raise "Invalid tags in %s (report this to the author)"%__file__
			f.close()
			try:
				code = [code, map(tags.getTag, ('import', 'Node', 'ToyParser'))]
			except KeyError:
				raise "Invalid tags in %s (report this to the author)"%__file__
		return reindent(indent, flatten(code))

class Parser(Node):
	""" Node for one parser. It contains rules and codes """
	def init(self, id, ids):
		""" Initialise parser name and ancestors """
		self.parserName = id
		self.parserBase = ids
		if _v>=1: print "parser %s(%s):"%(id.name,', '.join([i.name for i in ids]))
	def header(self, indent):
		""" Generate the class definition line (class ... :) """
		name = self.parserName.genLValue()
		toyParser = ToyParser.__name__
		base = self.parserBase.genLValue()
		return reindent(indent, ["class %s(%s, %s):"%(name,toyParser,base)])
	def genCode(self, indent):
		""" Generate the code of the parser (rules and codes) """
		self.items = self[2:]
		return [self.header(indent), [item.genCode(indent+1) for item in self.items]]

class Code(Node):
	""" Node for codes (in main, parser or rule sections) """
	def init(self, c):
		""" Initialise and unindent the code """
		self.code = unindent(c.splitlines())
	def genCode(self, indent, X=None, Y=None, lex=None):
		""" Generate the code (indentation) """
		tab = "\t"*indent
		return	[	reindent(indent, self.code),
					if_(X!=Y,tab+"%s = %s"%(Y,X),[]),
				]
	def verb(self):
		""" Return a string for verbose display """
		return ""
	prec = 1
	eater = 0

class Rule(Node):
	""" Node for grammar rules """
	def init(self, islex, symbol, expr):
		""" Initialise the rule """
		self.lex = if_(islex, 'lex_', '')
		self.s = symbol
		self.e = expr
		if _v>=2: print self.verb()
	def verb(self):
		""" Return a string for verbose display """
		return if_(self.lex,'lex ','')+"%s -> %s ."%(self.s.verb(), self.e.verb())
	def genCode(self, indent):
		""" Generate the code of the rule """
		self.env.initVar()
		X, Y = self.env.newVar(2)
		if self.s.getName() == 'START':		# START is the axiom => the class is callable
			tab = "\t"*indent
			axiom =	[	tab		+"def __call__(self, input, *args):",
						tab	+"\t"	+'""" Call the axiom of the grammar (the START symbol) """',
						tab	+"\t"	+"self.setInput(input)",
						tab	+"\t"	+"return self.START(self.tpg_Pos(),*args)[1]",
						"",
					]
		else:
			axiom = []
		doc = "\t"*(indent+1)+'"""%s"""'%self.verb()
		return	[	axiom,
					self.s.genDef(indent,X,Y),
						doc,
						self.e.genCode(indent+1,X,Y,self.lex),
						self.s.genRet(indent+1,X,Y),
				]

class Ident(Node):
	""" Node for identifiers """
	def init(self, id):
		""" Initialise the identifier """
		self.name = id
	def verb(self):
		""" Return a string for verbose display """
		return self.name
	def getSplit(self):
		""" Tell the scanner how to split tokens:
			1 = get the whole string
		"""
		return 1
	def genLValue(self):
		""" Generate code in left (assignable) position """
		return self.name
	def genRValue(self):
		""" Generate code in right (evaluable) position """
		return self.name

class Idents(Node):
	""" Node for identifier lists """
	def getSplit(self):
		""" Tell the scanner how to split tokens:
			0 = get nothing
			2 = get pieces of string
		"""
		if len(self)==0:
			return 0
		else:
			return 2
	def genLValue(self):
		""" Generate code in left (assignable) position """
		if len(self)==0:
			return ""
		else:
			return "(%s,)"%','.join([a.genLValue() for a in self])
	def genRValue(self):
		""" Generate code in right (evaluable) position """
		return ",".join([a.genRValue() for a in self])

class Ast(Node):
	""" Node for abstract syntax trees """
	def init(self, id, args):
		""" Initialise the AST """
		self.functor, self.args = id, args
	def genRValue(self):
		""" Generate code in right (evaluable) position """
		return "%s(self.line, self, %s)"%(self.functor.genRValue(), ', '.join([a.genRValue() for a in self.args]))

class Args(Node):
	""" Node for argument lists """
	pass

class Tuple(Node):
	""" Node for tuples """
	def genLValue(self):
		""" Generate code in left (assignable) position """
		return "(%s,)"%(', '.join([a.genLValue() for a in self]))
	def genRValue(self):
		""" Generate code in right (evaluable) position """
		return "(%s,)"%(', '.join([a.genRValue() for a in self]))

class Extract(Node):
	""" Node for text extraction """
	def init(self, start, end):
		""" Initialise extract zone """
		self.start, self.end = start.name, end.name
	def genRValue(self):
		""" Generate code in right (evaluable) position """
		return "self.tpg_input[%s.pos:%s.pos]"%(self.start, self.end)

class MakeAST(Node):
	""" Node for AST assignment """
	def init(self, id, ast):
		""" Initialise the AST assignment """
		self.var, self.ast = id, ast
	def genCode(self, indent, X, Y, lex):
		""" Generate the assignment code """
		tab = "\t"*indent
		return	[	tab+"%s = %s"%(self.var.genLValue(),self.ast.genRValue()),
					if_(X!=Y,tab+"%s = %s"%(Y,X),[]),
				]
	def verb(self):
		""" Return a string for verbose display """
		return ""
	prec = 1
	eater = 0

class AddAST(Node):
	""" Node for AST update """
	def init(self, id, ast):
		""" Initialise the AST update """
		self.var, self.ast = id, ast
	def genCode(self, indent, X, Y, lex):
		""" Generate the update code """
		tab = "\t"*indent
		return	[	tab+"%s.append(%s)"%(self.var.genLValue(),self.ast.genRValue()),
					if_(X!=Y,tab+"%s = %s"%(Y,X),[]),
				]
	def verb(self):
		""" Return a string for verbose display """
		return ""
	prec = 1
	eater = 0

class Mark(Node):
	""" Node for text bloc marks """
	def init(self, id):
		""" Initialise the position mark """
		self.var = id
	def verb(self):
		""" Return a string for verbose display """
		return ""
	def genCode(self, indent, X, Y, lex):
		""" Generate mark code """
		return "\t"*indent+"%s = %s"%(self.var.genLValue(), Y)
	prec = 1
	eater = 0

class BeginMark(Mark):
	""" Node for text bloc marks (begin mark)"""
	def verb(self):
		""" Return a string for verbose display """
		return ""
	def genCode(self, indent, X, Y, lex):
		""" Generate mark code """
		tab = "\t"*indent
		return	[	tab+	if_(lex, "%s = %s"%(Y, X), "%s, = self.tpg_lex_skip(%s)"%(Y, X)),
					tab+	"%s = %s"%(self.var.genLValue(), Y),
				]
	eater = 1	# pour skip* dans les r�gles syntaxiques

class EndMark(Mark):
	""" Node for text bloc marks (end mark)"""
	pass

def escape(st, chars):
	""" Escape chars in st """
	s = []
	for c in st:
		if c in chars:
			s.append('\\'+c)
		else:
			s.append(c)
	return ''.join(s)

class Re(Node):
	""" Node for non terminal symbols (regular expressions) """
	def init(self, s, val):
		""" Initialise the regular expression """
		self.re, self.ret = escape(s,"'"), val
	def genCode(self, indent, X, Y, lex):
		""" Generate lexical scanner call """
		return "\t"*indent + "%s, %s = self.tpg_%seat(%s, r'%s', %s)"%(Y, self.ret.genLValue(), lex, X, self.re, self.ret.getSplit())
	def verb(self):
		""" Return a string for verbose display """
		return "'%s'"%self.re
	prec = 1
	eater = 1

class Symbol(Node):
	""" Node for terminal symbols """
	def init(self, id, args, values):
		""" Initialise the symbol """
		self.name, self.params, self.ret = id, args, values
	def getName(self):
		""" Return the name of the symbol """
		return self.name.genLValue()
	def genDef(self, indent, X, Y):
		""" Generate the method definition """
		return "\t"*indent + "def %s(self, %s, %s):"%(self.name.genRValue(), X, ', '.join([a.genLValue() for a in self.params]))
	def genCode(self, indent, X, Y, lex):
		""" Generate the code for parsing the symbol """
		tab = "\t"*indent
		if not lex and self.env.isLex(self.name.name):
			Z = self.env.newVar()
			skip = tab + "%s, = self.tpg_lex_skip(%s)"%(Z, X)
			X = Z
		else:
			skip = []
		return	[	skip,
					tab + "%s, %s = self.%s(%s, %s)"%(Y, self.ret.genLValue(), self.name.genRValue(), X,', '.join([a.genRValue() for a in self.params])),
				]
	def genRet(self, indent, X, Y):
		""" Generate the return statement of the symbol """
		return "\t"*indent + "return %s, %s"%(Y, self.ret.genRValue())
	def verb(self):
		""" Return a string for verbose display """
		return self.name.verb()
	prec = 1
	eater = 1

class Alt(Node):
	""" Node for choice points """
	def init(self, a, b):
		""" Initialise choice point """
		self.a = a
		self.b = b
	def genCode(self, indent, X, Y, lex):
		""" Generate choice point code """
		tab = "\t"*indent
		return	[	tab+"try:",
						self.a.genCode(indent+1,X,Y,lex),
					tab+"except self.tpg_Error:",
						self.b.genCode(indent+1,X,Y,lex),
				]
	def verb(self):
		""" Return a string for verbose display """
		return ' | '.join([i.verb() for i in self])
	prec = 0
	eater = 1

class Seq(Node):
	""" Node for sequences """
	def genCode(self, indent, X, Y, lex):
		""" Generate sequence code """
		code = ""
		L = []
		n, last = 0, None
		for item in self:
			if item.eater:
				Z = self.env.newVar()	# creates a new postion mark for eater items
				L.append([item,X,Z])	# stores start and end mark
				X = Z
				last = n				# this is the last eater item
			else:
				L.append([item,X,X])	# non eater items don't consume marks
			n += 1
		if last is not None:
			L[last][2] = Y									# items after the last eater item
			for item in L[last+1:]: item[1] = item[2] = Y	# end parsing at Y mark
		code = [ item.genCode(indent,Xi,Yi,lex) for item, Xi, Yi in L ]
		if last is None: code.append("\t"*indent + "%s = %s"%(Y,X))	# in empty sequence, links Y to X
		return code
	def verb(self):
		""" Return a string for verbose display """
		def v(i):
			return if_(i.prec<self.prec, "( %s )", "%s")%i.verb()
		return ' '.join(filter(None,map(v, self)))
	prec = 1
	eater = 1

class Rep(Node):
	""" Node for repetition operator """
	def init(self, min, max, expr):
		""" Initialise the repetition """
		self.m, self.M, self.a = min, max, expr
		m, M = self.m, self.M
		if M!=None:
			self.env.check(m<=M and (m,M)!=(0,0))
	def genCode(self, indent, X, Y, lex):
		""" Generate repetition code """
		tab = "\t"*indent
		m, M = self.m, self.M
		if (m, M) == (0, 1):		# ?
			return	[	tab+"try:",
							self.a.genCode(indent+1,X,Y,lex),
						tab+"except self.tpg_Error:",
						tab+"\t"+	"%s = %s"%(Y,X),
					]
		elif (m, M) == (0, None):	# *
			return 	[	tab+"while 1:",
						tab+"\t"+	"try:",
										self.a.genCode(indent+2,X,Y,lex),
						tab+"\t\t"+		"%s = %s"%(X,Y),
						tab+"\t"+	"except self.tpg_Error:",
						tab+"\t\t"+		"%s = %s"%(Y,X),
						tab+"\t\t"+		"break",
					]
		else:						# + and other loops
			n = self.env.newCount()
			X1 = self.env.newVar()
			return	[	tab+"%s = 0"%n,
						tab+"%s = %s"%(X1,X),
						tab+"while "+if_(self.M==None,"1","%s < %s"%(n,self.M))+":",
						tab+"\t"+	"try:",
										self.a.genCode(indent+2,X1,Y,lex),
						tab+"\t\t"+		"%s += 1"%n,
						tab+"\t\t"+		"%s = %s"%(X1,Y),
						tab+"\t"+	"except self.tpg_Error:",
						tab+"\t\t"		"self.check(%s>=%s)"%(n,self.m),
						tab+"\t\t"+		"%s = %s"%(Y,X1),
						tab+"\t\t"+		"break",
					]
	def verb(self):
		""" Return a string for verbose display """
		m, M = self.m, self.M
		if (m, M) == (0, 1): r = '?'
		elif (m, M) == (0, None): r = '*'
		elif (m, M) == (1, None): r = '+'
		elif m == M: r = "{%s}"%m
		else: r = "{%s,%s}"%(if_(m,m,''),if_(M,M,''))
		return "( %s )%s"%(self.a.verb(),r)
	prec = 1
	eater = 1

}}

parser TPParser:

{{

	""" Parser for Toy Parser Grammars
	"""

	def init(self):
		""" Initialise parser
		"""
		self.lexs = {}	# Lexical rule names

	def initVar(self):
		""" Reinitialise TPG variable counters """
		self.nextVar = 0
		self.nextCount = 0

	def newVar(self, n=1):
		""" Generate a new position variable """
		if n>1:
			return [self.newVar() for i in xrange(n)]
		else:
			p = "tpg_p%s"%self.nextVar
			self.nextVar += 1
			return p

	def newCount(self):
		""" Generate a new counter variable """
		n = "tpg_n%s"%self.nextCount
		self.nextCount += 1
		return n

	def setLex(self, name):
		""" Register a lexical rule name """
		self.lexs[name] = 1

	def isLex(self, name):
		""" Return the lexical flag of a symbol """
		return self.lexs.has_key(name)

}}

START/code -> PARSER/parsers {{ code=parsers.genCode() }} .

PARSER/parsers ->
	OPTIONS/opts
	parsers = Parsers<opts>
	( CODE/c parsers-c )*
	(	'parser' IDENT/id
		( '\(' IDENTS/ids '\)' | ids = Idents<> )
		':'
		parser = Parser<id,ids>
		(	CODE/c parser-c
		|	RULE/r parser-r
		)*
		parsers-parser
	|	'main' ':'
		( CODE/c parsers-c )*
	)*
	'$'
	.

OPTIONS/opts ->
	opts = Options<>
	(	'set'
		(	'(no)?(runtime)'/<no,opt>		{{ opts.set(opt,not no) }}
				# L'option runtime permet d'inclure les classes Node et ToyParser
				# dans le code g�n�r�. Elle est d�sactiv�e par d�faut.
		|	'no(magic)'/<opt>				{{ opts.set(opt,None) }}
				# Par d�faut TPG n'ins�re pas de ligne #!
		|	'magic'/opt '=' '.*'/magic		{{ opts.set(opt,"#!%s\n"%magic) }}
				# Ajout d'une ligne #!magic au d�but de l'analyseur g�n�r�
		)
	)*
	.

lex skip ->
	'\s+'
|	'#.*'
|	'//.*'
|	'\/\*' ccomment '\*\/'
.

lex ccomment ->
	(	'\/\*' ccomment '\*\/'
	|	'\*[^\/]'
	|	'[^\*]'
	)*
.

CODE/Code<c> -> '{{((?:}?[^}]+)*)}}'/<c> .

IDENT/Ident<id> -> '\w+'/id .

IDENTS/ids -> ids=Idents<> IDENT/id ids-id ( ',' IDENT/id ids-id )* .

RULE/Rule<lex,s,e> ->
	(	'lex' lex=1 DEF_SYMBOL/s {{ self.setLex(s.name.name) }}
	|	lex=0 DEF_SYMBOL/s {{ self.check(s.name.name!='skip') }}
	)
	'->' EXPR/e '\.'
	.

# Definition of a symbol

DEF_SYMBOL/Symbol<id,args,values> ->
	IDENT/id
	DEF_ARGS<id>/args
	DEF_VALUES<id>/values
	.

DEF_ARGS<id>/args ->
	{{ self.check(id.name!='skip') }}
	'<' IDENTS/args '>'
|	args = Idents<>
.

DEF_VALUES<id>/values ->
	{{ self.check(id.name!='skip') }}
	'/'
	DEF_RET/values
|	values = Idents<>
.

DEF_RET/values ->
	'<' DEF_TUPLE/values '>'
|	DEF_AST/values
|	IDENT/start '\.\.' IDENT/end values=Extract<start,end>
|	IDENT/values
.

DEF_TUPLE/t -> t=Tuple<> DEF_RET/c t-c ( ',' DEF_RET/c t-c )* .

DEF_AST/Ast<id,args> -> IDENT/id '<' DEF_ASTS/args '>' .
DEF_ASTS/args -> args=Args<> ( DEF_AST_IT/a args-a ( ',' DEF_AST_IT/a args-a )* )? .
DEF_AST_IT/ast -> DEF_RET/ast .

# Definition of a regular expression call

RE/Re<s,val> -> string/s RE_VALUES/val .

string/s -> '"([^"]*)"'/<s> | "'([^']*)'"/<s> .

RE_VALUES/val ->
	'/'
	(	IDENT/val
	|	'<' IDENTS/val '>'
	)
|	val = Idents<>
.

# Definition of a symbol call

SYMBOL/Symbol<id,args,values> ->
	IDENT/id {{ self.check(id.name!='skip') }}
	ARGS/args
	VALUES/values
	.

ARGS/args -> '<' DEF_TUPLE/args '>' | args = Idents<> .

VALUES/values -> '/' RET/values | values = Idents<> .

RET/values -> '<' TUPLE/values '>' | IDENT/values .

TUPLE/t -> t=Tuple<> RET/c t-c ( ',' RET/c t-c )* .

# Definition of a grammar expression

EXPR/e -> TERM/e ( '\|' TERM/t e=Alt<e,t> )* .

TERM/t -> t=Seq<> ( FACT/f t-f )* .

FACT/f ->
	RET/id
	(	'=' DEF_RET/ast f=MakeAST<id,ast>
	|	'-' DEF_RET/ast f=AddAST<id,ast>
	)
|	'!<' IDENT/id f=BeginMark<id>
|	'!>' IDENT/id f=EndMark<id>
|	'!'  IDENT/id f=Mark<id>
|	CODE/f
|	ATOM/f REP<f>/f
.

REP<f>/f ->
	(	'\?'										f=Rep<0,1,f>
	|	'\*'										f=Rep<0,None,f>
	|	'\+'										f=Rep<1,None,f>
	|	'\{' nb<0>/m ( ',' nb<None>/M | M=m ) '\}'	f=Rep<m,M,f>
	)?
	.

nb<default>/n -> '\d+'/s {{ n=string.atoi(s) }} | n = default .

ATOM/a ->
	SYMBOL/a
|	RE/a
|	'\(' EXPR/a '\)'
.

main:

{{

class Tags(Node):
	""" Node for runtime tags """
	def init(self):
		""" Initialise tags """
		self.data = {}
	def append(self, tag):
		""" Add a new tag """
		name, text = tag
		self.data[name] = [unindent(text), []]
	def getTag(self, tag):
		""" Return a tag """
		return self.data[tag]

}}

parser TagParser:

{{
	""" Parse TPG source to extract runtime tags """
}}

	lex START/tags ->
		tags = Tags<>
		(	'\s*#\s*<([^>\n]*)>.*\n'/<name>
			code = Node<>
			( '(\s*[^#].*)\n'/<l> code-l )*
			'\s*#\s*<\s*/([^>\n]*)>.*\n'/<endname>
			{{ name, endname = name.strip(), endname.strip() }}
			{{ self.check(name==endname) }}
			tags-<name,code>
		|	'.*\n'
		)*
		'$'
		.

main:

{{

_v = 0	# verbosity is 0 if imported as a module

if __name__ == "__main__":

	class ArgError: pass

	def getargs(args):
		def check(cond):
			if not cond: raise ArgError
		i, o, v = None, None, 0
		while args:
			arg, args = args[0], args[1:]
			if arg == '-o':
				check(o is None and len(args)>0 and args[0].endswith('.py'))
				o, args = args[0], args[1:]
			elif re.match('-v+$',arg):
				v += len(arg)-1
			else:
				check(i is None and arg.endswith('.g'))
				i = arg
		check(i is not None)
		if o is None: o = i[:-2]+".py"
		return i, o, v

	__file__ = sys.argv[0]
	print "TPG v%s (c) Christophe Delord"%__version__
	try:
		(grammar_file, output_file, _v) = getargs(sys.argv[1:])
	except ArgError:
		sys.stderr.write("Syntax: %s [-v|vv] grammar_file.g [-o output_file.py]\n"%__file__)
	else:
		print "TPG: translating %s to %s"%(grammar_file,output_file)
		f = open(grammar_file, 'r')
		parser = TPParser()(f.read())
		f.close()
		g = open(output_file, 'w')
		g.write(parser)
		g.close()
		print "Translation OK"

}}

