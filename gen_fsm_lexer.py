# Generated from fsm_lexer repr()

from fsm import *


lexer = State(None, [
  Mark(0),
  Consume(advance=False),
  If('<=', '.', [If('<=', '"', [If('<=', '\x0c', [If('<=', '\x08', [Goto('yy2')], [], varname='yych'), If('<=', '\t', [Goto('yy4')], [], varname='yych'), If('<=', '\n', [Goto('yy7')], [], varname='yych')], [If('<=', '\x1f', [If('<=', '\r', [Goto('yy10')], [], varname='yych')], [If('<=', ' ', [Goto('yy4')], [], varname='yych'), If('<=', '!', [Goto('yy11')], [], varname='yych'), Goto('yy12')], varname='yych')], varname='yych')], [If('<=', '(', [If('in', '%', [Goto('yy13')], [], varname='yych'), If('>=', '(', [Goto('yy14')], [], varname='yych')], [If('<=', '+', [If('<=', ')', [Goto('yy16')], [], varname='yych'), Goto('yy18')], [If('<=', ',', [Goto('yy2')], [], varname='yych'), If('<=', '-', [Goto('yy20')], [], varname='yych'), Goto('yy21')], varname='yych')], varname='yych')], varname='yych')], [If('<=', '\\', [If('<=', '>', [If('<=', '/', [Goto('yy23')], [], varname='yych'), If('in', ':', [Goto('yy24')], [], varname='yych')], [If('<=', '@', [If('<=', '?', [Goto('yy26')], [], varname='yych')], [If('<=', 'Z', [Goto('yy27')], [], varname='yych'), If('<=', '[', [Goto('yy30')], [], varname='yych')], varname='yych')], varname='yych')], [If('<=', 'z', [If('<=', '^', [If('<=', ']', [Goto('yy32')], [], varname='yych')], [If('<=', '_', [Goto('yy34')], [], varname='yych'), If('>=', 'a', [Goto('yy35')], [], varname='yych')], varname='yych')], [If('<=', '|', [If('>=', '|', [Goto('yy38')], [], varname='yych')], [If('in', '~', [Goto('yy40')], [], varname='yych')], varname='yych')], varname='yych')], varname='yych')], varname='yych'),
  State('yy2', [
    Advance()
  ]),
  State('yy3', [
    Produce(None)
  ]),
  State('yy4', [
    Advance(),
    Consume(advance=False),
    If('in', '\t', [Goto('yy4')], [], varname='yych'),
    If('in', ' ', [Goto('yy4')], [], varname='yych'),
    Produce('WS')
  ]),
  State('yy7', [
    Mark(0),
    Advance(),
    Consume(advance=False),
    If('<=', '\x0c', [If('<=', '\x08', [Goto('yy9')], [], varname='yych'), If('<=', '\t', [Goto('yy42')], [], varname='yych'), If('<=', '\n', [Goto('yy7')], [], varname='yych')], [If('<=', '\r', [Goto('yy44')], [], varname='yych'), If('in', ' ', [Goto('yy42')], [], varname='yych')], varname='yych')
  ]),
  State('yy9', [
    Produce('NL')
  ]),
  State('yy10', [
    Advance(),
    Consume(advance=False),
    If('in', '\n', [Goto('yy7')], [], varname='yych'),
    Goto('yy3')
  ]),
  State('yy11', [
    Mark(1),
    Advance(),
    Consume(advance=False),
    If('<=', '^', [If('in', '?', [Goto('yy46')], [], varname='yych'), Goto('yy3')], [If('<=', '_', [Goto('yy46')], [], varname='yych'), If('<=', '`', [Goto('yy3')], [], varname='yych'), If('<=', 'z', [Goto('yy35')], [], varname='yych'), Goto('yy3')], varname='yych')
  ]),
  State('yy12', [
    Mark(1),
    Advance(),
    Consume(advance=False),
    If('in', '\n', [Goto('yy3')], [], varname='yych'),
    Goto('yy48')
  ]),
  State('yy13', [
    Mark(1),
    Advance(),
    Consume(advance=False),
    If('in', 'i', [Goto('yy53')], [], varname='yych'),
    Goto('yy3')
  ]),
  State('yy14', [
    Advance(),
    Produce('LPAR')
  ]),
  State('yy16', [
    Advance(),
    Produce('RPAR')
  ]),
  State('yy18', [
    Advance(),
    Consume(advance=False),
    If('in', '?', [Goto('yy54')], [], varname='yych'),
    If('<=', '`', [Goto('yy19')], [], varname='yych'),
    If('<=', 'z', [Goto('yy55')], [], varname='yych')
  ]),
  State('yy19', [
    Produce('OP')
  ]),
  State('yy20', [
    Advance(),
    Consume(advance=False),
    If('in', '>', [Goto('yy57')], [], varname='yych'),
    Goto('yy3')
  ]),
  State('yy21', [
    Advance(),
    Produce('DOT')
  ]),
  State('yy23', [
    Mark(1),
    Advance(),
    Consume(advance=False),
    If('in', '/', [Goto('yy61')], [], varname='yych'),
    Goto('yy59')
  ]),
  State('yy24', [
    Advance(),
    Produce('COLON')
  ]),
  State('yy26', [
    Advance(),
    Consume(advance=False),
    If('<=', '`', [Goto('yy62')], [], varname='yych'),
    If('<=', 'z', [Goto('yy35')], [], varname='yych'),
    Goto('yy62')
  ]),
  State('yy27', [
    Advance(),
    Consume(advance=False),
    If('<=', '@', [If('<=', '/', [Goto('yy29')], [], varname='yych'), If('<=', '9', [Goto('yy27')], [], varname='yych')], [If('<=', 'Z', [Goto('yy27')], [], varname='yych'), If('in', '_', [Goto('yy27')], [], varname='yych')], varname='yych')
  ]),
  State('yy29', [
    Produce('TOKEN')
  ]),
  State('yy30', [
    Advance(),
    Produce('LBRA')
  ]),
  State('yy32', [
    Advance(),
    Produce('RBRA')
  ]),
  State('yy34', [
    Advance(),
    Consume(advance=False),
    If('<=', '@', [Goto('yy3')], [], varname='yych'),
    If('<=', 'Z', [Goto('yy27')], [], varname='yych'),
    If('<=', '`', [Goto('yy3')], [], varname='yych'),
    If('>=', '{', [Goto('yy3')], [], varname='yych')
  ]),
  State('yy35', [
    Advance(),
    Consume(advance=False),
    If('<=', '^', [If('<=', '/', [Goto('yy37')], [], varname='yych'), If('<=', '9', [Goto('yy35')], [], varname='yych')], [If('in', '`', [Goto('yy37')], [], varname='yych'), If('<=', 'z', [Goto('yy35')], [], varname='yych')], varname='yych')
  ]),
  State('yy37', [
    Produce('RULE')
  ]),
  State('yy38', [
    Advance(),
    Produce('OR')
  ]),
  State('yy40', [
    Advance(),
    Produce('TILDE')
  ]),
  State('yy42', [
    Advance(),
    Consume(advance=False),
    If('in', '\t', [Goto('yy42')], [], varname='yych'),
    If('in', ' ', [Goto('yy42')], [], varname='yych'),
    Goto('yy9')
  ]),
  State('yy44', [
    Advance(),
    Consume(advance=False),
    If('in', '\n', [Goto('yy7')], [], varname='yych')
  ]),
  State('yy45', [
    Backtrack({}),
    If('<=', '\x01', [If('==', '\x00', [Goto('yy9')], [Goto('yy3')], varname='yyaccept')], [If('==', '\x02', [Goto('yy50')], [Goto('yy69')], varname='yyaccept')], varname='yyaccept')
  ]),
  State('yy46', [
    Advance(),
    Consume(advance=False),
    If('<=', '`', [Goto('yy45')], [], varname='yych'),
    If('<=', 'z', [Goto('yy35')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy47', [
    Advance(),
    Consume(advance=False)
  ]),
  State('yy48', [
    If('<=', '!', [If('in', '\n', [Goto('yy45')], [], varname='yych'), Goto('yy47')], [If('<=', '"', [Goto('yy49')], [], varname='yych'), If('in', '\\', [Goto('yy51')], [], varname='yych'), Goto('yy47')], varname='yych')
  ]),
  State('yy49', [
    Advance(),
    Consume(advance=False),
    If('in', 'i', [Goto('yy63')], [], varname='yych')
  ]),
  State('yy50', [
    Produce('STRING')
  ]),
  State('yy51', [
    Advance(),
    Consume(advance=False),
    If('<=', '!', [If('in', '\n', [Goto('yy45')], [], varname='yych'), Goto('yy47')], [If('<=', '"', [Goto('yy64')], [], varname='yych'), If('in', '\\', [Goto('yy51')], [], varname='yych'), Goto('yy47')], varname='yych')
  ]),
  State('yy53', [
    Advance(),
    Consume(advance=False),
    If('in', 'g', [Goto('yy65')], [], varname='yych'),
    If('in', 'm', [Goto('yy66')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy54', [
    Advance(),
    Consume(advance=False),
    If('<=', '`', [Goto('yy19')], [], varname='yych'),
    If('>=', '{', [Goto('yy19')], [], varname='yych')
  ]),
  State('yy55', [
    Advance(),
    Retract(),
    Produce('OP')
  ]),
  State('yy57', [
    Advance(),
    Produce('TO')
  ]),
  State('yy59', [
    Advance(),
    Consume(advance=False),
    If('<=', '.', [If('in', '\n', [Goto('yy45')], [], varname='yych'), Goto('yy59')], [If('<=', '/', [Goto('yy67')], [], varname='yych'), If('in', '\\', [Goto('yy70')], [], varname='yych'), Goto('yy59')], varname='yych')
  ]),
  State('yy61', [
    Advance(),
    Consume(advance=False),
    If('in', '\n', [Goto('yy45')], [], varname='yych'),
    Goto('yy72')
  ]),
  State('yy62', [
    Advance(),
    Goto('yy19')
  ]),
  State('yy63', [
    Advance(),
    Goto('yy50')
  ]),
  State('yy64', [
    Mark(2),
    Advance(),
    Consume(advance=False),
    If('<=', '"', [If('in', '\n', [Goto('yy50')], [], varname='yych'), If('<=', '!', [Goto('yy47')], [], varname='yych'), Goto('yy49')], [If('<=', '\\', [If('<=', '[', [Goto('yy47')], [], varname='yych'), Goto('yy51')], [If('in', 'i', [Goto('yy75')], [], varname='yych'), Goto('yy47')], varname='yych')], varname='yych')
  ]),
  State('yy65', [
    Advance(),
    Consume(advance=False),
    If('in', 'n', [Goto('yy76')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy66', [
    Advance(),
    Consume(advance=False),
    If('in', 'p', [Goto('yy77')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy67', [
    Advance(),
    Consume(advance=False),
    If('in', 'ilmsux', [Goto('yy67')], [], varname='yych'),
    Goto('yy69')
  ]),
  State('yy69', [
    Produce('REGEXP')
  ]),
  State('yy70', [
    Advance(),
    Consume(advance=False),
    If('<=', '.', [If('in', '\n', [Goto('yy45')], [], varname='yych'), Goto('yy59')], [If('<=', '/', [Goto('yy78')], [], varname='yych'), If('in', '\\', [Goto('yy70')], [], varname='yych'), Goto('yy59')], varname='yych')
  ]),
  State('yy72', [
    Advance(),
    Consume(advance=False),
    If('!=', '\n', [Goto('yy72')], [], varname='yych'),
    Produce('COMMENT')
  ]),
  State('yy75', [
    Mark(2),
    Advance(),
    Consume(advance=False),
    If('<=', '!', [If('in', '\n', [Goto('yy50')], [], varname='yych'), Goto('yy47')], [If('<=', '"', [Goto('yy49')], [], varname='yych'), If('in', '\\', [Goto('yy51')], [], varname='yych'), Goto('yy47')], varname='yych')
  ]),
  State('yy76', [
    Advance(),
    Consume(advance=False),
    If('in', 'o', [Goto('yy80')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy77', [
    Advance(),
    Consume(advance=False),
    If('in', 'o', [Goto('yy81')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy78', [
    Mark(3),
    Advance(),
    Consume(advance=False),
    If('<=', 'i', [If('<=', '/', [If('in', '\n', [Goto('yy69')], [], varname='yych'), If('<=', '.', [Goto('yy59')], [], varname='yych'), Goto('yy67')], [If('in', '\\', [Goto('yy70')], [], varname='yych'), If('<=', 'h', [Goto('yy59')], [], varname='yych'), Goto('yy78')], varname='yych')], [If('<=', 's', [If('<=', 'k', [Goto('yy59')], [], varname='yych'), If('<=', 'm', [Goto('yy78')], [], varname='yych'), If('<=', 'r', [Goto('yy59')], [], varname='yych'), Goto('yy78')], [If('<=', 'u', [If('<=', 't', [Goto('yy59')], [], varname='yych'), Goto('yy78')], [If('in', 'x', [Goto('yy78')], [], varname='yych'), Goto('yy59')], varname='yych')], varname='yych')], varname='yych')
  ]),
  State('yy80', [
    Advance(),
    Consume(advance=False),
    If('in', 'r', [Goto('yy82')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy81', [
    Advance(),
    Consume(advance=False),
    If('in', 'r', [Goto('yy83')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy82', [
    Advance(),
    Consume(advance=False),
    If('in', 'e', [Goto('yy84')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy83', [
    Advance(),
    Consume(advance=False),
    If('in', 't', [Goto('yy86')], [], varname='yych'),
    Goto('yy45')
  ]),
  State('yy84', [
    Advance(),
    Produce('IGNORE')
  ]),
  State('yy86', [
    Advance(),
    Produce('IMPORT')
  ])
])

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
