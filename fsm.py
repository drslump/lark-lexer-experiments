"""
 - Use `re2c -D` to get dot output with the states easy to parse
    - Find the node(s?) with yyaccept transitions
    - Find the lowest common ancestors between this node and the end transitions
    - Mark the ancestors according to the transition with the end node they share
 - Bitmaps are slower: Check if it's worth it to support generated bitmaps
"""
import sys, dis, struct, types

# Opcode helpers to make the code more readable
BINARY_SUBSCR = lambda: Opcode('BINARY_SUBSCR')
BUILD_TUPLE = lambda x: Opcode('BUILD_TUPLE', x)
COMPARE_OP = lambda x: Opcode('COMPARE_OP', x)
INPLACE_ADD = lambda: Opcode('INPLACE_ADD')
INPLACE_SUBTRACT = lambda: Opcode('INPLACE_SUBTRACT')
JUMP_ABSOLUTE = lambda x: Opcode('JUMP_ABSOLUTE', x)
LOAD_CONST = lambda x: Opcode('LOAD_CONST', x)
LOAD_FAST = lambda x: Opcode('LOAD_FAST', x)
POP_JUMP_IF_FALSE = lambda x: Opcode('POP_JUMP_IF_FALSE', x)
POP_JUMP_IF_TRUE = lambda x: Opcode('POP_JUMP_IF_TRUE', x)
STORE_FAST = lambda x: Opcode('STORE_FAST', x)
RETURN_VALUE = lambda: Opcode('RETURN_VALUE')
# Pseudo opcode to group opcodes belonging to a state
STATE = lambda x: Opcode('$STATE', x)

if sys.version_info < (3,0,0):
    STR_TYPES = (basestring,)
else:
    STR_TYPES = (str,)


class Opcode(object):
    __slots__ = ('name', 'arg')

    def __init__(self, name, arg=None):
        self.name = name
        self.arg = arg

    def is_labelled_jump(self):
        return dis.opmap[self.name] in dis.hasjabs \
            and not isinstance(self.arg, int)

    def encode(self):
        if self.name == 'COMPARE_OP':
            arg = dis.cmp_op.index(self.arg)
        elif self.is_labelled_jump():
            arg = 65535     # force a extended_arg in >3.6
        else:
            arg = self.arg or 0

        opcode = dis.opmap[self.name]
        if opcode >= dis.HAVE_ARGUMENT:
            assert arg <= 0xFFFF, 'unsupported opcode arg over 16bits'

        return self._encode(opcode, arg)

    if sys.version_info < (3,6):
        def _encode(self, opcode, arg):
            if opcode >= dis.HAVE_ARGUMENT:
                return struct.pack('<BH', opcode, arg)
            else:
                return struct.pack('B', opcode)

        @classmethod
        def patch_arg(cls, buffer, offset, arg):
            packed = struct.pack('<H', arg)
            buffer[offset + 1] = packed[0]
            buffer[offset + 2] = packed[1]

    else:
        def _encode(self, opcode, arg):
            if opcode >= dis.HAVE_ARGUMENT and arg > 0xFF:
                return struct.pack('BBBB', dis.EXTENDED_ARG, arg>>8, opcode, arg&0xFF)
            else:
                return struct.pack('BB', opcode, arg)

        @classmethod
        def patch_arg(cls, buffer, offset, arg):
            # TODO: Parse opcode and adapt extended arg if needed
            if False and arg <= 0xFF:
                buffer[offset+1] = arg
            else:
                buffer[offset+1] = arg >> 8
                buffer[offset+3] = arg & 0xFF


