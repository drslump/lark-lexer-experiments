""" Allows to assemble a function based on Python opcodes with support for
    labelled jumps.
"""
import sys, dis, struct, types
from functools import partial

from lark.utils import STRING_TYPE


class Opcode(object):
    """ Represents a Python opcode and allows to encode it into bytecode/wordcode.
    """
    __slots__ = ('name', 'arg')

    def __init__(self, name, arg=None):
        self.name = name
        self.arg = arg

    def is_named_jump(self):
        return dis.opmap.get(self.name) in dis.hasjabs and isinstance(self.arg, STRING_TYPE)

    def encode(self):
        if self.name == 'COMPARE_OP':
            arg = dis.cmp_op.index(self.arg)
        elif self.is_named_jump():
            arg = 65535    # force a extended_arg for >3.6
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

    def __repr__(self):
        return 'Opcode({}, {})'.format(repr(self.name), repr(self.arg))


class Opcodes(list):
    """ Holds a list of opcodes allowing to easily append with:

            opcodes << Opcode('NOP')

    """
    def __init__(self, iterable=None):
        if iterable:
            self.extend(iterable)

    def __lshift__(self, other):
        if isinstance(other, (tuple, list)):
            assert all(isinstance(x, Opcode) for x in other)
            self.extend(other)
        elif isinstance(other, Opcode):
            self.append(other)
        else:
            raise TypeError('Unsupported type: ' + type(other))

    def apply(self, fn, span=None):
        if span is None:
            span = fn.func_code.co_argcount

        idx = 0
        while idx <= len(self) - span:
            repl = fn(*self[idx:idx+span])
            if isinstance(repl, Opcode):
                repl = (repl,)

            if repl is None:
                idx += 1
            else:
                del self[idx:idx+span]
                for op in repl[::-1]:
                    self.insert(idx, op)
                idx += len(repl)


class Assembler(object):
    """ Allows to encode a set of opcodes to construct a function
    """
    def __init__(self, opcodes=(), name='noname', docblock=None):
        self.opcodes = Opcodes(opcodes)
        self.name = name
        self.docblock = docblock

    def _index_or(self, values, v):
        try:
            return values.index(v)
        except ValueError:
            values.append(v)
            return len(values) - 1

    map_name = lambda self, v: self._index_or(self._names, v)
    map_const = lambda self, v: self._index_or(self._consts, v)
    map_local = lambda self, v: self._index_or(self._locals, v)

    def _encode(self):
        code = bytearray()
        labels = {}
        jumps = []

        # First encode while keeping a registry of jumps and labels
        for opcode in self.opcodes:
            if opcode.name == '$LABEL':
                assert opcode.arg not in labels
                labels[opcode.arg] = len(code)
                continue

            if opcode.name in ('LOAD_CONST',):
                opcode = Opcode(opcode.name, self.map_const(opcode.arg))
            elif opcode.name in ('LOAD_GLOBAL', 'LOAD_ATTR'):
                opcode = Opcode(opcode.name, self.map_name(opcode.arg))
            elif opcode.name in ('STORE_FAST', 'LOAD_FAST'):
                opcode = Opcode(opcode.name, self.map_local(opcode.arg))

            if opcode.is_named_jump():
                jumps.append((opcode.arg, len(code)))

            code.extend(opcode.encode())

        # Now process the jumps to set the correct offsets
        for label, offset in jumps:
            Opcode.patch_arg(code, offset, labels[label])

        return bytes(code)

    def annotate(self):
        """ Annotate the label opcodes with a constant to see with dis()
        """
        def labels(op):
            if op.name == '$LABEL':
                return (
                    op,
                    Opcode('LOAD_CONST', '$LABEL={}'.format(op.arg)),
                    Opcode('POP_TOP'),
                )

        self.opcodes.apply(labels)

    def optimize(self):
        """ Applies simple optimizations to the opcodes
        """
        def immediate_jumps(op1, op2):
            if op1.name == 'JUMP_ABSOLUTE' and op2.name == '$LABEL' and op1.arg == op2.arg:
                return op2

        def store_load(op1, op2):
            if op1.name == 'STORE_FAST' and op2.name == 'LOAD_FAST' and op1.arg == op2.arg:
                return (
                    Opcode('DUP_TOP'),
                    op1)

        self.opcodes.apply(immediate_jumps)
        self.opcodes.apply(store_load)


    def compile(self, argnames=(), defaults={}, globals={}, stacksize=8):
        """ Encodes the opcodes into bytecode and builds a function type
        """
        assert set(defaults.keys()) <= set(argnames)
        defaults = tuple(defaults[k] for k in argnames if k in defaults)

        self._names = []
        self._consts = [self.docblock]
        self._locals = list(argnames)

        code = self._encode()

        locals = tuple(self._locals)
        consts = tuple(self._consts)
        names = tuple(self._names)

        args = [
            len(argnames),          # co_argcount -> (stream, ofs)
            len(locals),            # co_nlocals
            stacksize,              # co_stacksize -> maximum number of values in the stack
            0,                      # co_flags -> only if *args is used
            code,                   # co_code -> compiled bytecode
            consts,                 # co_consts -> literals in the code (first is docblock)
            names,                  # co_names -> global variables
            locals,                 # co_varnames -> list of local variables
            self.name + '_asm.py',  # co_filename,
            self.name,              # co_name,
            0,                      # co_firstlineno,
            bytes()                 # co_lnotab
        ]

        if sys.version_info >= (3,0,0):
            args.insert(1, 0)       # co_kwonlyargcount

        co = types.CodeType(*args)
        return types.FunctionType(co, globals, self.name, defaults)

    def __repr__(self):
        return u'Assembler(name={0!r}, docblock={1!r}, opcodes=[\n{2}\n])'.format(
            self.name, self.docblock,
            u'  ' + u',\n  '.join(repr(o) for o in self.opcodes))


# Generate helper functions to build Opcodes based on the names provided by Python
for opname in dis.opmap.keys():
    globals()[opname] = partial(Opcode, opname)

# Pseudo opcode for a named jump target
LABEL = lambda x: Opcode('$LABEL', x)
