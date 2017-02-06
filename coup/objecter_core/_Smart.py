# coding: utf-8
r"""Smart translate core (1)

Using ***_smart*** you can make your translate model very simple. See this example:

    ```
    ForIn = _smart(
        IN_FORMAT='for <EXP:NAME> in <EXP>:',
        OUT_FORMAT='for <EXP:NAME> in <EXP>'
    )
    ```

All ***\<EXP\>*** are pathes to parse child expressions.

Result is an class based on ***_Base***.

"""

_DOC_ADD = ['We have this smart translates now:\n']
#_DOC_SMARTERS = []

try:
    # Python 3
    from itertools import zip_longest as izip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest

from ._Base import _Base, _Line, _GoodLine
from ._smart_parsers import _ExpParser


def _smart(IN_FORMAT = None, OUT_FORMAT = None, INDEX = None,
           tst=False, locals=None, init_locals=None, TYPE_OUT=None,
           on_init=lambda self:None,
           on_try_instruction=lambda self, i, line: None,
           on_instruction=lambda self,i,ins:ins,
           on_block_start=lambda self, block:None,
           on_get_tree=lambda self,text:text,
           BLOCK_START='{', BLOCK_END='}'):

    _INDEX = INDEX
    _TYPE_OUT = TYPE_OUT
    _on_block_start = on_block_start
    _on_init = on_init

    def make_smart(IN_FORMAT):

        _DOC_ADD.append(
'''  {:>3}. {}
       {}
'''.format(len(_DOC_ADD), IN_FORMAT, OUT_FORMAT))

        start_name = IN_FORMAT.split('<')[0].strip()

        class _Exper:

            deleters_in = _ExpParser(IN_FORMAT)
            deleters_out = _ExpParser(OUT_FORMAT)

            if _INDEX == None:
                INDEX = -sum([len(d) for d in deleters_in]) + len(deleters_in.exps)
            else:
                INDEX = _INDEX

            _starts_with_deleter = len(deleters_in) > 0 and len(deleters_in[0]) > 0 and IN_FORMAT.startswith(deleters_in[0])

            init_locals = None

            def init_exps(self, line, on_instruction):
                #print('deleters_in:', self.deleters_in, line)
                #print('deleters_in.exps:', self.deleters_in.exps)
                line = line.strip()
                # for l in self.deleters_in:
                #     if len(l) == 0:
                #         continue
                #     line = line.replace(l, '|')
                # if line.startswith('|'):
                #     line = line[1:]
                # if line.endswith('|'):
                #     line = line[:-1]

                line = _line_to_slashs(line, self.deleters_in) #, IN_FORMAT)

                lst = line.split('|')
                #print('line:', line)

                def pr(ei, e, i):
                    #print('...', ei, e, self)
                    ins = on_try_instruction(self, i, e)
                    if ins:
                        return ins
                    return ei.try_instruction(e, line_number=self.line_number, parent=self)

                self.instructions = [ on_instruction(i, pr(ei, e, i)) for i, (e, ei) in enumerate(zip(lst, self.deleters_in.exps)) ]

            @classmethod
            def is_instruction(cls, line):
                line = line.strip()
                for i, part in enumerate(cls.deleters_in):
                    if part not in line:
                        return False
                    if i == 0 and cls._starts_with_deleter:
                        if line.find(part) != 0:
                            return False
                return True

            def get_tree_main(self):
                trees = [ ins.get_tree() for ins in self.instructions ] #line = '|'.join()
                #print( trees, self.deleters_out )
                #print(len(self.deleters_in), len(self.instructions), self.deleters_in[0], self.instructions[0])

                if len(trees) < len(self.deleters_out):
                    plus = lambda tree, d : d + tree
                else:
                    plus = lambda tree, d: tree + d

                #print( self.line, len(trees), len(self.deleters_out) )

                line = ''.join( plus(tree, d) for tree, d in izip_longest(trees, self.deleters_out, fillvalue='') )
                #print('new line:', line)

                # if tst:
                #     raise Exception('!!!')
                if self.init_locals:
                    i = 0
                    for name, tip in self.init_locals.items():
                        #print(self.in_block, name)
                        self.in_block.blocks.insert(i, _GoodLine(self.otstup_string(4)+'var {}:{}? = nil'.format(name, tip)))
                        i += 1
                    if i > 0:
                        self.in_block.blocks.insert(i, _GoodLine(''))

                    #line = '\n'.join([ 'var {}:{}?'.format(name, tip)
                    #                   for name, tip in self.init_locals.items() ]) + line

                return on_get_tree(self, line)

        class Smart(_Exper, _Base):

            #INDEX = _INDEX
            START_NAME = start_name
            locals = None
            TYPE_OUT = _TYPE_OUT

            on_block_start = _on_block_start
            _BLOCK_START = BLOCK_START
            _BLOCK_END = BLOCK_END

            def __init__(self, line, parent=None, line_number=0):
                self.locals = locals
                self.init_locals = init_locals

                super(Smart, self).__init__(line, parent, line_number)

                _on_init(self)

                def on_my_instruction(i, ins):
                    return on_instruction(self, i, ins)

                self.init_exps(line, on_my_instruction)

            def __eq__(self, other):
                if hasattr(other, 'instructions'):
                    return self.instructions == other.instructions
                return False

            def __str__(self):
                return self.make_my_str()

            @classmethod
            def make_my_str(cls):
                return cls.__name__ + '(' + start_name + ': ' + IN_FORMAT + ')'

            @classmethod
            def test_string(cls, line):
                print('{}: {} --> {}'.format(cls.make_my_str(), line, cls.is_instruction(line)))

        #print(IN_FORMAT, Smart.INDEX)

        return Smart

    if type(IN_FORMAT) not in (list, tuple):
        return make_smart(IN_FORMAT)

    ins_list = [make_smart(a) for a in IN_FORMAT]
    current = [ ins_list[0] ]

    def _install_current(cur):
        print('[ _install_current ] {}'.format(cur))
        current[ 0 ] = cur

    class FooType(type):

        def __getattr__(cls, key):
            print('[ get Foo attr ] {}'.format(key))
            val = getattr(current[ 0 ], key)
            return val

    import sys as _sys

    if _sys.version_info.major >= 3:
        _SmartListBase = FooType(str('_SmartListBase'), (), {})
    else:
        class _SmartListBase:
            __metaclass__ = FooType

    class SmartList(_SmartListBase):

        def __init__(self, *args, **kwargs):
            self._cur = current[ 0 ]( *args, **kwargs )

        def __getattr__(self, item):
            return getattr(self._cur, item)

        @classmethod
        def is_instruction(cls, line):
            print('[ is_instruction ] {}'.format(ins_list))
            for ins in ins_list:
                if ins.is_instruction(line):
                    _install_current( ins )
                    return True

    print('!!!', ins_list)

    return SmartList