class Opcodes(list):
    def __init__(self, iterable=None):
        if iterable:
            self.extend(iterable)

    def __lshift__(self, other):
        if isinstance(other, (tuple, list)):
            self.extend(other)
        elif isinstance(other, Opcode):
            self.append(other)
        else:
            raise TypeError('Unsupported type: ' + type(other))

    def encode(self, mut_names, mut_consts, mut_varnames, annotate=False):
        """
        Note that consts and varnames will be mutated!
        """
        def index_or(values, v, extra={}):
            try:
                return values.index(v)
            except ValueError:
                values.append(v)
                return len(values) - 1

        code = bytearray()
        states = {}
        jumps = []

        # First encode while keeping a registry of jumps and labels
        for opcode in self:
            if opcode.name == '$STATE':
                states[opcode.arg] = len(code)
                continue

            if opcode.name in ('LOAD_CONST',):
                arg = index_or(mut_consts, opcode.arg)
                opcode = Opcode(opcode.name, arg)

            if opcode.name in ('LOAD_GLOBAL', 'LOAD_ATTR'):
                arg = index_or(mut_names, opcode.arg)
                opcode = Opcode(opcode.name, arg)

            if opcode.name in ('STORE_FAST', 'LOAD_FAST'):
                arg = index_or(mut_varnames, opcode.arg)
                opcode = Opcode(opcode.name, arg)

            if opcode.is_labelled_jump():
                jumps.append((opcode.arg, len(code)))

            code.extend(opcode.encode())

        # Now process the jumps to set the correct offsets
        for state, offset in jumps:
            Opcode.patch_arg(code, offset, states[state])

        return bytes(code)


class Abstract(object):

    def opcodes(self, debug=False):
        raise AssertionError('Not implemented')

    def optimize(self):
        pass

    def compile(self, name='fsmlex', docblock=None, str_type=str, debug=False, annotate=False):
        """ Builds a function with the currently configured opcodes

            Python 2.7: use str_type=unicode if you're scanning an unicode
            document.
        """
        def fix_string(const):
            if isinstance(const, STR_TYPES):
                if type(const) != str_type:
                    return str_type(const)
            return const

        varglobals = {}
        names = list(varglobals.keys())
        argnames = ('stream', 'ofs')
        varnames = list(argnames)
        constnames = [docblock]

        opcodes = self.opcodes(debug)

        ## optimizations
        idx = 0
        while idx < len(opcodes):
            op = opcodes[idx]

            # Jumps to next opcode -> noop
            if op.name == 'JUMP_ABSOLUTE':
                op2 = opcodes[idx+1]
                if op2.name == '$STATE' and op.arg == op2.arg:
                    del opcodes[idx]
                    continue

            if annotate:
                if op.name == '$STATE':
                    ops = (
                        Opcode('LOAD_CONST', '$STATE={}'.format(op.arg)),
                        Opcode('POP_TOP'),
                    )

                    for x in ops[::-1]:
                        opcodes.insert(idx + 1, x)

                    idx += len(ops)
                    continue

            idx += 1


        code = opcodes.encode(names, constnames, varnames)

        constnames = [fix_string(c) for c in constnames]

        args = [
            len(argnames),          # co_argcount -> (stream, ofs)
            len(varnames),          # co_nlocals
            3,                      # co_stacksize -> maximum number of values in the stack
            0,                      # co_flags -> only if *args is used
            code,                   # co_code -> compiled bytecode
            tuple(constnames),      # co_consts -> literals in the code (first is docblock)
            tuple(names),           # co_names -> global variables
            tuple(varnames),        # co_varnames -> list of local variables (starting with args)
            name + '.py',           # co_filename,
            name,                   # co_name,
            0,                      # co_firstlineno,
            bytes()                 # co_lnotab
        ]

        if sys.version_info >= (3,0,0):
            args.insert(1, 0)       # co_kwonlyargcount

        co = types.CodeType(*args)

        return types.FunctionType(co, varglobals, name, (0,))

class BitMap(Abstract):
    """ Slower than the state jumps! """
    __slots__ = ('label', 'ofs', 'mask')
    def __init__(self, label, ofs=0, mask=0xFF):
        self.label = label
        self.ofs = ofs
        self.mask = mask

    def opcodes(self, debug=False):
        # if (yybm[256+ch] & 128) {
        #     goto yy4;
        # }
        ops = Opcodes()

        ops << LOAD_FAST('yybm')

        ops << Opcode('LOAD_FAST', 'ord')
        ops << LOAD_FAST('yych')
        ops << Opcode('CALL_FUNCTION', 1)

        if self.ofs:
            ops << LOAD_CONST(self.ofs)
            ops << INPLACE_ADD()

        ops << BINARY_SUBSCR()  # yybm[self.ofs + ord(ch)]

        ops << LOAD_CONST(self.mask)
        ops << Opcode('BINARY_AND')
        ops << POP_JUMP_IF_TRUE(self.label)

        return ops

    def __repr__(self):
        return 'BitMap({}, {}, {})'.format(repr(self.label), repr(self.ofs), repr(self.mask))


