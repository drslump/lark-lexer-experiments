""" Finite State machine builder for re2c lexers
"""
from __future__ import absolute_import

from lark.utils import STRING_TYPE
from lark.lexer import LexError

from fsm import State as FsmState, Abstract, Debug, Goto, If
from fsm.assembler import *


def build(asm, char_type=bytes):
    """ Builds a lexer function for the given assembler
        char_type: use `bytes` if you prefer to match ascii, utf-8 or binary
    """
    const_fn = asm.map_const
    try:
        # Cast strings to the desired type for a speed boost
        asm.map_const = lambda v: const_fn(char_type(v) if isinstance(v, STRING_TYPE) else v)

        return asm.compile(['stream', 'ofs'], {'ofs': 0})
    finally:
        asm.map_const = const_fn


def wrapper(lexfn, stream, ofs=0, sentinel='\0'):
    """ Wrapper for generated lexers
    """
    try:
        while True:
            ofs, end, token = lexfn(stream, ofs)
            if token is None:
                raise LexError('Unexpected input "{}" at position {}'.format(stream[ofs], ofs))

            assert end > ofs, 'lexer neither advance nor fail'

            yield ofs, token, stream[ofs:end]
            ofs = end
    except IndexError:
        # Retry with a sentinel to try to extract a last token
        try:
            ofs_tail, end, token = lexfn(stream[ofs:] + sentinel, 0)

            if token is None:
                ofs += ofs_tail
                raise LexError('Unexpected input "{}" at position {}'.format(stream[ofs], ofs))

            yield ofs+ofs_tail, token, stream[ofs+ofs_tail:ofs+end]
        except IndexError:
            raise LexError('Unexpected input "{}" at position {}'.format(stream[ofs], ofs))


class State(FsmState):
    def opcodes(self, debug=False):
        ops = Opcodes()

        # Initialize cursor on the root state
        if self.label is None:
            ops << LOAD_FAST('ofs')
            ops << STORE_FAST('YYCURSOR')

        ops << super(State, self).opcodes(debug)

        return ops


class Consume(Abstract):
    """ Consumes the next character from the stream
    """
    __slots__ = ()

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_FAST('stream')
        ops << LOAD_FAST('YYCURSOR')
        ops << BINARY_SUBSCR()       # > stream[ofs]
        ops << STORE_FAST('yych')    # > yych = stream[ofs]

        if debug:
            ops << Debug('FSM> Consume: {} (cursor: {})', '$yych', '$YYCURSOR').opcodes()

        return ops

    def __repr__(self):
        return 'Consume()'


class Advance(Abstract):
    """ Advances to the next character in the stream
    """
    __slots__ = ()

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_FAST('YYCURSOR')
        ops << LOAD_CONST(1)
        ops << INPLACE_ADD()        # > ofs + 1
        ops << STORE_FAST('YYCURSOR')    # > ofs = ofs + 1

        if debug:
            ops << Debug('FSM> Advance (cursor: {})', '$YYCURSOR').opcodes()

        return ops

    def __repr__(self):
        return 'Advance()'


class Retract(Abstract):
    """ Retracts to the next character in the stream
    """
    __slots__ = ()

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_FAST('YYCURSOR')
        ops << LOAD_CONST(1)
        ops << INPLACE_SUBTRACT()
        ops << STORE_FAST('YYCURSOR')

        if debug:
            ops << Debug('FSM> Retract (cursor: {})', '$YYCURSOR').opcodes()

        return ops

    def __repr__(self):
        return 'Retract()'


class Mark(Abstract):
    """ Marks a branch for a look ahead
    """
    __slots__ = ('mark',)

    def __init__(self, mark):
        self.mark = mark

    def opcodes(self, debug=False):
        ops = Opcodes()

        ops << LOAD_CONST(self.mark)
        ops << STORE_FAST('yyaccept')

        if debug:
            ops << Debug('FSM> Mark: {} (cursor: {})', '$yyaccept', '$YYCURSOR').opcodes()

        return ops

    def __repr__(self):
        return 'Mark({0!r})'.format(self.mark)


class Save(Abstract):
    """ Saves the current offset
    """
    __slots__ = ('var',)

    def __init__(self, var):
        self.var = var

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_FAST('YYCURSOR')
        ops << STORE_FAST(self.var)

        if debug:
            ops << Debug('FSM> Save (cursor: {})', '$YYCURSOR').opcodes()

        return ops

    def __repr__(self):
        return 'Save({0!r})'.format(self.var)


class Restore(Abstract):
    """ Restores the offset from a previous save
    """
    __slots__ = ('var',)

    def __init__(self, var):
        self.var = var

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_FAST(self.var)
        ops << STORE_FAST('YYCURSOR')

        if debug:
            ops << Debug('FSM> Restore (cursor: {})', '$YYCURSOR').opcodes()

        return ops

    def __repr__(self):
        return 'Restore({0!r})'.format(self.var)


class Produce(Abstract):
    """ Returns the current offset with an optional token

    """
    __slots__ = ('token',)

    def __init__(self, token=None):
        self.token = token

    def opcodes(self, debug=False):
        ops = Opcodes()

        #XXX if token is ignored (and no callbacks) jump to start
        # if self.token in ('WS','WS_INLINE','NEWLINE','CR','LF'):
        #     # print('WS HACK! -- REMOVE ME!')
        #     if debug:
        #         ops << Debug('FSM> Ignoring: <{}> (ofs: {}, cursor: {})', self.token, '$ofs', '$YYCURSOR').opcodes()

        #     ops << LOAD_FAST('YYCURSOR')
        #     ops << STORE_FAST('ofs')
        #     ops << Goto('$START').opcodes(debug)
        #     return ops

        if debug:
            ops << Debug('FSM> Produce: <{}> (ofs: {}, cursor: {})', self.token, '$ofs', '$YYCURSOR').opcodes()

        # > return (ofs, YYCURSOR, self.token)
        ops << LOAD_FAST('ofs')
        ops << LOAD_FAST('YYCURSOR')
        ops << LOAD_CONST(self.token)
        ops << BUILD_TUPLE(3)
        ops << RETURN_VALUE()
        return ops

    def __repr__(self):
        return 'Produce({0!r})'.format(self.token)
