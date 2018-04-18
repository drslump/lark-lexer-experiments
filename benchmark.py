import pytest


@pytest.fixture
def data():
    return open('grammar.g').read() * 100


@pytest.fixture
def py_data():
    return open(__file__).read() * 100


@pytest.fixture
def lex_regex():
    import re
    rex = re.compile(r'''
        (?P<REGEXP>/(?!/)(\\/|\\\\|[^/\n])*?/[imslux]*)
        |(?P<_NL>(\r?\n)+\s*)
        |(?P<STRING>"(\\"|\\\\|[^"\n])*?"i?)
        |(?P<RULE>!?[_?]?[a-z][_a-z0-9]*)
        |(?P<TOKEN>_?[A-Z][_A-Z0-9]*)
        |(?P<WS>[ \t]+)
        |(?P<NUMBER>\d+)
        |(?P<_IGNORE>%ignore)
        |(?P<_IMPORT>%import)
        |(?P<OP>[+*][?]?|[?](?![a-z]))
        |(?P<_TO>->)
        |(?P<_DOT>\.)
        |(?P<_LBRA>\[)
        |(?P<_LPAR>\()
        |(?P<_OR>\|)
        |(?P<_RBRA>\])
        |(?P<_RPAR>\))
        |(?P<TILDE>~)
        |(?P<_COLON>:)
    ''', re.X)

    types = {
        1: 'REGEXP', 3: '_NL', 5: 'STRING', 7: 'RULE', 8: 'TOKEN', 9: 'WS',
        10: 'NUMBER', 11: '_IGNORE', 12: '_IMPORT', 13: 'OP', 14: '_TO', 15: '_DOT',
        16: '_LBRA', 17: '_LPAR', 18: '_OR', 19: '_RBRA', 20: '_RPAR', 21: 'TILDE',
        22: '_COLON'
    }

    def lex(stream):
        ofs = 0
        while ofs < len(stream):
            m = rex.match(stream, ofs)
            if m:
                token = types[m.lastindex]
                ofs, end = m.span(m.lastindex)
                yield ofs, token, stream[ofs:end]
                ofs = end
                continue

            raise RuntimeError('Unexpected character {} at {}'.format(repr(stream[ofs]), ofs))

    return lex


@pytest.fixture
def lex_fsm():
    try:
        from re2c import build_lexer
        with open('grammar.g') as fd:
            return build_lexer(fd.read(), char_type=str)
    except:
        from warnings import warn
        warn('Unable to build re2c on-demand, falling back to pre-generated re2c_lexer.py')

        from re2c_lexer import lex
        return lex


@pytest.fixture
def lex_c():
    from _lexer import lex

    def clex(stream):
        ofs = 0
        length = len(stream)
        while ofs < length:
            pos, token = lex(stream, ofs)
            if token is None:
                break

            assert pos > ofs

            yield ofs, token, stream[ofs:pos]
            ofs = pos

    return clex


@pytest.fixture
def lex_cseq():
    from _lexer import lexseq

    def clexseq(stream):
        ofs = 0
        for end, token in lexseq(stream):
            yield ofs, token, stream[ofs:end]
            ofs = end

    return clexseq


