#!/usr/bin/env python


#........[ TOY PARSER GENERATOR  v 0.1.5 ]................!
#                                                        ! !
# Warning: This file was automatically generated by TPG ! | !
# Do not edit this file unless you know what you do.   !  |  !
#                                                     !   @   !
#....................................................!!!!!!!!!!!
#
# For further information about TPG you can visit
# http://christophe.delord.free.fr/tpg



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
import pre
#</import>

__date__ = "7 february 2002"
__version__ = "0.1.5"
__author__ = "Christophe Delord <christophe.delord@free.fr>"

__all__ = ["ToyParser", "TPParser", "Node"]

###########################################################
# History                                                 #
# #######                                                 #
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

# Bug in sre:
#	when regexp = "<<.*?>>" and string is "<< a big string >>"
#	=> RuntimeError: maximum recursion limit exceeded
# this works fine with pre

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
		apply(self.init,args)
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
		apply(self.init,args)

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
			r = pre.compile(regexp)			# or make it if necessary
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
		return apply(getattr(self,symbol), [self.tpg_Pos()]+list(args))[1]
#</ToyParser>

def flatten(L):
	for i in L:
		if type(i) == list:
			for j in flatten(i):
				yield j
		else:
			yield i

emptyLine = pre.compile(r'\s*$')
startSpaces = pre.compile(r'\s*')

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
						tab	+"\t"	+"return apply(self.START, [self.tpg_Pos()]+list(args))[1]",
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

