set noruntime		# the runtime is in the grammar
set magic = "/usr/bin/env python2.2"

{{
#<copyright>
#........[ TOY PARSER GENERATOR ].........................!
#                                                        ! !
# Warning: This file was automatically generated by TPG ! | !
# Do not edit this file unless you know what you do.   !  |  !
#                                                     !   @   !
#....................................................!!!!!!!!!!!
#
# For further information about TPG you can visit
# http://christophe.delord.free.fr/en/tpg
#</copyright>

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

###########################################################
# History                                                 #
# #######                                                 #
#                                                         #
# v 2.0 - 26/05/2002                                      #
#       - First release of TPG 2                          #
#                                                         #
###########################################################

#<import>
from __future__ import generators
import re
#</import>

import tpg

__date__ = "26 may 2002"
__version__ = "2.0"
__author__ = "Christophe Delord <christophe.delord@free.fr>"

def compile(grammar):
	""" Translate a grammar into Python """
	return _TPGParser(grammar)

def flatten(L):
	""" Flatten a list. Each item is yielded """
	for i in L:
		if type(i) == list:
			for j in flatten(i):
				yield j
		else:
			yield i

def reindent(lines, indent):
	""" Reindent a sequence of lines. Remove common tabs and spaces and add indent tabs """
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
	tab = '\t'*indent
	return [tab+line[t:] for line in lines]

def _if(cond, trueval, falseval):
	""" C-ternary operator like """
	if cond: return trueval
	else   : return falseval

class Parsers(list):
	""" List of parsers """

	def __init__(self, opts):
		self.opts = opts

	def add(self, obj):
		""" Add a parser or a code """
		if _v>=1:
			if isinstance(obj, Parser): sys.stdout.write("%s\n"%obj)
		self.append(obj)

	def genCode(self):
		""" Generate code for all parsers """
		code = [
			self.magic(),					# magic line : #!...
			self.runtime(),					# runtime if necessary
			[ p.genCode() for p in self ],	# parsers and codes
		]
		code = "\n".join(flatten(code))
		if self.opts['runtime']:				# if runtime included
			code = code.replace('tpg'+'.',"")	# then remove tpg. prefix
		return code

	def magic(self):
		""" Generate the magic line if provided """
		magic = self.opts['magic']
		return _if(magic,"#!%s"%magic,[])
		
	def runtime(self):
		""" Generate the runtime if necessary """
		if self.opts['runtime']:
			tags = self.getTags(__file__)
			return [
				tags['copyright'],
				tags['import'],
				tags['runtime'],
			]
		else:
			return []

	def getTags(self, file):
		""" Extract TPG tags from the source file """
		tag_pat = re.compile(r"#<(\w+)>(.*)#</\1>",re.S)
		f = open(file)
		code = f.read()
		f.close()
		i = 0
		tags = {}
		while 1:
			tag = tag_pat.search(code,i)
			if not tag: break
			i = tag.end()
			tag, val = tag.group(1,2)
			tags[tag] = val
		return tags

class Options:
	""" Container for TPG options """

	def __init__(self):
		self.opts = {}

	def set(self, opt, val):
		self.opts[opt] = val

	def __getitem__(self, item):
		return self.opts.get(item,None)

class Code:
	""" Container for code sections """

	def __init__(self, code):
		self.code = code

	def __str__(self): return self.code

	def genCode(self, indent=0, vargen=None, p=None):
		return reindent(self.code.splitlines(), indent)

	def collect(self, collector): pass

	def doc(self): return ""

def _2str(st):
	return 'r"%s"'%st

class Collector:
	""" Container for token and rule definitions """

	ident_pat = re.compile(r'^\w+$')	# keyword pattern

	def __init__(self):
		self.inline_tokens = []
		self.tokens = []
		self.token_name = {}	# dict: regexp -> token_name
		self.inline_number = 0
		self.rules = []
		self.knowntokens = {}

	def add_inline_token(self, tok):
		""" Add an inline token """
		regexp = tok.expr
		try:
			name = self.token_name[regexp]			# this token has already been stored
		except KeyError:							# if not
			if self.ident_pat.match(regexp):		#	if it is a keyword
				name = regexp						#		the name is the regexp
			else:									#	otherwise
				self.inline_number += 1				#		make a new token name
				name = "_tok_%s"%self.inline_number	#
			self.token_name[regexp] = name			# store the new token name
			self.inline_tokens.append(tok)			# and the new token definition

	def add_token(self, tok):
		""" Add a predefined token """
		self.tokens.append(tok)					# definition
		self.token_name[tok.expr] = tok.tok		# name
		self.knowntokens[tok.tok] = tok			# remember that tok is a token, not a symbol

	def add_rule(self, rule):
		""" Add a rule """
		self.rules.append(rule)

	def __str__(self):
		return "\n".join(map(str,self.inline_tokens+self.tokens))

	def get_inline_tokens(self):
		return	[ (_2str(self.token_name[t.expr]), _2str(t.expr)) for t in self.inline_tokens ]

	def get_tokens(self):
		return [ (_2str(t.tok), _2str(t.expr), t.action, t.sep) for t in self.tokens ]

	def istoken(self, name):
		""" Make the difference between a token and a symbol """
		return name in self.knowntokens

class Parser(list):
	""" Container for a set of rules """

	def __init__(self, name, bases):
		self.name = name		# name of the parser class
		self.bases = bases		# list of the base classes

	def add(self, obj):
		""" Add a token, a rule or a code section """
		if _v>=2: sys.stdout.write("%s\n"%obj)
		self.append(obj)

	def __str__(self): return "%s(%s)"%(self.name, self.bases)

	def genCode(self):
		""" Generate the code of the parser in 2 passes:
			1) get inline token, token and symbol list
			2) generate the code
		"""
		collector = Collector()
		for p in self: p.collect(collector)
		return [
			"class %s(tpg.ToyParser,%s):"%(self.name, self.bases.genCode()),
			"",
				self.genInitCode(1, collector.get_inline_tokens(), collector.get_tokens()),
				[ obj.genCode(1) for obj in self ],
		]

	def genInitCode(self, indent, inline_tokens, tokens):
		""" Generate the initialisation code of the scanner """
		tab = "\t"*indent
		tab1 = tab+"\t"
		tab2 = tab1+"\t"
		return [
			tab  +	"def __init__(self):",
			tab1 +		"self._init_scanner(",
			[ tab2 +		"(%s, %s),"%t for t in inline_tokens ],
			[ tab2 +		"(%s, %s, %s, %s),"%t for t in tokens ],
			tab1 +		")",
			"",
		]

class Object:
	""" Object (identifier or number) container """

	def __init__(self, name):
		self.name = name

	def __str__(self): return self.name

	def genCode(self): return self.name

	def doc(self): return self.name

class String:
	""" String container """

	def __init__(self, name):
		self.name = 'r"%s"'%name;

	def __str__(self): return self.name

	def genCode(self): return self.name

	def doc(self): return self.name

class Objects(list):
	""" Object list container (tuples, arguments, ...) """

	def add(self, obj):
		self.append(obj)

	def __str__(self): return ','.join(map(str,self))

	def genCode(self): return ','.join([o.genCode() for o in self])

	def doc(self): return ','.join([o.doc() for o in self])

class Composition:
	""" Composition container (object.ident) """

	def __init__(self, o1, o2):
		self.o1, self.o2 = o1, o2

	def __str__(self): return "%s.%s"%(self.o1, self.o2)

	def doc(self): return "%s.%s"%(self.o1.doc(), self.o2.doc())

	def genCode(self): return "%s.%s"%(self.o1.genCode(), self.o2.genCode())

class Application:
	""" Application container (object<args>) """

	def __init__(self, o, as):
		self.o, self.as = o, as

	def __str__(self):
		return "%s(%s)"%(self.o, ','.join(map(str,self.as)))

	def doc(self):
		return "%s<%s>"%(self.o.doc(), self.as.doc())

	def genCode(self): return "%s(%s)"%(self.o.genCode(), self.as.genCode())

class Indexation:
	""" Indexation container (object[index]) """

	def __init__(self, o, i):
		self.o, self.i = o, i

	def __str__(self):
		return "%s[%s]"%(self.o, self.i)

	def doc(self):
		return "%s[%s]"%(self.o.doc(), self.i.doc())

	def genCode(self):
		return "%s[%s]"%(self.o.genCode(), self.i.genCode())

class Slice:
	""" Slice container (object:object) """

	def __init__(self, i, j):
		self.i, self.j = i, j

	def __str__(self):
		return "%s:%s"%(self.i, self.j)

	def doc(self):
		return "%s:%s"%(self.i.doc(), self.j.doc())

	def genCode(self):
		return "%s:%s"%(self.i.genCode(), self.j.genCode())

class Token:
	""" Token container """

	def __init__(self, tok, expr, fun, sep):
		self.tok = tok			# token
		self.expr = expr		# regular expression
		self.action = fun		# function to apply to the token
		self.sep = sep			# flag telling if tok is a separator

	def __str__(self):
		return "%s %s: '%s' %s"%(self.sep and "separator" or "token", self.tok, self.expr, self.action)

	def collect(self, collector):
		collector.add_token(self)

	def genCode(self, indent):
		return []	# scanner code is generated by Parser

class VariableGenerator:
	""" New variable generator """

	def __init__(self):
		self.variables = {}

	def next(self, base):
		n = self.variables.get(base,0)
		n += 1
		self.variables[base] = n
		return "%s%d"%(base, n)

class Rule:
	""" Rule container """

	def __init__(self, symbol, expr):
		self.symbol = symbol	# head
		self.expr = expr		# body

	def __str__(self):
		return "%s -> %s ;"%(self.symbol, self.expr)

	def collect(self, collector):
		collector.add_rule(self)
		self.expr.collect(collector)

	def genCode(self, indent):
		ret = self.symbol.genRetCode()
		return [
			self.symbol.genDefCode(indent),							# def symbol(args):
			"\t"*(indent+1)+self.doc(),								#	""" head -> body """
			self.expr.genCode(indent+1,vargen=VariableGenerator()),	#	code
			_if(ret, "\t"*(indent+1)+"return %s"%ret, []),			#	return code
			"",
		]

	def doc(self):
		return '""" %s -> %s """'%(self.symbol.doc(), self.expr.doc())

class Symbol:
	""" Symbol container """
	
	def __init__(self, id, as, ret):
		self.name = id
		self.args = as
		self.ret = ret

	def __str__(self): return "%s(%s)/%s"%(self.name, ','.join(map(str,self.args)), self.ret)

	def collect(self, collector):
		self.collector = collector

	def genCode(self, indent, vargen=None, p=None):
		""" Code to call a symbol """
		if self.ret: c = "%s = "%self.ret.genCode()
		else: c = ""
		if self.collector.istoken(self.name):
			c += "self._eat('%s')"%self.name
		else:
			c += "self.%s(%s)"%(self.name, self.args.genCode())
		return "\t"*indent + c

	def genDefCode(self, indent):
		""" Code to define a symbol (ie a rule) """
		return "\t"*indent + "def %s(self,%s):"%(self.name, self.args.genCode())

	def genRetCode(self):
		""" Code for the return value of the symbol """
		if self.ret: return self.ret.genCode()
		else: return ""

	def doc(self): return self.name

class Sequence(list):
	""" Container for a sequence in a rule """

	def add(self, e):
		self.append(e)

	def __str__(self): return " ".join(map(str,self))

	def collect(self, collector):
		for i in self: i.collect(collector)

	def doc(self): return " ".join([(isinstance(e,Alternative) and "(%s)" or "%s")%e.doc() for e in self])

	def genCode(self, indent, vargen=None, p=None):
		return [ e.genCode(indent,vargen=vargen) for e in self ]

class Alternative:
	""" Container for a choice in a rule """

	def __init__(self, a, b):
		self.a = a
		self.b = b

	def __str__(self): return "(%s | %s)"%(self.a, self.b)

	def collect(self, collector):
		self.a.collect(collector)
		self.b.collect(collector)

	def doc(self): return "%s | %s"%(self.a.doc(), self.b.doc())

	def genCode(self, indent, vargen=None, p=None):
		tab = "\t"*indent
		if p is None:
			p = vargen.next("__p")
			pos = tab + "%s = self._cur_token"%p
		else:
			pos = []
		return [
			pos,
			tab + "try:",
				self.a.genCode(indent+1,vargen=vargen,p=p),
			tab + "except tpg.TPGWrongMatch:",
			tab + "\tself._cur_token = %s"%p,
				self.b.genCode(indent+1,vargen=vargen,p=p),
		]

class MakeAST:
	""" Container for an AST affectation (LHS=RHS) """

	def __init__(self, LHS, RHS):
		self.LHS = LHS
		self.RHS = RHS

	def __str__(self): return "%s = %s"%(self.LHS, self.RHS)

	def collect(self, collector): pass

	def doc(self): return ""

	def genCode(self, indent, vargen=None, p=None):
		return "\t"*indent + "%s = %s"%(self.LHS.genCode(), self.RHS.genCode())

class AddAST:
	""" Container for an AST update (LHS-RHS) """

	def __init__(self, LHS, RHS):
		self.LHS = LHS
		self.RHS = RHS

	def __str__(self): return "%s-%s"%(self.LHS, self.RHS)

	def collect(self, collector): pass

	def doc(self): return ""

	def genCode(self, indent, vargen=None, p=None):
		return "\t"*indent + "%s.add(%s)"%(self.LHS.genCode(), self.RHS.genCode())

class Rep:
	""" Container for a repeated expression (*, +, ?, {m,n}) """

	def __init__(self, parser, m, M, e):
		if None not in (m, M) and m>M: parser.WrongMatch()
		self.e = e	# expression
		self.m = m	# min loops
		self.M = M	# max loops

	def __str__(self): return "(%s){%s,%s}"%(self.e, self.m or "", self.M or "")

	def collect(self, collector):
		self.e.collect(collector)

	def doc(self):
		if self.m == 0:
			if self.M == 1:
				r = "?"
			elif self.M is None:
				r = "*"
			else:
				r = "{,%M}"%self.M
		elif self.m == 1:
			if self.M is None:
				r = "+"
			else:
				r = "{1,%s}"%self.M
		else:
			if self.M is None:
				r = "{%s,}"%self.m
			else:
				r = "{%s,%s}"%(self.m, self.M)
		return "(%s)%s"%(self.e.doc(), r)

	def genCode(self, indent, vargen=None, p=None):
		tab = "\t"*indent
		m, M = self.m, self.M
		p = vargen.next("__p")
		if (m, M) == (0, 1):	# "e ?"
			return [
				tab + "%s = self._cur_token"%p,					# get current token
				tab + "try:",
					self.e.genCode(indent+1, vargen=vargen),	# try to match e once
				tab + "except tpg.TPGWrongMatch:",				# if failed
				tab + "\tself._cur_token = %s"%p,				# go back to the current token
			]
		elif (m, M) == (0, None):	# "e *"
			return [
				tab + "%s = self._cur_token"%p,						# get current token
				tab + "while 1:",									# loop as much as possible
				tab + "\ttry:",
						self.e.genCode(indent+2, vargen=vargen),	# try to match e
				tab + "\t\t%s = self._cur_token"%p,					# if succeded get the new current token
				tab + "\texcept tpg.TPGWrongMatch:",
				tab + "\t\tself._cur_token = %s"%p,					# otherwise go back to the current token
				tab + "\t\tbreak",									# and exit the loop
			]
		else:						# "e +" or "e {m,M}"
			n = vargen.next("__n")
			return [
				tab + "%s = self._cur_token"%p,						# get current token
				tab + "%s = 0"%n,									# loop counter = 0
				tab + "while %s:"%_if(M is None,"1","%s<%s"%(n,M)),	# loop until counter = M
				tab + "\ttry:",
						self.e.genCode(indent+2, vargen=vargen),	# try to match e
				tab + "\t\t%s += 1"%n,								# inc loop counter
				tab + "\t\t%s = self._cur_token"%p,					# if succeded get the new current token
				tab + "\texcept tpg.TPGWrongMatch:",
				tab + "\t\tif %s >= %s:"%(n, m),					# otherwise if enough loops
				tab + "\t\t\tself._cur_token = %s"%p,				# go back to the current token
				tab + "\t\t\tbreak",								# and exit the loop
				tab + "\t\telse:",
				tab + "\t\t\tself.WrongMatch()",					# otherwise fail
			]

class InlineToken:
	""" Container for inline tokens """

	def __init__(self, expr, ret):
		self.expr = expr	# expression
		self.ret = ret		# return object

	def __str__(self): return "'%s'/%s"%(self.expr, self.ret)

	def collect(self, collector):
		collector.add_inline_token(self)
		self.collector = collector

	def genCode(self, indent, vargen=None, p=None):
		if self.ret:
			ret = "%s = "%self.ret.genCode()
		else:
			ret = ""
		name = self.collector.token_name[self.expr]
		if not self.expr.startswith(name):
			comment = " # %s"%self.expr
		else:
			comment = ""
		return "\t"*indent + ret + "self._eat('%s')%s"%(name, comment)

	def doc(self): return "'%s'"%self.expr

class Mark:
	""" Container for marks """

	def __init__(self, obj):
		self.obj = obj;

	def __str__(self): return "!%s"%self.obj

	def collect(self, collector): pass

	def genCode(self, indent, vargen=None, p=None):
		return "\t"*indent + "%s = self._mark()"%self.obj.genCode()

	def doc(self): return ""

class Extraction:
	""" Container for text extraction """

	def __init__(self, start, end):
		self.start = start
		self.end = end

	def __str__(self): return "%s..%s"%(self.start, self.end)

	def collect(self, collector): pass

	def genCode(self, vargen=None, p=None):
		return "self._extract(%s,%s)"%(self.start.genCode(), self.end.genCode())

	def doc(self): return ""

#<runtime>
class _TokenDef:
	""" Token definition for the scanner """

	ident_pat = re.compile(r'^\w+$')
	
	def __init__(self, tok, regex=None, action=None, separator=0):
		if regex is None: regex = tok
		if self.ident_pat.match(regex): regex += r'\b'	# match 'if\b' instead of 'if'
		if action is None: action = lambda x:x			# default action if identity
		elif not callable(action): action = lambda x,y=action:y	# action must be callable
		self.tok = tok							# token name
		self.regex = '(?P<%s>%s)'%(tok, regex)	# token regexp
		self.action = action					# token modifier
		self.separator = separator				# is this a separator ?

	def __str__(self):
		return "token %s: %s %s;"%(self.tok, self.regex, self.action)

class _Token:
	""" Token instanciated while scanning """

	def __init__(self, tok, text, val, lineno, start, end):
		self.tok = tok			# token type
		self.text = text		# matched text
		self.val = val			# value (ie action(text))
		self.lineno = lineno	# token line number
		self.start = start		# token start index
		self.end = end			# token end index

	def __str__(self):
		return "%d:%s[%s]"%(self.lineno, self.tok, self.val)

class _Eof:
	""" EOF token """

	def __init__(self, lineno='EOF'):
		self.lineno = lineno
		self.text = 'EOF'
		self.val = 'EOF'

	def __str__(self):
		return "%s:Eof"%self.lineno

class _Scanner:
	""" Lexical scanner """

	def __init__(self, *tokens):
		regex = []				# regex list
		actions = {}			# dict token->action
		separator = {}			# set of separators
		for token in tokens:
			regex.append(token.regex)
			actions[token.tok] = token.action
			separator[token.tok] = token.separator
		self.regex = re.compile('|'.join(regex))	# regex is the choice between all tokens
		self.actions = actions
		self.separator = separator

	def tokens(self, input):
		""" Scan input and return a list of _Token instances """
		self.input = input
		i = 0				# start of the next token
		l = len(input)
		lineno = 1			# current token line number
		toks = []			# token list
		while i<l:												# while not EOF
			token = self.regex.match(input,i)					# get next token
			if not token:										# if none raise LexicalError
				last = toks and toks[-1] or _Eof(lineno)
				raise tpg.LexicalError(last)
			j = token.end()										# end of the current token
			for (t,v) in token.groupdict().items():				# search the matched token
				if v is not None and self.actions.has_key(t):
					tok = t										# get its type
					text = token.group()						# get matched text
					val = self.actions[tok](text)				# compute its value
					break
			if not self.separator[tok]:								# if the matched token is a real token
				toks.append(_Token(tok, text, val, lineno, i, j))	# store it
			lineno += input.count('\n', i, j)					# update lineno
			i = j												# go to the start of the next token
		return toks

class TPGWrongMatch(Exception):
	def __init__(self, last):
		self.last = last

class LexicalError(Exception):
	def __init__(self, last):
		self.last = last
	def __str__(self):
		if self.last:
			return "%s: Lexical error near %s"%(self.last.lineno, self.last.text)
		else:
			return "1: Lexical error"

class SyntaxError(Exception):
	def __init__(self, last):
		self.last = last
	def __str__(self):
		if self.last:
			return "%s: Syntax error near %s"%(self.last.lineno, self.last.text)
		else:
			return "1: Syntax error"

class ToyParser:
	""" Base class for every TPG parsers """

	def _init_scanner(self, *tokens):
		""" Build the scanner """
		self._lexer = _Scanner(*[_TokenDef(*t) for t in tokens])
		self._cur_token = 0

	def _eat(self, token):
		""" Eat one token """
		try:
			t = self._tokens[self._cur_token]	# get current token
		except IndexError:						# if EOF
			self.WrongMatch()					# raise TPGWrongMatch to backtrack
		if t.tok == token:						# if current is an expected token
			self._cur_token += 1				# go to the next one
			return t.val						# and return its value
		else:
			self.WrongMatch()					# else backtrack

	def WrongMatch(self):
		""" Backtracking """
		try:
			raise tpg.TPGWrongMatch(self._tokens[self._cur_token])
		except IndexError:
			raise tpg.TPGWrongMatch(_Eof())

	def check(self, cond):
		""" Check a condition while parsing """
		if not cond:			# if condition is false
			self.WrongMatch()	# backtrac

	def __call__(self, input, *args):
		""" Parse the axiom of the grammar (if any) """
		return self.parse('START', input, *args)

	def parse(self, symbol, input, *args):
		""" Parse an input start at a given symbol """
		try:
			self._tokens = self._lexer.tokens(input)	# scan tokens
			self._cur_token = 0							# start at the first token
			ret = getattr(self, symbol)(*args)			# call the symbol
			if self._cur_token < len(self._tokens):		# if there are unparsed tokens
				self.WrongMatch()						# raise an error
			return ret									# otherwise return the result
		except tpg.TPGWrongMatch, e:					# convert an internal TPG error
			raise tpg.SyntaxError(e.last)				# into a tpg.SyntaxError

	def _mark(self):
		""" Get a mark for the current token """
		return self._cur_token

	def _extract(self, a, b):
		""" Extract text between 2 marks """
		if not self._tokens: return ""
		if a<len(self._tokens):
			start = self._tokens[a].start
		else:
			start = self._tokens[-1].end
		if b>0:
			end = self._tokens[b-1].end
		else:
			end = self._tokens[0].start
		return self._lexer.input[start:end]

	def lineno(self, mark=None):
		""" Get the line number of a mark (or the current token if none) """
		if mark is None: mark = self._cur_token
		if not self._tokens: return 0
		if mark<len(self._tokens):
			return self._tokens[mark].lineno
		else:
			return self._tokens[-1].lineno
	
#</runtime>

}}

