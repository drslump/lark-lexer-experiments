import pytest


@pytest.fixture
def data():
    return open('test.g').read() * 10


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
                end = m.end()
                value = m.group(0)
                yield ofs, token, value
                ofs = end
                continue

            raise RuntimeError('Unexpected character {} at {}'.format(repr(stream[ofs]), ofs))

    return lex


@pytest.fixture
def lex_fsm():
    try:
        import fsm_lexer
    except:
        import gen_fsm_lexer as fsm_lexer

    return fsm_lexer.lex


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


def recompose(lexer):
    parts = []
    for ofs, token, value in lexer:
        parts.append(value)
    return ''.join(parts).split('\n')


def test_regex(benchmark, data, lex_regex):
    assert data.split('\n') == recompose(lex_regex(data))
    benchmark(lambda: list(lex_regex(data)))

def test_fsm(benchmark, data, lex_fsm):
    assert data.split('\n') == recompose(lex_fsm(data))
    benchmark(lambda: list(lex_fsm(data)))

def test_c(benchmark, data, lex_c):
    assert data.split('\n') == recompose(lex_c(data))
    benchmark(lambda: list(lex_c(data)))

def test_cseq(benchmark, data, lex_cseq):
    assert data.split('\n') == recompose(lex_cseq(data))
    benchmark(lambda: list(lex_cseq(data)))
