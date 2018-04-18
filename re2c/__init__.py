from __future__ import print_function

import codecs
import os
import sys
import subprocess
import tempfile
from functools import partial

from lark.load_grammar import load_grammar
from lark.common import PatternStr, PatternRE

from re2c.regex import RegexParser
from re2c.parser import parse
from re2c.fsm import build, wrapper


def transform_grammar(grammar):
    g = load_grammar(grammar)
    tokens, rules, ignore_tokens = g.compile(lexer=True)

    tokens.sort(key=lambda t: (-t.priority, -1 if isinstance(t.pattern, PatternStr) else 1, -t.pattern.max_width))

    rules = []
    for token in tokens:
        if isinstance(token.pattern, PatternStr):
            if 'i' in token.pattern.flags:
                regexes = ["'{}'".format(token.pattern.value)]
            else:
                regexes = ['"{}"'.format(token.pattern.value)]
        else:
            if 'i' in token.pattern.flags:
                raise SyntaxError('Case insensitive regular expressions are not supported ({})'.format(token.name))
            else:
                try:
                    parser = RegexParser(token.pattern.flags)
                    asts = parser.parse(token.pattern.to_regexp())
                    regexes = [repr(ast) for ast in asts]
                except SyntaxError as ex:
                    raise SyntaxError('{0} ({1})'.format(ex, token.name))

        for regex in regexes:
            rules.append((regex, token.name, token.pattern.value.encode('unicode_escape')))

    return rules


def lark2re2c(rules, binary=False, unicode=False, re2c_bin=None):
    if not re2c_bin:
        re2c_bin = os.environ.get('RE2C', 're2c')

    args = [re2c_bin, '-s']

    if unicode:
        args.append('-u')
    elif not binary:
        args.append('-8')

    tmpfd, fpath = tempfile.mkstemp()
    try:
        with codecs.open(fpath, 'w', encoding='utf-8') as fd:
            print('/*!re2c', file=fd)
            print('re2c:yyfill:enable = 0;', file=fd)
            for rule in rules:
                print("{0:60} {{ {1} }}  // {2}".format(rule[0], rule[1], rule[2]), file=fd)
            print('*  { None }', file=fd)
            print('*/', file=fd)

        args.append(fpath)
        return subprocess.check_output(args)
    finally:
        os.remove(fpath)


def build_lexer(grammar, char_type=str, name='re2c'):
    try:
        unicode = unicode
    except:
        unicode = str

    rules = transform_grammar(grammar)
    ccode = lark2re2c(rules, binary=char_type is bytes, unicode=char_type is unicode)
    fsm = parse(ccode)
    asm = fsm.assemble(name=name)

    _lex = build(asm, char_type=char_type)
    return partial(wrapper, _lex)
