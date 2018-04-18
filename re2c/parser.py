from lark import Lark, InlineTransformer

from re2c.fsm import *


GRAMMAR = r'''
    start       : "{" main state+ "}"
    main        : stmt+
    state       : LABEL ":" stmt+

    ?stmt       : expr ";"
                | switch
                | if_stmt
                | "{" CNAME? "}"   -> produce

    switch      : "switch" "(" CNAME ")" "{" case+ default? "}"
    case        : ( "case" literal ":" )+ case_block
    default     : "default" ":" case_block
    case_block  : ( expr ";" )+

    if_stmt     : "if" "(" CNAME OP literal ")" if_block [ "else" if_block ]

    if_block    : "{" stmt+ "}"
                | stmt

    ?expr       : CNAME+ CNAME [ "=" literal ]          -> decl
                | "goto" LABEL                          -> goto
                | "++YYCURSOR"                          -> advance
                | "yych" "=" "*YYCURSOR"                -> consume
                | "yych" "=" "*++YYCURSOR"              -> advance_consume
                | "yych" "=" "*(YYMARKER = ++YYCURSOR)" -> advance_save_consume
                | "yyaccept" "=" literal                -> mark
                | "YYCURSOR" "=" "YYMARKER"             -> backtrack
                | "YYCURSOR" "-=" literal               -> retract
                | "YYCTXMARKER" "=" "YYCURSOR"          -> context_save
                | "YYCURSOR" "=" "YYCTXMARKER"          -> context_restore

    ?literal    : STRING                  -> string
                | INT                     -> int
                | "0x" HEXDIGIT+          -> hex

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
        return self._state_factory(None, [
            main,
            states
        ])

    def main(self, *stmts):
        return self._state_factory('$START', [Mark(0)] + list(stmts))

    def state(self, t_label, *stmts):
        return self._state_factory(t_label.value, stmts)

    def switch(self, t_var, *cases):
        # boost tests for whitespace, newlines and numbers
        def sortkey(iff):
            if iff.op in ('in', '=='):
                if ' ' in iff.test:
                    return -100
                elif '\n' in iff.test:
                    return -10
                elif '0' in iff.test:
                    return -1
            return ord(iff.test[0])

        cases = list(cases)
        if isinstance(cases[-1], list):
            default = cases.pop()
        else:
            default = []

        cases.sort(key=sortkey)

        cases.extend(default)
        return cases

    def case(self, *args):
        assert len(args) >= 2

        args = list(args)
        block = args.pop()

        if type(args[0]) is int:
            assert len(args) == 1
            return If('yyaccept', '==', args[0], block)

        buffer = bytearray()
        for arg in args:
            buffer.extend(arg)

        return If('yych', 'in', bytes(buffer), block)

    def case_block(self, *exprs):
        return list(exprs)

    def default(self, block):
        return block

    def if_stmt(self, t_var, t_op, rhs, true, false=None):
        return If(t_var.value, t_op.value, rhs, true, false)

    def if_block(self, *stmts):
        return list(stmts)

    def backtrack(self):
        return Restore('YYMARKER')

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
        return (Advance(), Consume())

    def advance_save_consume(self):
        return (Advance(), Save('YYMARKER'), Consume())

    def consume(self):
        return Consume()

    def produce(self, t = None):
        return Produce(t.value if t else None)

    def context_save(self):
        return Save('YYCTXMARKER')

    def context_restore(self):
        return Restore('YYCTXMARKER')

    def string(self, t):
        #XXX escape according to actual C rules
        v = t.value[1:-1]
        v = v.decode('string_escape')
        return v

    def int(self, t):
        return int(t.value)

    def hex(self, *t_digit):
        digits = ''.join(t.value for t in t_digit)
        return chr(int(digits, 16))


def parse(re2c):
    parser = Lark(GRAMMAR, parser='lalr', lexer='contextual', transformer=Re2cTransformer())
    return parser.parse(re2c)