@pytest.fixture
def py_lex_regex():
    import re

    rex = re.compile(r'''
        (?P<LONG_STRING>(?s)(?i)[ubf]?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\'))
        |(?P<_NEWLINE>(?:(?:\r?\n[\t ]*|\#[^\n]*))+)
        |(?P<IMAG_NUMBER>(?:(?:[0-9])+|(?:(?:[0-9])+(?:e|E)(?:(?:\+|\-))?(?:[0-9])+|(?:(?:[0-9])+\.(?:(?:[0-9])+)?|\.(?:[0-9])+)(?:(?:e|E)(?:(?:\+|\-))?(?:[0-9])+)?))(?:j|J))
        |(?P<STRING>(?i)[ubf]?r?("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?'))
        |(?P<FLOAT>(?:(?:[0-9])+(?:e|E)(?:(?:\+|\-))?(?:[0-9])+|(?:(?:[0-9])+\.(?:(?:[0-9])+)?|\.(?:[0-9])+)(?:(?:e|E)(?:(?:\+|\-))?(?:[0-9])+)?))
        |(?P<HEX_NUMBER>(?i)0x[\da-f]*l?)
        |(?P<OCT_NUMBER>(?i)0o?[0-7]*l?)
        |(?P<DEC_NUMBER>(?i)[1-9]\d*l?)
        |(?P<NAME>(?:\_|(?:[A-Z]|[a-z]))(?:(?:(?:\_|(?:[A-Z]|[a-z]))|[0-9]))*)
        |(?P<COMMENT>\#[^\n]*)
        |(?P<_INT>(?:[0-9])+)
        |(?P<_DEDENT>\<DEDENT\>)
        |(?P<_INDENT>\<INDENT\>)
        |(?P<__ANONSTR_10>\<\<\=)
        |(?P<__ANONSTR_11>\>\>\=)
        |(?P<__ANONSTR_12>\*\*\=)
        |(?P<__ANONSTR_13>\/\/\=)
        |(?P<__ANONSTR_1>\*\*)
        |(?P<__ANONSTR_15>\>\>)
        |(?P<__ANONSTR_2>\+\=)
        |(?P<__ANONSTR_3>\-\=)
        |(?P<__ANONSTR_4>\*\=)
        |(?P<__ANONSTR_42>\=\=)
        |(?P<__ANONSTR_43>\>\=)
        |(?P<__ANONSTR_44>\<\=)
        |(?P<__ANONSTR_45>\<\>)
        |(?P<__ANONSTR_46>\!\=)
        |(?P<__ANONSTR_48>\<\<)
        |(?P<__ANONSTR_49>\/\/)
        |(?P<__ANONSTR_5>\/\=)
        |(?P<__ANONSTR_6>\%\=)
        |(?P<__ANONSTR_7>\&\=)
        |(?P<__ANONSTR_8>\|\=)
        |(?P<__ANONSTR_9>\^\=)
        |(?P<__AMPERSAND>\&)
        |(?P<__AT>\@)
        |(?P<__BACKQUOTE>\`)
        |(?P<__CIRCUMFLEX>\^)
        |(?P<__COLON>\:)
        |(?P<__COMMA>\,)
        |(?P<__DOT>\.)
        |(?P<__EQUAL>\=)
        |(?P<__LBRACE>\{)
        |(?P<__LESSTHAN>\<)
        |(?P<__LPAR>\()
        |(?P<__LSQB>\[)
        |(?P<__MINUS>\-)
        |(?P<__MORETHAN>\>)
        |(?P<__PERCENT>\%)
        |(?P<__PLUS>\+)
        |(?P<__RBRACE>\})
        |(?P<__RPAR>\))
        |(?P<__RSQB>\])
        |(?P<__SEMICOLON>\;)
        |(?P<__SLASH>\/)
        |(?P<__STAR>\*)
        |(?P<__TILDE>\~)
        |(?P<__VBAR>\|)
        |(?P<__IGNORE_1>\\[\t \x0c]*\r?\n)
        |(?P<__IGNORE_0>[\t \x0c]+)
        ''', re.X)

    types = {
        1: u'LONG_STRING', 5: u'_NEWLINE', 6: u'IMAG_NUMBER', 7: u'STRING',
        11: u'FLOAT', 12: u'HEX_NUMBER', 13: u'OCT_NUMBER', 14: u'DEC_NUMBER',
        15: u'NAME', 16: u'COMMENT', 17: u'_INT', 18: u'_DEDENT', 19: u'_INDENT',
        20: u'__ANONSTR_10', 21: u'__ANONSTR_11', 22: u'__ANONSTR_12',
        23: u'__ANONSTR_13', 24: u'__ANONSTR_1', 25: u'__ANONSTR_15',
        26: u'__ANONSTR_2', 27: u'__ANONSTR_3', 28: u'__ANONSTR_4',
        29: u'__ANONSTR_42', 30: u'__ANONSTR_43', 31: u'__ANONSTR_44',
        32: u'__ANONSTR_45', 33: u'__ANONSTR_46', 34: u'__ANONSTR_48',
        35: u'__ANONSTR_49', 36: u'__ANONSTR_5', 37: u'__ANONSTR_6',
        38: u'__ANONSTR_7', 39: u'__ANONSTR_8', 40: u'__ANONSTR_9',
        41: u'__AMPERSAND', 42: u'__AT', 43: u'__BACKQUOTE', 44: u'__CIRCUMFLEX',
        45: u'__COLON', 46: u'__COMMA', 47: u'__DOT', 48: u'__EQUAL', 49: u'__LBRACE',
        50: u'__LESSTHAN', 51: u'__LPAR', 52: u'__LSQB', 53: u'__MINUS',
        54: u'__MORETHAN', 55: u'__PERCENT', 56: u'__PLUS', 57: u'__RBRACE',
        58: u'__RPAR', 59: u'__RSQB', 60: u'__SEMICOLON', 61: u'__SLASH',
        62: u'__STAR', 63: u'__TILDE', 64: u'__VBAR', 65: u'__IGNORE_1',
        66: u'__IGNORE_0'}


    def lex(stream):
        ofs = 0
        while ofs < len(stream):
            m = rex.match(stream, ofs)
            if m:
                token = types[m.lastindex]
                ofs, end = m.span(m.lastindex)
                yield ofs, token, stream[ofs:end]
                ofs = end
                continue

            raise RuntimeError('Unexpected character {} at {}'.format(repr(stream[ofs]), ofs))

    return lex


