import sys
from collections import defaultdict

from lark import Lark, InlineTransformer

from fsm import Goto, Backtrack, If, Mark, Retract, State, Produce, Consume, Advance


GRAMMAR = r'''
    start       : "{" main state+ "}"
    main        : stmt+
    state       : LABEL ":" stmt+

    ?stmt       : expr ";"
                | switch
                | if_stmt
                | "{" CNAME? "}"   -> produce

    switch      : "switch" "(" CNAME ")" "{" case+ default? "}"
    case        : ( "case" literal ":" )+ stmt
    default     : "default" ":" stmt

    if_stmt     : "if" "(" CNAME OP literal ")" if_block [ "else" if_block ]

    if_block    : "{" stmt+ "}"
                | stmt

    ?expr       : CNAME+ CNAME [ "=" literal ]          -> decl
                | "goto" LABEL                          -> goto
                | "++YYCURSOR"                          -> advance
                | "yych" "=" "*YYCURSOR"                -> consume
                | "yych" "=" "*++YYCURSOR"              -> advance_consume
                | "yych" "=" "*(YYMARKER = ++YYCURSOR)" -> advance_consume
                | "yyaccept" "=" literal                -> mark
                | "YYCURSOR" "=" "YYMARKER"             -> backtrack
                | "YYCURSOR" "-=" literal               -> retract

    ?literal    : STRING                  -> string
                | INT                     -> int
                | "0x" HEXDIGIT HEXDIGIT  -> hex

    // dissambiguate with hex
    INT         : /0\b|[1-9]\d*/

    OP          : /==|!=|<=|>=/
    LABEL       : "yy" /\d+/
    STRING      : "'" /\\.|./* "'"

    COMMENT     : "/*" ( /./ )* "*/"
                | /#[^\n]*/
    %ignore COMMENT

    %import common.CNAME
    %import common.HEXDIGIT
    %import common.WS
    %ignore WS
'''


class Re2cTransformer(InlineTransformer):

    def _state_factory(self, label, stmts):
        actions = []
        for stmt in stmts:
            if isinstance(stmt, (list, tuple)):
                actions.extend(stmt)
            elif stmt is not None:
                actions.append(stmt)

        return State(label, actions)

    def start(self, main, *states):
        main.add(*states)
        return main

    def main(self, *stmts):
        return self._state_factory(None, [Mark(0)] + list(stmts))

    def state(self, t_label, *stmts):
        return self._state_factory(t_label.value, stmts)

    def switch(self, t_var, *stmts):
        return list(stmts)

    def case(self, *args):
        assert len(args) >= 2
        if type(args[0]) is int:
            assert len(args) == 2
            return If('==', args[0], args[1], varname='yyaccept')

        buffer = bytearray()
        for arg in args[:-1]:
            buffer.extend(arg)

        return If.IN(bytes(buffer), args[-1])

    def default(self, stmt):
        return stmt

    def if_stmt(self, t_var, t_op, rhs, true, false=None):
        return If(t_op.value, rhs, true, false, varname=t_var.value)

    def if_block(self, *stmts):
        return list(stmts)

    def backtrack(self):
        return Backtrack()

    def decl(self, *args):
        pass

    def goto(self, t):
        return Goto(t.value)

    def mark(self, value):
        return Mark(value)

    def advance(self):
        return Advance()

    def retract(self, i):
        return Retract()

    def advance_consume(self):
        return (Advance(), Consume(False))

    def consume(self):
        return Consume(False)

    def produce(self, t = None):
        return Produce(t.value if t else None)

    def string(self, t):
        # TODO: escape according to actual C rules
        v = t.value[1:-1]
        v = v.decode('string_escape')
        return v

    def int(self, t):
        return int(t.value)

    def hex(self, t1, t2):
        return chr(bytearray.fromhex(t1.value + t2.value)[0])



with open('fsm.c') as fd:
    data = fd.read()

parser = Lark(GRAMMAR, parser='lalr', lexer='contextual', transformer=Re2cTransformer())
lexer = parser.parse(data)

_lex = lexer.compile(str_type=str, debug=False, annotate=False)
# import dis; print(dis.dis(_lex))

def lex(stream, ofs=0, sentinel='\0'):
    try:
        while True:
            end, token = _lex(stream, ofs)
            if token is None:
                raise RuntimeError('Unexpected char {} at {}'.format(repr(stream[ofs]), ofs))

            assert end > ofs, 'lexer did not advance nor failed'

            yield ofs, token, stream[ofs:end]
            ofs = end
    except IndexError:
        # Retry with a sentinel to try to extract a last token
        yield next(lex(stream[ofs:] + sentinel))