class TPParser(ToyParser, ):
	
	
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
	
	def __call__(self, input, *args):
		""" Call the axiom of the grammar (the START symbol) """
		self.setInput(input)
		return apply(self.START, [self.tpg_Pos()]+list(args))[1]

	def START(self, tpg_p0, ):
		"""START -> PARSER ."""
		tpg_p1, parsers = self.PARSER(tpg_p0, )
		code=parsers.genCode() 
		return tpg_p1, code
	def PARSER(self, tpg_p0, ):
		"""PARSER -> OPTIONS ( CODE )* ( 'parser' IDENT ( '\(' IDENTS '\)' |  ) ':' ( CODE | RULE )* | 'main' ':' ( CODE )* )* '$' ."""
		tpg_p2, opts = self.OPTIONS(tpg_p0, )
		parsers = Parsers(self.line, self, opts)
		while 1:
			try:
				tpg_p3, c = self.CODE(tpg_p2, )
				parsers.append(c)
				tpg_p2 = tpg_p3
			except self.tpg_Error:
				tpg_p3 = tpg_p2
				break
		while 1:
			try:
				try:
					tpg_p7,  = self.tpg_eat(tpg_p3, r'parser', 0)
					tpg_p8, id = self.IDENT(tpg_p7, )
					try:
						tpg_p12,  = self.tpg_eat(tpg_p8, r'\(', 0)
						tpg_p13, ids = self.IDENTS(tpg_p12, )
						tpg_p9,  = self.tpg_eat(tpg_p13, r'\)', 0)
					except self.tpg_Error:
						ids = Idents(self.line, self, )
						tpg_p9 = tpg_p8
					tpg_p10,  = self.tpg_eat(tpg_p9, r':', 0)
					parser = Parser(self.line, self, id, ids)
					while 1:
						try:
							try:
								tpg_p4, c = self.CODE(tpg_p10, )
								parser.append(c)
							except self.tpg_Error:
								tpg_p4, r = self.RULE(tpg_p10, )
								parser.append(r)
							tpg_p10 = tpg_p4
						except self.tpg_Error:
							tpg_p4 = tpg_p10
							break
					parsers.append(parser)
				except self.tpg_Error:
					tpg_p17,  = self.tpg_eat(tpg_p3, r'main', 0)
					tpg_p18,  = self.tpg_eat(tpg_p17, r':', 0)
					while 1:
						try:
							tpg_p4, c = self.CODE(tpg_p18, )
							parsers.append(c)
							tpg_p18 = tpg_p4
						except self.tpg_Error:
							tpg_p4 = tpg_p18
							break
				tpg_p3 = tpg_p4
			except self.tpg_Error:
				tpg_p4 = tpg_p3
				break
		tpg_p1,  = self.tpg_eat(tpg_p4, r'$', 0)
		return tpg_p1, parsers
	def OPTIONS(self, tpg_p0, ):
		"""OPTIONS -> ( 'set' ( '(no)?(runtime)' | 'no(magic)' | 'magic' '=' '.*' ) )* ."""
		opts = Options(self.line, self, )
		while 1:
			try:
				tpg_p3,  = self.tpg_eat(tpg_p0, r'set', 0)
				try:
					try:
						tpg_p1, (no,opt,) = self.tpg_eat(tpg_p3, r'(no)?(runtime)', 2)
						opts.set(opt,not no) 
					except self.tpg_Error:
						tpg_p1, (opt,) = self.tpg_eat(tpg_p3, r'no(magic)', 2)
						opts.set(opt,None) 
				except self.tpg_Error:
					tpg_p7, opt = self.tpg_eat(tpg_p3, r'magic', 1)
					tpg_p8,  = self.tpg_eat(tpg_p7, r'=', 0)
					tpg_p1, magic = self.tpg_eat(tpg_p8, r'.*', 1)
					opts.set(opt,"#!%s\n"%magic) 
				tpg_p0 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p0
				break
		return tpg_p1, opts
	def skip(self, tpg_p0, ):
		"""lex skip -> '\s+' | '#.*' | '//.*' | '\/\*' ccomment '\*\/' ."""
		try:
			try:
				try:
					tpg_p1,  = self.tpg_lex_eat(tpg_p0, r'\s+', 0)
				except self.tpg_Error:
					tpg_p1,  = self.tpg_lex_eat(tpg_p0, r'#.*', 0)
			except self.tpg_Error:
				tpg_p1,  = self.tpg_lex_eat(tpg_p0, r'//.*', 0)
		except self.tpg_Error:
			tpg_p5,  = self.tpg_lex_eat(tpg_p0, r'\/\*', 0)
			tpg_p6,  = self.ccomment(tpg_p5, )
			tpg_p1,  = self.tpg_lex_eat(tpg_p6, r'\*\/', 0)
		return tpg_p1, 
	def ccomment(self, tpg_p0, ):
		"""lex ccomment -> ( '\/\*' ccomment '\*\/' | '\*[^\/]' | '[^\*]' )* ."""
		while 1:
			try:
				try:
					try:
						tpg_p3,  = self.tpg_lex_eat(tpg_p0, r'\/\*', 0)
						tpg_p4,  = self.ccomment(tpg_p3, )
						tpg_p1,  = self.tpg_lex_eat(tpg_p4, r'\*\/', 0)
					except self.tpg_Error:
						tpg_p1,  = self.tpg_lex_eat(tpg_p0, r'\*[^\/]', 0)
				except self.tpg_Error:
					tpg_p1,  = self.tpg_lex_eat(tpg_p0, r'[^\*]', 0)
				tpg_p0 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p0
				break
		return tpg_p1, 
	def CODE(self, tpg_p0, ):
		"""CODE -> '{{((?:.|\n)*?)}}' ."""
		tpg_p1, (c,) = self.tpg_eat(tpg_p0, r'{{((?:.|\n)*?)}}', 2)
		return tpg_p1, Code(self.line, self, c)
	def IDENT(self, tpg_p0, ):
		"""IDENT -> '\w+' ."""
		tpg_p1, id = self.tpg_eat(tpg_p0, r'\w+', 1)
		return tpg_p1, Ident(self.line, self, id)
	def IDENTS(self, tpg_p0, ):
		"""IDENTS -> IDENT ( ',' IDENT )* ."""
		ids = Idents(self.line, self, )
		tpg_p2, id = self.IDENT(tpg_p0, )
		ids.append(id)
		while 1:
			try:
				tpg_p4,  = self.tpg_eat(tpg_p2, r',', 0)
				tpg_p1, id = self.IDENT(tpg_p4, )
				ids.append(id)
				tpg_p2 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p2
				break
		return tpg_p1, ids
	def RULE(self, tpg_p0, ):
		"""RULE -> ( 'lex' DEF_SYMBOL | DEF_SYMBOL ) '->' EXPR '\.' ."""
		try:
			tpg_p6,  = self.tpg_eat(tpg_p0, r'lex', 0)
			lex = 1
			tpg_p2, s = self.DEF_SYMBOL(tpg_p6, )
			self.setLex(s.name.name) 
		except self.tpg_Error:
			lex = 0
			tpg_p2, s = self.DEF_SYMBOL(tpg_p0, )
			self.check(s.name.name!='skip') 
		tpg_p3,  = self.tpg_eat(tpg_p2, r'->', 0)
		tpg_p4, e = self.EXPR(tpg_p3, )
		tpg_p1,  = self.tpg_eat(tpg_p4, r'\.', 0)
		return tpg_p1, Rule(self.line, self, lex, s, e)
	def DEF_SYMBOL(self, tpg_p0, ):
		"""DEF_SYMBOL -> IDENT DEF_ARGS DEF_VALUES ."""
		tpg_p2, id = self.IDENT(tpg_p0, )
		tpg_p3, args = self.DEF_ARGS(tpg_p2, id)
		tpg_p1, values = self.DEF_VALUES(tpg_p3, id)
		return tpg_p1, Symbol(self.line, self, id, args, values)
	def DEF_ARGS(self, tpg_p0, id):
		"""DEF_ARGS -> '<' IDENTS '>' |  ."""
		try:
			self.check(id.name!='skip') 
			tpg_p2,  = self.tpg_eat(tpg_p0, r'<', 0)
			tpg_p3, args = self.IDENTS(tpg_p2, )
			tpg_p1,  = self.tpg_eat(tpg_p3, r'>', 0)
		except self.tpg_Error:
			args = Idents(self.line, self, )
			tpg_p1 = tpg_p0
		return tpg_p1, args
	def DEF_VALUES(self, tpg_p0, id):
		"""DEF_VALUES -> '/' DEF_RET |  ."""
		try:
			self.check(id.name!='skip') 
			tpg_p2,  = self.tpg_eat(tpg_p0, r'/', 0)
			tpg_p1, values = self.DEF_RET(tpg_p2, )
		except self.tpg_Error:
			values = Idents(self.line, self, )
			tpg_p1 = tpg_p0
		return tpg_p1, values
	def DEF_RET(self, tpg_p0, ):
		"""DEF_RET -> '<' DEF_TUPLE '>' | DEF_AST | IDENT '\.\.' IDENT | IDENT ."""
		try:
			try:
				try:
					tpg_p2,  = self.tpg_eat(tpg_p0, r'<', 0)
					tpg_p3, values = self.DEF_TUPLE(tpg_p2, )
					tpg_p1,  = self.tpg_eat(tpg_p3, r'>', 0)
				except self.tpg_Error:
					tpg_p1, values = self.DEF_AST(tpg_p0, )
			except self.tpg_Error:
				tpg_p6, start = self.IDENT(tpg_p0, )
				tpg_p7,  = self.tpg_eat(tpg_p6, r'\.\.', 0)
				tpg_p1, end = self.IDENT(tpg_p7, )
				values = Extract(self.line, self, start, end)
		except self.tpg_Error:
			tpg_p1, values = self.IDENT(tpg_p0, )
		return tpg_p1, values
	def DEF_TUPLE(self, tpg_p0, ):
		"""DEF_TUPLE -> DEF_RET ( ',' DEF_RET )* ."""
		t = Tuple(self.line, self, )
		tpg_p2, c = self.DEF_RET(tpg_p0, )
		t.append(c)
		while 1:
			try:
				tpg_p4,  = self.tpg_eat(tpg_p2, r',', 0)
				tpg_p1, c = self.DEF_RET(tpg_p4, )
				t.append(c)
				tpg_p2 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p2
				break
		return tpg_p1, t
	def DEF_AST(self, tpg_p0, ):
		"""DEF_AST -> IDENT '<' DEF_ASTS '>' ."""
		tpg_p2, id = self.IDENT(tpg_p0, )
		tpg_p3,  = self.tpg_eat(tpg_p2, r'<', 0)
		tpg_p4, args = self.DEF_ASTS(tpg_p3, )
		tpg_p1,  = self.tpg_eat(tpg_p4, r'>', 0)
		return tpg_p1, Ast(self.line, self, id, args)
	def DEF_ASTS(self, tpg_p0, ):
		"""DEF_ASTS -> ( DEF_AST_IT ( ',' DEF_AST_IT )* )? ."""
		args = Args(self.line, self, )
		try:
			tpg_p3, a = self.DEF_AST_IT(tpg_p0, )
			args.append(a)
			while 1:
				try:
					tpg_p5,  = self.tpg_eat(tpg_p3, r',', 0)
					tpg_p1, a = self.DEF_AST_IT(tpg_p5, )
					args.append(a)
					tpg_p3 = tpg_p1
				except self.tpg_Error:
					tpg_p1 = tpg_p3
					break
		except self.tpg_Error:
			tpg_p1 = tpg_p0
		return tpg_p1, args
	def DEF_AST_IT(self, tpg_p0, ):
		"""DEF_AST_IT -> DEF_RET ."""
		tpg_p1, ast = self.DEF_RET(tpg_p0, )
		return tpg_p1, ast
	def RE(self, tpg_p0, ):
		"""RE -> string RE_VALUES ."""
		tpg_p2, s = self.string(tpg_p0, )
		tpg_p1, val = self.RE_VALUES(tpg_p2, )
		return tpg_p1, Re(self.line, self, s, val)
	def string(self, tpg_p0, ):
		"""string -> '"([^"]*)"' | '\'([^\']*)\'' ."""
		try:
			tpg_p1, (s,) = self.tpg_eat(tpg_p0, r'"([^"]*)"', 2)
		except self.tpg_Error:
			tpg_p1, (s,) = self.tpg_eat(tpg_p0, r'\'([^\']*)\'', 2)
		return tpg_p1, s
	def RE_VALUES(self, tpg_p0, ):
		"""RE_VALUES -> '/' ( IDENT | '<' IDENTS '>' ) |  ."""
		try:
			tpg_p2,  = self.tpg_eat(tpg_p0, r'/', 0)
			try:
				tpg_p1, val = self.IDENT(tpg_p2, )
			except self.tpg_Error:
				tpg_p5,  = self.tpg_eat(tpg_p2, r'<', 0)
				tpg_p6, val = self.IDENTS(tpg_p5, )
				tpg_p1,  = self.tpg_eat(tpg_p6, r'>', 0)
		except self.tpg_Error:
			val = Idents(self.line, self, )
			tpg_p1 = tpg_p0
		return tpg_p1, val
	def SYMBOL(self, tpg_p0, ):
		"""SYMBOL -> IDENT ARGS VALUES ."""
		tpg_p2, id = self.IDENT(tpg_p0, )
		self.check(id.name!='skip') 
		tpg_p3, args = self.ARGS(tpg_p2, )
		tpg_p1, values = self.VALUES(tpg_p3, )
		return tpg_p1, Symbol(self.line, self, id, args, values)
	def ARGS(self, tpg_p0, ):
		"""ARGS -> '<' DEF_TUPLE '>' |  ."""
		try:
			tpg_p2,  = self.tpg_eat(tpg_p0, r'<', 0)
			tpg_p3, args = self.DEF_TUPLE(tpg_p2, )
			tpg_p1,  = self.tpg_eat(tpg_p3, r'>', 0)
		except self.tpg_Error:
			args = Idents(self.line, self, )
			tpg_p1 = tpg_p0
		return tpg_p1, args
	def VALUES(self, tpg_p0, ):
		"""VALUES -> '/' RET |  ."""
		try:
			tpg_p2,  = self.tpg_eat(tpg_p0, r'/', 0)
			tpg_p1, values = self.RET(tpg_p2, )
		except self.tpg_Error:
			values = Idents(self.line, self, )
			tpg_p1 = tpg_p0
		return tpg_p1, values
	def RET(self, tpg_p0, ):
		"""RET -> '<' TUPLE '>' | IDENT ."""
		try:
			tpg_p2,  = self.tpg_eat(tpg_p0, r'<', 0)
			tpg_p3, values = self.TUPLE(tpg_p2, )
			tpg_p1,  = self.tpg_eat(tpg_p3, r'>', 0)
		except self.tpg_Error:
			tpg_p1, values = self.IDENT(tpg_p0, )
		return tpg_p1, values
	def TUPLE(self, tpg_p0, ):
		"""TUPLE -> RET ( ',' RET )* ."""
		t = Tuple(self.line, self, )
		tpg_p2, c = self.RET(tpg_p0, )
		t.append(c)
		while 1:
			try:
				tpg_p4,  = self.tpg_eat(tpg_p2, r',', 0)
				tpg_p1, c = self.RET(tpg_p4, )
				t.append(c)
				tpg_p2 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p2
				break
		return tpg_p1, t
	def EXPR(self, tpg_p0, ):
		"""EXPR -> TERM ( '\|' TERM )* ."""
		tpg_p2, e = self.TERM(tpg_p0, )
		while 1:
			try:
				tpg_p4,  = self.tpg_eat(tpg_p2, r'\|', 0)
				tpg_p1, t = self.TERM(tpg_p4, )
				e = Alt(self.line, self, e, t)
				tpg_p2 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p2
				break
		return tpg_p1, e
	def TERM(self, tpg_p0, ):
		"""TERM -> ( FACT )* ."""
		t = Seq(self.line, self, )
		while 1:
			try:
				tpg_p1, f = self.FACT(tpg_p0, )
				t.append(f)
				tpg_p0 = tpg_p1
			except self.tpg_Error:
				tpg_p1 = tpg_p0
				break
		return tpg_p1, t
	def FACT(self, tpg_p0, ):
		"""FACT -> RET ( '=' DEF_RET | '-' DEF_RET ) | '!<' IDENT | '!>' IDENT | '!' IDENT | CODE | ATOM REP ."""
		try:
			try:
				try:
					try:
						try:
							tpg_p2, id = self.RET(tpg_p0, )
							try:
								tpg_p4,  = self.tpg_eat(tpg_p2, r'=', 0)
								tpg_p1, ast = self.DEF_RET(tpg_p4, )
								f = MakeAST(self.line, self, id, ast)
							except self.tpg_Error:
								tpg_p6,  = self.tpg_eat(tpg_p2, r'-', 0)
								tpg_p1, ast = self.DEF_RET(tpg_p6, )
								f = AddAST(self.line, self, id, ast)
						except self.tpg_Error:
							tpg_p8,  = self.tpg_eat(tpg_p0, r'!<', 0)
							tpg_p1, id = self.IDENT(tpg_p8, )
							f = BeginMark(self.line, self, id)
					except self.tpg_Error:
						tpg_p10,  = self.tpg_eat(tpg_p0, r'!>', 0)
						tpg_p1, id = self.IDENT(tpg_p10, )
						f = EndMark(self.line, self, id)
				except self.tpg_Error:
					tpg_p12,  = self.tpg_eat(tpg_p0, r'!', 0)
					tpg_p1, id = self.IDENT(tpg_p12, )
					f = Mark(self.line, self, id)
			except self.tpg_Error:
				tpg_p1, f = self.CODE(tpg_p0, )
		except self.tpg_Error:
			tpg_p15, f = self.ATOM(tpg_p0, )
			tpg_p1, f = self.REP(tpg_p15, f)
		return tpg_p1, f
	def REP(self, tpg_p0, f):
		"""REP -> ( '\?' | '\*' | '\+' | '\{' nb ( ',' nb |  ) '\}' )? ."""
		try:
			try:
				try:
					try:
						tpg_p1,  = self.tpg_eat(tpg_p0, r'\?', 0)
						f = Rep(self.line, self, 0, 1, f)
					except self.tpg_Error:
						tpg_p1,  = self.tpg_eat(tpg_p0, r'\*', 0)
						f = Rep(self.line, self, 0, None, f)
				except self.tpg_Error:
					tpg_p1,  = self.tpg_eat(tpg_p0, r'\+', 0)
					f = Rep(self.line, self, 1, None, f)
			except self.tpg_Error:
				tpg_p6,  = self.tpg_eat(tpg_p0, r'\{', 0)
				tpg_p7, m = self.nb(tpg_p6, 0)
				try:
					tpg_p10,  = self.tpg_eat(tpg_p7, r',', 0)
					tpg_p8, M = self.nb(tpg_p10, None)
				except self.tpg_Error:
					M = m
					tpg_p8 = tpg_p7
				tpg_p1,  = self.tpg_eat(tpg_p8, r'\}', 0)
				f = Rep(self.line, self, m, M, f)
		except self.tpg_Error:
			tpg_p1 = tpg_p0
		return tpg_p1, f
	def nb(self, tpg_p0, default):
		"""nb -> '\d+' |  ."""
		try:
			tpg_p1, s = self.tpg_eat(tpg_p0, r'\d+', 1)
			n=string.atoi(s) 
		except self.tpg_Error:
			n = default
			tpg_p1 = tpg_p0
		return tpg_p1, n
	def ATOM(self, tpg_p0, ):
		"""ATOM -> SYMBOL | RE | '\(' EXPR '\)' ."""
		try:
			try:
				tpg_p1, a = self.SYMBOL(tpg_p0, )
			except self.tpg_Error:
				tpg_p1, a = self.RE(tpg_p0, )
		except self.tpg_Error:
			tpg_p4,  = self.tpg_eat(tpg_p0, r'\(', 0)
			tpg_p5, a = self.EXPR(tpg_p4, )
			tpg_p1,  = self.tpg_eat(tpg_p5, r'\)', 0)
		return tpg_p1, a


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