{{ cut = lambda n: lambda s,n=n:s[n:-n] }}

parser TPGParser:

	separator space: "\s+|#.*";

	token string: "\"(\\.|[^\"\\]+)*\"|'(\\.|[^'\\]+)*'" cut<1>;
	token code: "\{\{(\}?[^\}]+)*\}\}" cut<2>;
	token obra: "\{";
	token cbra: "\}";
	token ident: "\w+";


	START/parsers.genCode<> -> PARSERS/parsers ;

	PARSERS/parsers ->
		OPTIONS/opts
		parsers = Parsers<opts>
		( code/c parsers-Code<c> )*
		(	'parser' ident/id ( '\(' OBJECTS/ids '\)' | ids = Objects<> ) ':'
			p = Parser<id, ids>
			(	code/c p-Code<c>
			|	TOKEN/t p-t
			|	RULE/c p-c
			)*
			parsers-p
		|	'main' ':' ( code/c parsers-Code<c> )*
		)*
		;

	OPTIONS/opts ->
		opts = Options<>
		(	'set' ident/opt ( '=' string/val | val = 1 )
			{{ if opt.startswith('no'): opt, val = opt[2:], None }}
			{{ opts.set(opt,val) }}
		)*
		;

	TOKEN/Token<t,e,f,s> ->
		(	'token' s = 0
		|	'separator' s = 1
		)
		ident/t ':' string/e ( OBJECT/f | f = None )
		';'
		;

	OBJECT/o ->
			ident/o SOBJECT<Object<o>>/o
		|	string/o SOBJECT<String<o>>/o
		|	'<' OBJECTS/o '>'
		;

	SOBJECT<o>/o ->
		(	'\.\.' OBJECT/o2 o=Extraction<o,o2>
		|	'\.' ident/o2 SOBJECT<Composition<o,Object<o2>>>/o
		|	'<' OBJECTS/as '>' SOBJECT<Application<o,as>>/o
		|	'\[' INDICE/i '\]' SOBJECT<Indexation<o,i>>/o
		|	#
		)
		;

	OBJECTS/objs ->
		objs = Objects<>
		(	OBJECT/obj objs-obj
			( ',' OBJECTS/obj objs-obj )*
		)?
		;

	INDICE/i -> OBJECT/i ( ':' OBJECT/i2 i=Slice<i,i2> )? ;

	RULE/Rule<s,e> -> SYMBOL/s '->' EXPR/e ';' ;

	SYMBOL/Symbol<id,as,ret> ->
		ident/id
		( '<' OBJECTS/as '>' | as = Objects<> )
		(	'/' OBJECT/ret
		|	ret = None
		)
		;

	EXPR/e -> TERM/e ( '\|' TERM/t e = Alternative<e,t> )* ;

	TERM/t -> t = Sequence<> ( FACT/f t-f )* ;

	FACT/f -> AST_OP/f | MARK_OP/f | code/c f=Code<c> | ATOM/f REP<f>/f ;

	AST_OP/op ->
		OBJECT/o1
		(	'=' OBJECT/o2 op = MakeAST<o1,o2>
		|	'-' OBJECT/o2 op = AddAST<o1,o2>
		)
		;

	MARK_OP/op -> '!' OBJECT/o op = Mark<o> ;

	ATOM/a ->
		(	SYMBOL/a
		|	INLINE_TOKEN/a
		|	'\(' EXPR/a '\)'
		)
		;

	REP<a>/a ->
		(	'\?'										a = Rep<self,0,1,a>
		|	'\*'										a = Rep<self,0,None,a>
		|	'\+'										a = Rep<self,1,None,a>
		|	obra NB<0>/m ( ',' NB<None>/M | M=m ) cbra	a = Rep<self,m,M,a>
		)?
		;

	NB<n>/eval<n> -> ident/n ? ;

	INLINE_TOKEN/InlineToken<expr, ret> ->
		string/expr
		( '/' OBJECT/ret | ret = None )
		;