class State(Abstract):
    """ Holds the set of actions for a label
    """
    __slots__ = ('label', 'actions')

    def __init__(self, label=None, actions=None):
        self.label = str(label) if label is not None else None
        self.actions = list(actions) if actions else []

    def add(self, *actions):
        self.actions.extend(actions)

    def optimize(self):
        # TODO: Collapse Matches with same target

        for action in self.actions:
            action.optimize()

    def opcodes(self, debug=False):
        ops = Opcodes()

        if self.label:
            ops << STATE(self.label)

            if debug and len(self.actions):
                # Allows to track states when disassembling
                ops << LOAD_CONST('State: {}'.format(self.label))
                ops << Opcode('POP_TOP')

                ops << Debug('FSM> State: {} (ofs: {}, ch: {})', self.label, '$ofs', '$ch').opcodes(debug)

        for action in self.actions:
            ops << action.opcodes(debug)

        return ops

    def __repr__(self):
        indent = lambda x: '\n  '.join(x.split('\n'))
        actions = ['  ' + indent(repr(action)) for action in self.actions]
        return 'State({}, [\n{}\n])'.format(repr(self.label), ',\n'.join(actions))


class If(Abstract):
    EQL = staticmethod(lambda *a, **k: If('==', *a, **k))
    NEQ = staticmethod(lambda *a, **k: If('!=', *a, **k))
    LTE = staticmethod(lambda *a, **k: If('<=', *a, **k))
    GTE = staticmethod(lambda *a, **k: If('>=', *a, **k))
    IN  = staticmethod(lambda *a, **k: If('in', *a, **k))

    def __init__(self, op, test, true, false=None, varname='yych'):
        assert op == 'in' or not isinstance(test, STR_TYPES) or len(test) == 1, \
            'operator {} does not support a string of length {} ({})' \
            .format(op, len(test), test)

        #XXX `in` seems to be faster than `==`
        if op == '==' and isinstance(test, STR_TYPES):
            op = 'in'

        self.op = op
        self.varname = varname

        if isinstance(test, int):
            test = chr(test)
        self.test = test

        if isinstance(true, Abstract):
            true = [true]
        elif isinstance(true, str):
            true = [Goto(true)]
        self.true = true

        if isinstance(false, Abstract):
            false = [false]
        elif isinstance(false, str):
            false = [Goto(false)]
        elif false is None:
            false = []
        self.false = false

    def opcodes(self, debug=False):
        ops = Opcodes()

        false_lbl = 'false_if{}'.format(id(self))

        ops << LOAD_FAST(self.varname)
        ops << LOAD_CONST(self.test)
        ops << COMPARE_OP(self.op)

        # Optimize when the condition triggers a jump
        if self.true and isinstance(self.true[0], Goto):
            ops << POP_JUMP_IF_TRUE(self.true[0].label)
        else:
            ops << POP_JUMP_IF_FALSE(false_lbl)
            for action in self.true:
                ops << action.opcodes(debug)

        ops << State(false_lbl, self.false).opcodes(debug)

        return ops

    def __repr__(self):
        true = repr(self.true)
        false = repr(self.false)
        return 'If({}, {}, {}, {}, varname={})'.format(
            repr(self.op), repr(self.test), true, false, repr(self.varname))


class Debug(Abstract):
    """ Prints debug information
    """
    def __init__(self, format, *args):
        self.format = format
        self.args = args

    def opcodes(self, debug=False):
        ops = Opcodes()

        if debug:
            ops << LOAD_CONST(self.format + '\n')
            ops << Opcode('LOAD_ATTR', 'format')
            for arg in self.args:
                if isinstance(arg, STR_TYPES) and arg.startswith('$'):
                    ops << LOAD_FAST(arg[1:])
                    ops << Opcode('LOAD_ATTR', '__repr__')
                    ops << Opcode('CALL_FUNCTION', 0)
                else:
                    ops << LOAD_CONST(arg)

            ops << Opcode('CALL_FUNCTION', len(self.args))
            ops << Opcode('PRINT_ITEM')

        return ops

    def __repr__(self):
        return 'Debug({}, *{})'.format(
            repr(self.format), repr(self.args))


