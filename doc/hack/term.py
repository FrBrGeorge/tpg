
class Foo(tpg.base.ToyParser,):

    def _init_scanner(self):
        self._lexer = tpg.base._Scanner(
            tpg.base._TokenDef(r"_kw_inline", r"inline"),
            tpg.base._TokenDef(r"predef", r"bar", None, 0),
        )

    def S(self,):
        """ S -> 'inline' predef 'inline' predef """
        self._eat('_kw_inline') # inline
        self._eat('predef')
        s1 = self._eat('_kw_inline') # inline
        s2 = self._eat('predef')