main:

{{

_TPGParser = TPGParser()

_v = 0

if __name__ == "__main__":

	import sys

	class ArgError: pass

	def getargs(args):
		def check(cond):
			if not cond: raise ArgError
		i, o, v = None, None, 0
		while args:
			arg = args.pop(0)
			if arg == '-o':
				check(o is None and args)
				o = args.pop()
				check(o.endswith('.py'))
			elif re.match('-v+$', arg):
				v += len(arg)-1
			else:
				check(i is None and arg.endswith('.g'))
				i = arg
		check(i is not None)
		if o is None: o = i[:-2] + '.py'
		return i, o, v

	__file__ = sys.argv[0]
	sys.stdout.write("TPG v%s (c) Christophe Delord\n"%__version__)
	try: (grammar_file, output_file, _v) = getargs(sys.argv[1:])
	except ArgError: sys.stderr.write("Syntax: %s [-v|vv] grammar_file.g [-o output_file.py]\n"%__file__)
	else:
		try:
			sys.stdout.write("TPG: translating %s to %s\n"%(grammar_file,output_file))
			f = open(grammar_file, 'r')
			parser = compile(f.read())
			f.close()
			g = open(output_file, 'w')
			g.write(parser)
			g.close()
			sys.stdout.write("Translation OK\n")
		except IOError, e:
			sys.stderr.write("IOError: %s\n"%e)

}}