class Goto(Abstract):
    """ Jumps to a specific label
    """
    __slots__ = ('label',)

    def __init__(self, label):
        self.label = str(label)

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << JUMP_ABSOLUTE(self.label)
        return ops

    def __repr__(self):
        return 'Goto({})'.format(repr(self.label))


class Consume(Abstract):
    """ Consumes the next character from the stream
    """
    __slots__ = ('advance',)

    def __init__(self, advance=True):
        self.advance = advance

    def opcodes(self, debug=False):
        ops = Opcodes()

        if self.advance:
            ops << Advance().opcodes(debug)

        ops << LOAD_FAST('stream')
        ops << LOAD_FAST('ofs')
        ops << BINARY_SUBSCR()       # > stream[ofs]
        ops << STORE_FAST('yych')    # > yych = stream[ofs]

        ops << Debug('FSM> Consume: {} (ofs: {})', '$ch', '$ofs').opcodes(debug)

        return ops

    def __repr__(self):
        return 'Consume(advance={})'.format(repr(self.advance))


class Advance(Abstract):
    """ Advances to the next character in the stream
    """
    __slots__ = ()

    def opcodes(self, debug=False):
        ops = Opcodes()

        ops << LOAD_FAST('ofs')
        ops << LOAD_CONST(1)
        ops << INPLACE_ADD()        # > ofs + 1
        ops << STORE_FAST('ofs')    # > ofs = ofs + 1

        ops << Debug('FSM> Advance (ofs: {})', '$ofs').opcodes(debug)

        return ops

    def __repr__(self):
        return 'Advance()'


class Retract(Abstract):
    """ Retracts to the next character in the stream
    """
    __slots__ = ()

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_FAST('ofs')
        ops << LOAD_CONST(1)
        ops << INPLACE_SUBTRACT()   # > ofs - 1
        ops << STORE_FAST('ofs')    # > ofs = ofs - 1

        ops << Debug('FSM> Retract (ofs: {})', '$ofs').opcodes(debug)

        return ops

    def __repr__(self):
        return 'Retract()'


class Mark(Abstract):
    """ Marks the current offset for a look ahead
    """
    __slots__ = ('mark',)

    def __init__(self, mark):
        self.mark = mark

    def opcodes(self, debug=False):
        ops = Opcodes()
        ops << LOAD_CONST(self.mark)
        ops << STORE_FAST('yyaccept')   # > yyaccept = self.mark
        ops << LOAD_FAST('ofs')
        ops << STORE_FAST('YYMARKER')   # > YYMARKER = ofs

        ops << Debug('FSM> Mark: {} (ofs: {})', '$yyaccept', '$ofs').opcodes(debug)

        return ops

    def __repr__(self):
        return 'Mark({})'.format(repr(self.mark))


class Backtrack(Abstract):
    """ Backtracks a look ahead
    """
    __slots__ = ('gotos',)

    def __init__(self, gotos={}):
        self.gotos = gotos

    def opcodes(self, debug=False):
        ops = Opcodes()

        ops << Debug('FSM> Backtrack: {} (ofs: {}, marker: {}, ch: {})', '$yyaccept', '$ofs', '$YYMARKER', '$yych').opcodes(debug)

        # > ofs = marker
        ops << LOAD_FAST('YYMARKER')
        ops << STORE_FAST('ofs')

        if self.gotos:
            # Sort the marks from low to high, the highest acts as default route
            markers = sorted(self.gotos.keys())
            for mark in markers[:-1]:
                ops << If.EQL(mark, self.gotos[mark], varname='yyaccept').opcodes(debug)

            ops << Goto(self.gotos[markers[-1]]).opcodes(debug)

        return ops

    def __repr__(self):
        return 'Backtrack({})'.format(repr(self.gotos))


class Produce(Abstract):
    """ Returns the current offset with an optional token
    """
    __slots__ = ('token',)

    def __init__(self, token=None):
        self.token = token

    def opcodes(self, debug=False):
        ops = Opcodes()

        ops << Debug('FSM> Produce: <{}> (ofs: {})', self.token, '$ofs').opcodes(debug)

        # > return (ofs, self.token)
        ops << LOAD_FAST('ofs')
        ops << LOAD_CONST(self.token)
        ops << BUILD_TUPLE(2)
        ops << RETURN_VALUE()
        return ops

    def __repr__(self):
        return 'Produce({})'.format(repr(self.token))