class TagParser(ToyParser, ):
	
	""" Parse TPG source to extract runtime tags """
	def __call__(self, input, *args):
		""" Call the axiom of the grammar (the START symbol) """
		self.setInput(input)
		return apply(self.START, [self.tpg_Pos()]+list(args))[1]

	def START(self, tpg_p0, ):
		"""lex START -> ( '\s*#\s*<\s*(.*?)\s*>.*\n' ( '(\s*[^#].*)\n' )* '\s*#\s*<\s*/\s*(.*?)\s*>.*\n' | '.*\n' )* '$' ."""
		tags = Tags(self.line, self, )
		while 1:
			try:
				try:
					tpg_p4, (name,) = self.tpg_lex_eat(tpg_p0, r'\s*#\s*<\s*(.*?)\s*>.*\n', 2)
					code = Node(self.line, self, )
					while 1:
						try:
							tpg_p5, (l,) = self.tpg_lex_eat(tpg_p4, r'(\s*[^#].*)\n', 2)
							code.append(l)
							tpg_p4 = tpg_p5
						except self.tpg_Error:
							tpg_p5 = tpg_p4
							break
					tpg_p2, (endname,) = self.tpg_lex_eat(tpg_p5, r'\s*#\s*<\s*/\s*(.*?)\s*>.*\n', 2)
					self.check(name==endname) 
					tags.append((name, code,))
				except self.tpg_Error:
					tpg_p2,  = self.tpg_lex_eat(tpg_p0, r'.*\n', 0)
				tpg_p0 = tpg_p2
			except self.tpg_Error:
				tpg_p2 = tpg_p0
				break
		tpg_p1,  = self.tpg_lex_eat(tpg_p2, r'$', 0)
		return tpg_p1, tags


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
			elif pre.match('-v+$',arg):
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
		g = open(output_file, 'w')
		g.write(TPParser()(f.read()))
		f.close()
		g.close()
		print "Translation OK"

