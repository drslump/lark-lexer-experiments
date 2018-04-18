"""
Parses a Python regex generating an AST compatible with re2c
"""

import re
import sre_parse
import sre_constants


def escape(chars, quotes):
    mapping = {'\n': r'\n', '\r': r'\r', '\t': r'\t', '\f': r'\f', '\b': r'\b'}

    escaped = []
    for ch in chars:
        if ch in mapping:
            ch = mapping[ch]
        elif ch < chr(0x20) or ch > chr(0x7E):
            ch = r'\x{:02X}'.format(ord(ch))

        if ch == '\\':
            ch = '\\\\'
        elif ch in quotes:
            ch = '\\' + ch

        escaped.append(ch)

    return ''.join(escaped)


class Chars(object):
    def __init__(self, chars):
        self.chars = chars

    def __iter__(self):
        return iter(self.chars)

    def __repr__(self):
        return '"' + escape(self.chars, '"') + '"'


class Choice(object):
    def __init__(self, exprs, negated=False):
        self.exprs = exprs
        self.negated = negated

    def __repr__(self):
        if not self.negated and len(self.exprs) == 1:
            if isinstance(self.exprs[0], Chars):
                return '"' + repr(sel.exprs[0]) + '"'

        parts = ['[']
        if self.negated:
            parts.append('^')

        for expr in self.exprs:
            if isinstance(expr, tuple):
                parts.append(escape(expr[0], ']^-'))
                parts.append('-')
                parts.append(escape(expr[1], ']^-'))
            else:
                parts.append(escape(expr, ']^-'))

        parts.append(']')
        return ''.join(parts)


class Repeat(object):
    def __init__(self, min, max, expr):
        self.min = min
        self.max = max
        self.expr = expr

    def __repr__(self):
        if self.min == 0 and self.max == 1:
            op = '?'
        elif self.min == 0 and self.max == sre_constants.MAXREPEAT:
            op = '*'
        elif self.min == 1 and self.max == sre_constants.MAXREPEAT:
            op = '+'
        elif self.min == self.max:
            op = '{' + str(self.min) + '}'
        elif self.max == sre_constants.MAXREPEAT:
            op = '{' + str(self.min) + ',}'
        else:
            op = '{' + str(self.min) + ',' + str(self.max) + '}'

        result = repr(self.expr)
        if isinstance(self.expr, (Sequence, Alternates)):
            result = '( ' + result + ' )'

        return '{}{}'.format(result, op)


class Sequence(object):
    def __new__(cls, exprs):
        # pack runs of characters
        result = []
        for i,expr in enumerate(exprs):
            if len(result) and isinstance(expr, Chars) and isinstance(result[-1], Chars):
                result[-1].chars += expr.chars
            else:
                result.append(expr)

        # Fold if it's just one element
        if len(result) == 1:
            return result[0]

        for expr in result:
            if isinstance(expr, LookAhead) and expr is not result[-1]:
                raise SyntaxError('LookAhead (?=) is only supported at the tail')

        self = super(Sequence, cls).__new__(cls)
        self.exprs = result
        return self

    def __repr__(self):
        items = []
        for expr in self.exprs:
            if isinstance(expr, Alternates):
                items.append('(' + repr(expr) + ')')
                continue

            items.append(repr(expr))

        return ' '.join(items)


class Alternates(object):
    def __new__(cls, exprs):
        # Fold if it's just one element
        exprs = list(exprs)
        if len(exprs) == 1:
            return exprs[0]

        self = super(Alternates, cls).__new__(cls)
        self.exprs = exprs
        return self

    def __repr__(self):
        items = []
        for expr in self.exprs:
            if isinstance(expr, Alternates):
                items.append('(' + repr(expr) + ')')
                continue

            items.append(repr(expr))

        return ' | '.join(items)


class LookAhead(object):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '/ ' + repr(self.expr)


class Any(object):
    __slots__ = ('dotall',)

    def __init__(self, dotall):
        self.dotall = dotall

    def __repr__(self):
        return '[^]' if self.dotall else '.'


class RegexParser(object):

    def __init__(self, flags=''):
        self.dotall = 's' in flags
        self.rules = {}

        rules = (x[len('rule_'):] for x in self.__dict__.keys() if x.startswith('rule_'))
        for rule in rules:
            const = getattr(sre_constants, rule.upper())
            self.rules[const] = getattr(self, 'rule_' + rule)

    def parse(self, rex):
        parsed = sre_parse.parse(rex)
        ast = Sequence(self.recurse(parsed))

        if isinstance(ast, Alternates):
            return ast.exprs

        return [ ast ]

    def recurse(self, data):
        if hasattr(data, 'data'):
            data = data.data

        if isinstance(data, list):
            return [self.recurse(x) for x in data]

        action, params = data

        fn = getattr(self, 'rule_' + action, None)
        if not fn:
            raise SyntaxError('Unsupported regex construct: {}'.format(action))

        return fn(params)

    def rule_literal(self, charcode):
        return Chars(chr(charcode))

    def rule_not_literal(self, charcode):
        return Choice([chr(charcode)], negated=True)

    def rule_any(self, params):
        return Any(self.dotall)

    def rule_subpattern(self, params):
        gid, pattern = params
        data = self.recurse(pattern.data)
        if len(data) == 1:
            return data[0]
        else:
            return Sequence(data)

    def rule_branch(self, params):
        gid, exprs = params
        return Alternates(Sequence(self.recurse(x.data)) for x in exprs)

    def rule_in(self, params):
        negated = params[0] == (sre_constants.NEGATE, None)
        if negated:
            params = params[1:]

        params = self.recurse(params)

        # Expand categories
        result = []
        for param in params:
            if isinstance(param, list):
                result.extend(param)
            else:
                result.append(param)

        return Choice(result, negated=negated)

    def rule_min_repeat(self, params):
        raise SyntaxError('Non greedy repetition (*? or +?) is not supported')

    def rule_max_repeat(self, params):
        min, max, data = params
        return Repeat(min, max, Sequence(self.recurse(data)))

    def rule_assert(self, data):
        gid, params = data
        return LookAhead(Sequence(self.recurse(params)))

    def rule_range(self, data):
        return (chr(data[0]), chr(data[1]))

    def rule_category(self, category):
        #XXX word have inconsistencies with unicode, maybe we should error
        if category == sre_constants.CATEGORY_DIGIT:
            return [('0', '9')]
        elif category == sre_constants.CATEGORY_NOT_DIGIT:
            return list({chr(x) for x in range(256)} - {'0123456789'.split()})
        elif category == sre_constants.CATEGORY_WORD:
            return [('0', '9'), ('A', 'Z'), ('a', 'z'), '_']
        elif category == sre_constants.CATEGORY_LINEBREAK:
            return ['\r', '\n']
        elif category == sre_constants.CATEGORY_NOT_LINEBREAK:
            return list({chr(x) for x in range(256)} - {'\r', '\n'})
        elif category == sre_constants.CATEGORY_SPACE:
            return [' ', '\t', '\r', '\n', '\f']
        elif category == sre_constants.CATEGORY_NOT_SPACE:
            return list({chr(x) for x in range(256)} - {' \t\r\n\f'.split()})

        raise SyntaxError('Unsupported category {}'.format(category))
