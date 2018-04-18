from bisect import bisect_left


class LexicalInfo(object):
    __slots__ = ('lines',)

    def __init__(self):
        self.lines = []

    def mark_line(self, pos):
        """ Must be called in order! """
        self.lines.append(pos)

    def lookup(self, pos):
        lines = self.lines
        line = bisect_left(lines, pos)
        if line > 0:
            pos -= lines[line-1] + 1
        return (line, pos)


class Token(object):
    __slots__ = ('name', 'value', 'position', 'lexinfo')

    def __init__(self, name, value=None, position=None, lexinfo=None):
        self.name = name
        self.value = value
        self.position = position
        self.lexinfo = lexinfo

    @property
    def length(self):
        return len(self.value)

    @property
    def span(self):
        return (self.position, self.position + self.length)

    @property
    def line(self):
        return self.linecol[0]

    @property
    def column(self):
        return self.linecol[1]

    @property
    def linecol(self):
        line, column = self.lexinfo.lookup(self.position)
        return (line+1, column+1)

    def __repr__(self):
        return 'Token({})'.format(self.name)




from fsm_lexer import lex


data = open('test.g').read()

lexinfo = LexicalInfo()
tokens = []

for ofs, token, value in lex(data):
    if token in ('NL', 'REGEXP'):
        for i in range(value.count('\n')):
            lexinfo.mark_line(ofs + i)

    tokens.append( Token(token, value, ofs, lexinfo) )


for t in tokens:
    print('{0:02}:{1:02} -- {2} = {3}'.format(
        t.line, t.column, t.name, repr(t.value)))