@pytest.fixture
def py_lex_fsm():
    try:
        from re2c import build_lexer
        with open('python2.g') as fd:
            return build_lexer(fd.read(), char_type=str)
    except:
        from warnings import warn
        warn('Unable to build re2c on-demand, falling back to pre-generated re2c_py_lexer.py')

        from re2c_py_lexer import lex
        return lex


@pytest.fixture
def py_lex_c():
    from _lexer import lex

    def clex(stream):
        ofs = 0
        length = len(stream)
        while ofs < length:
            pos, token = lex(stream, ofs)
            if token is None:
                break

            assert pos > ofs

            yield ofs, token, stream[ofs:pos]
            ofs = pos

    return clex


@pytest.fixture
def py_lex_cseq():
    from _lexer import lexseq

    def clexseq(stream):
        ofs = 0
        for end, token in lexseq(stream):
            yield ofs, token, stream[ofs:end]
            ofs = end

    return clexseq


def recompose(lexer):
    parts = []
    for ofs, token, value in lexer:
        parts.append(value)
    return ''.join(parts).split('\n')


# def test_regex(benchmark, data, lex_regex):
#     assert data.split('\n') == recompose(lex_regex(data))
#     result = benchmark(lambda: list(lex_regex(data)))
#     assert data.split('\n') == recompose(result)

# def test_fsm(benchmark, data, lex_fsm):
#     assert data.split('\n') == recompose(lex_fsm(data))
#     result = benchmark(lambda: list(lex_fsm(data)))
#     assert data.split('\n') == recompose(result)

# def test_c(benchmark, data, lex_c):
#     assert data.split('\n') == recompose(lex_c(data))
#     result = benchmark(lambda: list(lex_c(data)))
#     assert data.split('\n') == recompose(result)

# def test_cseq(benchmark, data, lex_cseq):
#     assert data.split('\n') == recompose(lex_cseq(data))
#     result = benchmark(lambda: list(lex_cseq(data)))
#     assert data.split('\n') == recompose(result)

def test_py_regex(benchmark, py_data, py_lex_regex):
    assert py_data.split('\n') == recompose(py_lex_regex(py_data))
    result = benchmark(lambda: list(py_lex_regex(py_data)))
    assert py_data.split('\n') == recompose(result)

def test_py_fsm(benchmark, py_data, py_lex_fsm):
    assert py_data.split('\n') == recompose(py_lex_fsm(py_data))
    result = benchmark(lambda: list(py_lex_fsm(py_data)))
    assert py_data.split('\n') == recompose(result)

# def test_py_c(benchmark, py_data, py_lex_c):
#     assert py_data.split('\n') == recompose(py_lex_c(py_data))
#     result = benchmark(lambda: list(py_lex_c(py_data)))
#     assert py_data.split('\n') == recompose(result)

# def test_py_cseq(benchmark, py_data, py_lex_cseq):
#     assert py_data.split('\n') == recompose(py_lex_cseq(py_data))
#     result = benchmark(lambda: list(py_lex_cseq(py_data)))
#     assert py_data.split('\n') == recompose(result)
