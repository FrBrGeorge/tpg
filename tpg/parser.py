
#........[ TOY PARSER GENERATOR ].........................!
#                                                        ! !
# Warning: This file was automatically generated by TPG ! | !
# Do not edit this file unless you know what you do.   !  |  !
#                                                     !   @   !
#....................................................!!!!!!!!!!!
#
# For further information about TPG you can visit
# http://christophe.delord.free.fr/en/tpg

import base


"""
Toy Parser Generator: A Python parser generator
Copyright (C) 2002 Christophe Delord
 
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

For further information about TPG you can visit
http://christophe.delord.free.fr/en/tpg
"""

from codegen import *

cut = lambda n: lambda s,n=n:s[n:-n]

def cutstr(st):
    if st[0]=="'": st = st.replace('"', r'\"')
    return st[1:-1]

class TPGParser(base.ToyParser,):

    def _init_scanner(self):
        self._lexer = base._Scanner(
            base._TokenDef(r"_kw_parser", r"parser"),
            base._TokenDef(r"_tok_1", r"\("),
            base._TokenDef(r"_tok_2", r"\)"),
            base._TokenDef(r"_tok_3", r":"),
            base._TokenDef(r"_kw_main", r"main"),
            base._TokenDef(r"_kw_set", r"set"),
            base._TokenDef(r"_tok_4", r"="),
            base._TokenDef(r"_tok_5", r","),
            base._TokenDef(r"_kw_token", r"token"),
            base._TokenDef(r"_kw_separator", r"separator"),
            base._TokenDef(r"_tok_6", r";"),
            base._TokenDef(r"_tok_7", r"<"),
            base._TokenDef(r"_tok_8", r">"),
            base._TokenDef(r"_tok_9", r"\.\."),
            base._TokenDef(r"_tok_10", r"\."),
            base._TokenDef(r"_tok_11", r"\["),
            base._TokenDef(r"_tok_12", r"\]"),
            base._TokenDef(r"_tok_13", r"->"),
            base._TokenDef(r"_kw_lex", r"lex"),
            base._TokenDef(r"_tok_14", r"\|"),
            base._TokenDef(r"_tok_15", r"!"),
            base._TokenDef(r"_kw_check", r"check"),
            base._TokenDef(r"_kw_error", r"error"),
            base._TokenDef(r"_tok_16", r"-"),
            base._TokenDef(r"_tok_17", r"@"),
            base._TokenDef(r"_tok_18", r"\?"),
            base._TokenDef(r"_tok_19", r"\+"),
            base._TokenDef(r"space", r"\s+|#.*", None, 1),
            base._TokenDef(r"string", r"\"(\\.|[^\"\\]+)*\"|'(\\.|[^'\\]+)*'", cutstr, 0),
            base._TokenDef(r"code", r"\{\{(\}?[^\}]+)*\}\}", cut(2), 0),
            base._TokenDef(r"obra", r"\{", None, 0),
            base._TokenDef(r"cbra", r"\}", None, 0),
            base._TokenDef(r"retsplit", r"//", None, 0),
            base._TokenDef(r"ret", r"/", None, 0),
            base._TokenDef(r"star2", r"\*\*", None, 0),
            base._TokenDef(r"star", r"\*", None, 0),
            base._TokenDef(r"ident", r"\w+", None, 0),
        )

    def kw(self,name):
        """ kw -> ident """
        i = self._eat('ident')
        self.check(i==name )

    def START(self,):
        """ START -> PARSERS """
        parsers = self.PARSERS()
        return parsers.genCode()

    def PARSERS(self,):
        """ PARSERS -> GLOBAL_OPTIONS (code)* ('parser' ident ('\(' ARGS '\)' | ) ':' LOCAL_OPTIONS (code | TOKEN | RULE | LEX_RULE)* | 'main' ':' (code)*)* """
        opts = self.GLOBAL_OPTIONS()
        parsers = Parsers(opts)
        __p1 = self._cur_token
        while 1:
            try:
                c = self._eat('code')
                parsers.add(Code(c))
                __p1 = self._cur_token
            except self.TPGWrongMatch:
                self._cur_token = __p1
                break
        __p2 = self._cur_token
        while 1:
            try:
                try:
                    self._eat('_kw_parser') # parser
                    try:
                        id = self._eat('ident')
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                    try:
                        __p3 = self._cur_token
                        try:
                            self._eat('_tok_1') # \(
                            try:
                                ids = self.ARGS()
                                self._eat('_tok_2') # \)
                            except self.TPGWrongMatch, e:
                                self.ParserError(e.last)
                        except self.TPGWrongMatch:
                            self._cur_token = __p3
                            ids = Args()
                        self._eat('_tok_3') # :
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                    try:
                        opts = self.LOCAL_OPTIONS()
                        p = Parser(id,ids,opts)
                        self.current_parser = p
                        __p4 = self._cur_token
                        while 1:
                            try:
                                try:
                                    try:
                                        c = self._eat('code')
                                        p.add(Code(c))
                                    except self.TPGWrongMatch:
                                        self._cur_token = __p4
                                        t = self.TOKEN()
                                        p.add(t)
                                except self.TPGWrongMatch:
                                    self._cur_token = __p4
                                    try:
                                        r = self.RULE()
                                        p.add(r)
                                    except self.TPGWrongMatch:
                                        self._cur_token = __p4
                                        r = self.LEX_RULE()
                                        p.add(r)
                                __p4 = self._cur_token
                            except self.TPGWrongMatch:
                                self._cur_token = __p4
                                break
                        parsers.add(p)
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                except self.TPGWrongMatch:
                    self._cur_token = __p2
                    self._eat('_kw_main') # main
                    self._eat('_tok_3') # :
                    try:
                        __p5 = self._cur_token
                        while 1:
                            try:
                                c = self._eat('code')
                                parsers.add(Code(c))
                                __p5 = self._cur_token
                            except self.TPGWrongMatch:
                                self._cur_token = __p5
                                break
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                __p2 = self._cur_token
            except self.TPGWrongMatch:
                self._cur_token = __p2
                break
        return parsers

    def GLOBAL_OPTIONS(self,):
        """ GLOBAL_OPTIONS -> ('set' kw '=' string)* """
        opts = Options()
        __p1 = self._cur_token
        while 1:
            try:
                self._eat('_kw_set') # set
                try:
                    self.kw(r"magic")
                    try:
                        self._eat('_tok_4') # =
                        val = self._eat('string')
                        opts.set('magic', val) 
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
                __p1 = self._cur_token
            except self.TPGWrongMatch:
                self._cur_token = __p1
                break
        return opts

    def LOCAL_OPTIONS(self,):
        """ LOCAL_OPTIONS -> ('set' (kw | kw '=' string (',' string)?))* """
        opts = Options()
        __p1 = self._cur_token
        while 1:
            try:
                self._eat('_kw_set') # set
                try:
                    __p2 = self._cur_token
                    try:
                        self.kw(r"CSL")
                        try:
                            opts.set('CSL', 1) 
                        except self.TPGWrongMatch, e:
                            self.ParserError(e.last)
                    except self.TPGWrongMatch:
                        self._cur_token = __p2
                        self.kw(r"indent")
                        try:
                            self._eat('_tok_4') # =
                            tabs = self._eat('string')
                            opts.set('indent', tabs) 
                            __p3 = self._cur_token
                            try:
                                self._eat('_tok_5') # ,
                                regexp = self._eat('string')
                                opts.set('noindent', regexp) 
                            except self.TPGWrongMatch:
                                self._cur_token = __p3
                        except self.TPGWrongMatch, e:
                            self.ParserError(e.last)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
                __p1 = self._cur_token
            except self.TPGWrongMatch:
                self._cur_token = __p1
                break
        return opts

    def CHECK_CSL(self,obj):
        """ CHECK_CSL ->  |  """
        __p1 = self._cur_token
        try:
            self.check(self.current_parser.opts['CSL'] )
        except self.TPGWrongMatch:
            self._cur_token = __p1
            self.error("%s: Only for CSL lexers"%obj )

    def CHECK_NOT_CSL(self,obj):
        """ CHECK_NOT_CSL ->  |  """
        __p1 = self._cur_token
        try:
            self.check(not self.current_parser.opts['CSL'] )
        except self.TPGWrongMatch:
            self._cur_token = __p1
            self.error("%s: Only for non CSL lexers"%obj )

    def TOKEN(self,):
        """ TOKEN -> ('token' | 'separator') CHECK_NOT_CSL ident ':' string (OBJECT | ) ';' """
        __p1 = self._cur_token
        try:
            self._eat('_kw_token') # token
            s = 0
        except self.TPGWrongMatch:
            self._cur_token = __p1
            self._eat('_kw_separator') # separator
            s = 1
        try:
            self.CHECK_NOT_CSL(r"Predefined token")
            t = self._eat('ident')
            self._eat('_tok_3') # :
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        try:
            e = self._eat('string')
            __p2 = self._cur_token
            try:
                f = self.OBJECT()
            except self.TPGWrongMatch:
                self._cur_token = __p2
                f = None
            self._eat('_tok_6') # ;
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        return Token(t,e,f,s)

    def ARGS(self,):
        """ ARGS -> (ARG (',' ARG)*)? """
        args = Args()
        __p1 = self._cur_token
        try:
            arg = self.ARG()
            args.add(arg)
            __p2 = self._cur_token
            while 1:
                try:
                    self._eat('_tok_5') # ,
                    arg = self.ARG()
                    args.add(arg)
                    __p2 = self._cur_token
                except self.TPGWrongMatch:
                    self._cur_token = __p2
                    break
        except self.TPGWrongMatch:
            self._cur_token = __p1
        return args

    def ARG(self,):
        """ ARG -> '\*\*' OBJECT | '\*' OBJECT | ident '=' OBJECT | OBJECT """
        __p1 = self._cur_token
        try:
            try:
                self._eat('star2') # \*\*
                try:
                    kw = self.OBJECT()
                    arg = ArgDict(kw)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
            except self.TPGWrongMatch:
                self._cur_token = __p1
                self._eat('star') # \*
                try:
                    args = self.OBJECT()
                    arg = ArgList(args)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
        except self.TPGWrongMatch:
            self._cur_token = __p1
            try:
                name = self._eat('ident')
                self._eat('_tok_4') # =
                try:
                    value = self.OBJECT()
                    arg = KeyWordArg(name,value)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
            except self.TPGWrongMatch:
                self._cur_token = __p1
                arg = self.OBJECT()
        return arg

    def OBJECT(self,):
        """ OBJECT -> ident SOBJECT | string SOBJECT | '<' OBJECTS '>' | code """
        __p1 = self._cur_token
        try:
            try:
                o = self._eat('ident')
                o = self.SOBJECT(Object(o))
            except self.TPGWrongMatch:
                self._cur_token = __p1
                o = self._eat('string')
                o = self.SOBJECT(String(o))
        except self.TPGWrongMatch:
            self._cur_token = __p1
            try:
                self._eat('_tok_7') # <
                o = self.OBJECTS()
                self._eat('_tok_8') # >
            except self.TPGWrongMatch:
                self._cur_token = __p1
                c = self._eat('code')
                self.check(c.count('\n')==0)
                o = Code(c)
        return o

    def SOBJECT(self,o):
        """ SOBJECT -> ('\.\.' OBJECT | '\.' ident SOBJECT | '<' ARGS '>' SOBJECT | '\[' INDICE '\]' SOBJECT | ) """
        __p1 = self._cur_token
        try:
            try:
                self._eat('_tok_9') # \.\.
                o2 = self.OBJECT()
                o = Extraction(o,o2)
            except self.TPGWrongMatch:
                self._cur_token = __p1
                self._eat('_tok_10') # \.
                o2 = self._eat('ident')
                o = self.SOBJECT(Composition(o,Object(o2)))
        except self.TPGWrongMatch:
            self._cur_token = __p1
            try:
                self._eat('_tok_7') # <
                as = self.ARGS()
                self._eat('_tok_8') # >
                o = self.SOBJECT(Application(o,as))
            except self.TPGWrongMatch:
                self._cur_token = __p1
                try:
                    self._eat('_tok_11') # \[
                    i = self.INDICE()
                    self._eat('_tok_12') # \]
                    o = self.SOBJECT(Indexation(o,i))
                except self.TPGWrongMatch:
                    self._cur_token = __p1
        return o

    def OBJECTS(self,):
        """ OBJECTS -> (OBJECT (',' OBJECT)*)? """
        objs = Objects()
        __p1 = self._cur_token
        try:
            obj = self.OBJECT()
            objs.add(obj)
            __p2 = self._cur_token
            while 1:
                try:
                    self._eat('_tok_5') # ,
                    obj = self.OBJECT()
                    objs.add(obj)
                    __p2 = self._cur_token
                except self.TPGWrongMatch:
                    self._cur_token = __p2
                    break
        except self.TPGWrongMatch:
            self._cur_token = __p1
        return objs

    def INDICE(self,):
        """ INDICE -> (OBJECT | ) (':' (OBJECT | ))? """
        __p1 = self._cur_token
        try:
            i = self.OBJECT()
        except self.TPGWrongMatch:
            self._cur_token = __p1
            i = None
        __p2 = self._cur_token
        try:
            self._eat('_tok_3') # :
            __p3 = self._cur_token
            try:
                i2 = self.OBJECT()
            except self.TPGWrongMatch:
                self._cur_token = __p3
                i2 = None
            i = Slice(i,i2)
        except self.TPGWrongMatch:
            self._cur_token = __p2
        __p4 = self._cur_token
        try:
            self.check(i is not None)
        except self.TPGWrongMatch:
            self._cur_token = __p4
            self.error(r"Empty index or slice")
        return i

    def RULE(self,):
        """ RULE -> SYMBOL '->' EXPR ';' """
        s = self.SYMBOL()
        self._eat('_tok_13') # ->
        try:
            e = self.EXPR()
            self._eat('_tok_6') # ;
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        return Rule(s,e)

    def LEX_RULE(self,):
        """ LEX_RULE -> 'lex' CHECK_CSL ('separator' | SYMBOL) '->' EXPR ';' """
        self._eat('_kw_lex') # lex
        try:
            self.CHECK_CSL(r"Lexical rule")
            __p1 = self._cur_token
            try:
                name = self._eat('_kw_separator') # separator
                s = Symbol(name,Args(),None)
            except self.TPGWrongMatch:
                self._cur_token = __p1
                s = self.SYMBOL()
            self._eat('_tok_13') # ->
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        try:
            e = self.EXPR()
            self._eat('_tok_6') # ;
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        return LexRule(s,e)

    def SYMBOL(self,):
        """ SYMBOL -> ident ('<' ARGS '>' | ) ('/' OBJECT | ) """
        id = self._eat('ident')
        __p1 = self._cur_token
        try:
            self._eat('_tok_7') # <
            as = self.ARGS()
            self._eat('_tok_8') # >
        except self.TPGWrongMatch:
            self._cur_token = __p1
            as = Args()
        __p2 = self._cur_token
        try:
            self._eat('ret') # /
            ret = self.OBJECT()
        except self.TPGWrongMatch:
            self._cur_token = __p2
            ret = None
        return Symbol(id,as,ret)

    def EXPR(self,):
        """ EXPR -> CUT_TERM ('\|' CUT_TERM)* """
        e = self.CUT_TERM()
        __p1 = self._cur_token
        while 1:
            try:
                self._eat('_tok_14') # \|
                try:
                    t = self.CUT_TERM()
                    e = Alternative(e,t)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
                __p1 = self._cur_token
            except self.TPGWrongMatch:
                self._cur_token = __p1
                break
        return balance(e)

    def CUT_TERM(self,):
        """ CUT_TERM -> TERM ('!' TERM ('!' TERM)*)? """
        e = self.TERM()
        __p1 = self._cur_token
        try:
            self._eat('_tok_15') # !
            try:
                ce = self.TERM()
                c = Cut()
                c.add(ce)
                __p2 = self._cur_token
                while 1:
                    try:
                        self._eat('_tok_15') # !
                        try:
                            ce = self.TERM()
                            c.add(ce)
                        except self.TPGWrongMatch, e:
                            self.ParserError(e.last)
                        __p2 = self._cur_token
                    except self.TPGWrongMatch:
                        self._cur_token = __p2
                        break
                e = Sequence(e,c)
            except self.TPGWrongMatch, e:
                self.ParserError(e.last)
        except self.TPGWrongMatch:
            self._cur_token = __p1
        return e

    def TERM(self,):
        """ TERM -> (FACT)* """
        t = Sequence()
        __p1 = self._cur_token
        while 1:
            try:
                f = self.FACT()
                t.add(f)
                __p1 = self._cur_token
            except self.TPGWrongMatch:
                self._cur_token = __p1
                break
        return t

    def FACT(self,):
        """ FACT -> AST_OP | MARK_OP | code | ATOM REP | 'check' OBJECT | 'error' OBJECT """
        __p1 = self._cur_token
        try:
            try:
                f = self.AST_OP()
            except self.TPGWrongMatch:
                self._cur_token = __p1
                try:
                    f = self.MARK_OP()
                except self.TPGWrongMatch:
                    self._cur_token = __p1
                    c = self._eat('code')
                    f = Code(c)
        except self.TPGWrongMatch:
            self._cur_token = __p1
            try:
                f = self.ATOM()
                try:
                    f = self.REP(f)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
            except self.TPGWrongMatch:
                self._cur_token = __p1
                try:
                    self._eat('_kw_check') # check
                    try:
                        cond = self.OBJECT()
                        f = Check(cond)
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                except self.TPGWrongMatch:
                    self._cur_token = __p1
                    self._eat('_kw_error') # error
                    try:
                        err = self.OBJECT()
                        f = Error(err)
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
        return f

    def AST_OP(self,):
        """ AST_OP -> OBJECT ('=' | '-') OBJECT """
        o1 = self.OBJECT()
        __p1 = self._cur_token
        try:
            self._eat('_tok_4') # =
            op = MakeAST
        except self.TPGWrongMatch:
            self._cur_token = __p1
            self._eat('_tok_16') # -
            op = AddAST
        try:
            o2 = self.OBJECT()
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        return op(o1,o2)

    def MARK_OP(self,):
        """ MARK_OP -> '@' OBJECT """
        self._eat('_tok_17') # @
        try:
            o = self.OBJECT()
        except self.TPGWrongMatch, e:
            self.ParserError(e.last)
        return Mark(o)

    def ATOM(self,):
        """ ATOM -> (SYMBOL | INLINE_TOKEN | '\(' EXPR '\)') """
        __p1 = self._cur_token
        try:
            a = self.SYMBOL()
        except self.TPGWrongMatch:
            self._cur_token = __p1
            try:
                a = self.INLINE_TOKEN()
            except self.TPGWrongMatch:
                self._cur_token = __p1
                self._eat('_tok_1') # \(
                try:
                    a = self.EXPR()
                    self._eat('_tok_2') # \)
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
        return a

    def REP(self,a):
        """ REP -> (('\?' | '\*' | '\+' | '\{' NB (',' NB | ) '\}'))? """
        __p1 = self._cur_token
        try:
            __p2 = self._cur_token
            try:
                try:
                    self._eat('_tok_18') # \?
                    try:
                        m, M = 0, 1 
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                except self.TPGWrongMatch:
                    self._cur_token = __p2
                    self._eat('star') # \*
                    try:
                        m, M = 0, None 
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
            except self.TPGWrongMatch:
                self._cur_token = __p2
                try:
                    self._eat('_tok_19') # \+
                    try:
                        m, M = 1, None 
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
                except self.TPGWrongMatch:
                    self._cur_token = __p2
                    self._eat('obra') # \{
                    try:
                        m = self.NB(0)
                        __p3 = self._cur_token
                        try:
                            self._eat('_tok_5') # ,
                            try:
                                M = self.NB(None)
                            except self.TPGWrongMatch, e:
                                self.ParserError(e.last)
                        except self.TPGWrongMatch:
                            self._cur_token = __p3
                            M = m
                        self._eat('cbra') # \}
                    except self.TPGWrongMatch, e:
                        self.ParserError(e.last)
            
            if M is not None:
                if m>M: self.error("Invalid repetition")
            elif a.empty():
                self.error("Infinite repetition of an empty expression")
            
            a = Rep(m,M,a)
        except self.TPGWrongMatch:
            self._cur_token = __p1
        return a

    def NB(self,n):
        """ NB -> ident? """
        __p1 = self._cur_token
        try:
            n = self._eat('ident')
        except self.TPGWrongMatch:
            self._cur_token = __p1
        return n

    def INLINE_TOKEN(self,):
        """ INLINE_TOKEN -> string ('/' OBJECT | '//' CHECK_CSL OBJECT | ) """
        expr = self._eat('string')
        __p1 = self._cur_token
        try:
            self._eat('ret') # /
            try:
                ret = self.OBJECT()
                split = None
            except self.TPGWrongMatch, e:
                self.ParserError(e.last)
        except self.TPGWrongMatch:
            self._cur_token = __p1
            try:
                self._eat('retsplit') # //
                try:
                    self.CHECK_CSL(r"Split return")
                    ret = self.OBJECT()
                    split = 1
                except self.TPGWrongMatch, e:
                    self.ParserError(e.last)
            except self.TPGWrongMatch:
                self._cur_token = __p1
                ret = None
                split = None
        return InlineToken(expr,ret,split)




_TPGParser = TPGParser()

def _compile(grammar):
    source = _TPGParser(grammar)
    code = __builtins__['compile'](source, "", 'exec')
    return source, code

def translate(grammar):
    """ Translate a grammar into Python """
    return _compile(grammar)[0]

def compile(grammar):
    """ Compile a grammer into a Python code object """
    return _compile(grammar)[1]

