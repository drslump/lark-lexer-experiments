""" Generic building blocks for constructing a finite state machine
"""

import sys

from lark.utils import STRING_TYPE

from fsm.assembler import *


class Abstract(object):
    def opcodes(self, debug=False):
        raise AssertionError('Not implemented')

    def assemble(self, name='fsm', docblock=None, debug=False, annotate=False):
        """ Prepares an Assembler instance with the opcodes
        """
        opcodes = self.opcodes(debug)
        asm = Assembler(opcodes, name, docblock)

        if annotate:
            asm.annotate()

        if not debug:
            asm.optimize()

        return asm


class State(Abstract):
    """ Holds the set of actions for a label
    """
    __slots__ = ('label', 'actions',)

    def __init__(self, label=None, actions=()):
        self.label = label
        self.actions = list(actions)

    def add(self, *actions):
        self.actions.extend(actions)

    def opcodes(self, debug=False):
        ops = Opcodes()

        if self.label:
            ops << LABEL(self.label)
            if debug:
                ops << Debug('FSM> State: {0}'.format(self.label))

        for action in self.actions:
            ops << action.opcodes(debug)

        return ops

    def __repr__(self):
        actions = [repr(action).replace('\n', '\n  ') for action in self.actions]
        return 'State({0!r}, [\n  {1}\n])'.format(self.label, ',\n  '.join(actions))


class If(Abstract):
    def __init__(self, varname, op, test, true, false=None):
        assert op in ('in', 'not in') or not isinstance(test, STRING_TYPE) or len(test) == 1, \
            'operator {} does not support a string of length {} ({})' \
            .format(op, len(test), test)

        #XXX `in` seems to be faster than `==`
        if op == '==' and isinstance(test, STRING_TYPE):
            op = 'in'

        self.op = op
        self.varname = varname

        if isinstance(test, int):
            test = chr(test)
        self.test = test

        if isinstance(true, Abstract):
            true = [true]
        elif isinstance(true, STRING_TYPE):
            true = [Goto(true)]
        self.true = true

        if isinstance(false, Abstract):
            false = [false]
        elif isinstance(false, STRING_TYPE):
            false = [Goto(false)]
        elif false is None:
            false = []
        self.false = false

    def opcodes(self, debug=False):
        ops = Opcodes()

        else_lbl = 'else_{}'.format(id(self))
        endif_lbl = 'endif_{}'.format(id(self))

        ops << LOAD_FAST(self.varname)
        ops << LOAD_CONST(self.test)
        ops << COMPARE_OP(self.op)

        # Optimize when the condition triggers a jump
        if self.true and isinstance(self.true[0], Goto):
            ops << POP_JUMP_IF_TRUE(self.true[0].label)
        else:
            #XXX check if POP_JUMP_IF_TRUE is faster
            ops << POP_JUMP_IF_FALSE(else_lbl)
            for action in self.true:
                ops << action.opcodes(debug)
            ops << JUMP_ABSOLUTE(endif_lbl)

        ops << LABEL(else_lbl)
        for action in self.false:
            ops << action.opcodes(debug)
        ops << LABEL(endif_lbl)

        return ops

    def __repr__(self):
        true = repr(self.true)
        false = repr(self.false)
        return 'If({0!r}, {1!r}, {2!r}, {3}, {4})'.format(
            self.varname, self.op, self.test, true, false)


class Debug(Abstract):
    """ Prints debug information.
        To dump local variables prefix the arg with '$'.
    """
    def __init__(self, format, *args):
        self.format = format
        self.args = args

    def opcodes(self, debug=False):
        ops = Opcodes()

        ops << LOAD_CONST(self.format + '\n')
        ops << LOAD_ATTR('format')
        for arg in self.args:
            if isinstance(arg, STRING_TYPE) and arg.startswith('$'):
                ops << LOAD_FAST(arg[1:])
            else:
                ops << LOAD_CONST(arg)

        ops << CALL_FUNCTION(len(self.args))
        ops << Opcode('PRINT_ITEM')

        return ops

    def __repr__(self):
        return 'Debug({0!r}, *{1!r})'.format(self.format, self.args)


class Goto(Abstract):
    """ Jumps to a specific label
    """
    __slots__ = ('label',)

    def __init__(self, label):
        self.label = str(label)

    def opcodes(self, debug=False):
        ops = Opcodes()
        if debug:
            ops << Debug('FSM> Goto: {}', self.label).opcodes()

        ops << JUMP_ABSOLUTE(self.label)
        return ops

    def __repr__(self):
        return 'Goto({0!r})'.format(self.label)