def _line_to_slashs(line, deleters_in):
    line = line.strip()
    start_line = line

    #IN_FORMAT = IN_FORMAT.replace('<EXP', '<EEEEEEEE')

    #IN_FORMAT = '<EXP>'.join( [ a.split('>')[-1] for a in IN_FORMAT.split('<EXP') ] )
    #IN_FORMAT_LEFT = IN_FORMAT[:len(IN_FORMAT)/2]
    #IN_FORMAT_RIGHT = IN_FORMAT[len(IN_FORMAT) / 2:]

    #print('^^^ {} / {}'.format(IN_FORMAT_LEFT, IN_FORMAT_RIGHT))

    #left = [a for a in deleters_in if a in IN_FORMAT_LEFT] #[:len(deleters_in)/2+1]
    #right = [a for a in deleters_in[::-1] if a in IN_FORMAT_RIGHT] #deleters_in[-1:-len(deleters_in) / 2:-1]

    left = deleters_in[:len(deleters_in)/2+1]
    right = deleters_in[-1:-len(deleters_in) / 2:-1]

    if len(right) > len(left):
        left, right = left + right[-1:], right[:-1]
    elif len(left) + 1 > len(right):
        left, right = left[:-1], right + left[-1:]

    #print('::: {} / {}'.format(left, right))

    for l in left:
        if len(l) == 0:
            continue
        i = line.find(l)
        #print('\t{} [{}]: {}'.format(i, l, line))
        line = line[:i] + '|' + line[i+len(l):]

    for l in right:
        if len(l) == 0:
            continue
        i = line.rfind(l)
        #print('\t{} [{}]: {} R'.format(i, l, line))
        line = line[:i] + '|' + line[i + len(l):]


    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]

    #print('... {} --> {} --> {}'.format(start_line, deleters_in, line) )

    return line
