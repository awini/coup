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
           on_init_end=lambda self:None,
           on_try_instruction=lambda self, i, line: None,
           on_instruction=lambda self,i,ins:ins,
           on_block_start=lambda self, block:None,
           on_block_before_start=lambda self, block:None,
           on_get_tree=lambda self,text:text,
           BLOCK_START='{', BLOCK_END='}',
           full_line=False, IN=None, OUT=None):

    if IN != None:
        IN_FORMAT = IN
    if OUT != None:
        OUT_FORMAT = OUT

    _INDEX = INDEX
    _TYPE_OUT = TYPE_OUT
    _on_block_start = on_block_start
    _on_block_before_start = on_block_before_start
    _on_init = on_init
    _on_init_end = on_init_end

    def make_smart(IN_FORMAT):

        _DOC_ADD.append(
'''  {:>3}. {}
       {}
'''.format(len(_DOC_ADD), IN_FORMAT, OUT_FORMAT))

        start_name = IN_FORMAT.split('<')[0].strip()

        class _Exper:

            deleters_in = _ExpParser(IN_FORMAT)

            if _INDEX == None:
                INDEX = (-sum([len(d) for d in deleters_in])*20 + len(deleters_in.exps)) + (
                    -1000 if full_line else 0)
            else:
                INDEX = _INDEX

            _starts_with_deleter = len(deleters_in) > 0 and len(deleters_in[0]) > 0 and IN_FORMAT.startswith(deleters_in[0])

            init_locals = None

            def init_exps(self, line, on_instruction):
                need_debug = False #'readonly' in line #self.deleters_in.line == 'self.<EXP:TEXT>.<EXP:TEXT>'

                self.deleters_out = _ExpParser(OUT_FORMAT(self)) if callable(OUT_FORMAT) else _ExpParser(OUT_FORMAT)

                if need_debug: #and OUT_FORMAT == '':
                    print('--------')
                    print('deleters_in:', self.deleters_in, line)
                    print('deleters_in.exps:', self.deleters_in.exps)
                    print('deleters_out:', self.deleters_out, line)
                    print('deleters_out.exps:', self.deleters_out.exps)

                line = line.strip()

                new_line = _line_to_slashs(line, self.deleters_in, need_debug=need_debug)
                if new_line == None:
                    raise Exception('cant be {}: {}'.format(self, line))
                line = new_line

                lst = line.split('|')
                if need_debug:
                    print('line:', line)

                _tmp_line = self.line

                def pr(ei, e, i):
                    if need_debug:
                        print('...', ei, e, self)
                    ins = on_try_instruction(self, i, e)

                    if i > len(self.deleters_out.exps)-1:
                        return _Line('')

                    if type(ins) == str:
                        e = ins
                    elif ins:
                        return ins
                    return ei.try_instruction(e, line_number=self.line_number, parent=self)

                self.instructions = [ on_instruction(i, pr(ei, e, i)) for i, (e, ei) in enumerate(zip(lst, self.deleters_in.exps)) ]

                if need_debug:
                    print('>>>>>>', self.instructions)

                self.line = _tmp_line

            @classmethod
            def is_instruction(cls, line):
                if OUT_FORMAT == NotImplemented:
                    return False

                line = line.strip()
                need_debug = False #'self.ttt' == line and 'self.' in cls.deleters_in
                pos = -1
                i = -1

                not_empty_deleters = len([d for d in cls.deleters_in if len(d.strip()) > 0 ])

                for i, part in enumerate(cls.deleters_in):
                    pos = line.find(part, pos+1)
                    if need_debug:
                        print('>>>>>', line, '>>', cls.deleters_in, '>>', part, ':', pos)
                    # if pos <= _last_pos:
                    #     return False
                    if pos < 0:#part not in line:
                        if need_debug:
                            print('\tFALSE')
                        return False
                    if i == 0 and cls._starts_with_deleter:
                        if pos != 0:
                            if need_debug:
                                print('\tFALSE')
                            return False
                    pos += len(part) #len(part)-1

                pos -= len(part)
                    #_last_pos = pos + len(part)-1
                if need_debug or i < len(cls.deleters_in.exps) and i < not_empty_deleters:
                    if line[pos:] == cls.deleters_in[-1]:
                        return True
                    print('>>>> {} = {}'.format(part, line[pos:]))
                    print('\tOK', i, '/', len(cls.deleters_in.exps), not_empty_deleters, '=', line, IN_FORMAT)
                    print('\t', pos, len(line), '=', line[pos:], '!=', cls.deleters_in[-1], cls.deleters_in)
                    return False
                return True

            def get_tree_main(self):
                #print('::: {} --> {} : {}'.format(self.line, self, self.instructions))
                trees = [ ins.get_tree() for ins in self.instructions ] #line = '|'.join()
                #print( trees, self.deleters_out )
                #print(len(self.deleters_in), len(self.instructions), self.deleters_in[0], self.instructions[0])

                if len(trees) < len(self.deleters_out):
                    plus = lambda tree, d : d + tree
                else:
                    plus = lambda tree, d: tree + d

                cor = lambda ex, p: ex.funcer(p) if hasattr(ex, 'funcer') else p

                #print( self.line, len(trees), len(self.deleters_out) )

                line = ''.join( cor(ex, plus(tree, d)) for tree, d, ex in izip_longest(trees, self.deleters_out, self.deleters_out.exps, fillvalue='') )
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
            on_block_before_start = _on_block_before_start
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

                _on_init_end(self)

            @classmethod
            def to_str(cls):
                return '{}: {}'.format(cls.__name__, IN_FORMAT)

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
        #print('[ _install_current ] {}'.format(cur))
        current[ 0 ] = cur

    class FooType(type):

        def __getattr__(cls, key):
            #print('[ get Foo attr ] {}'.format(key))
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

        def __str__(self):
            return 'SmartList({})'.format(self._cur)

        def __repr__(self):
            return self.__str__()

        @classmethod
        def is_instruction(cls, line):
            #print('[ is_instruction ] {}'.format(ins_list))
            for ins in ins_list:
                if ins.is_instruction(line):
                    _install_current( ins )
                    return True

    #print('!!!', ins_list)
    return SmartList

def _line_to_slashs(line, deleters_in, need_debug=False):
    line = line.strip()
    start_line = line

    left = deleters_in[:len(deleters_in)/2+1]
    right = deleters_in[-1:-len(deleters_in) / 2:-1]

    if len(right) > len(left):
        left, right = left + right[-1:], right[:-1]
    elif len(left) + 1 > len(right):
        left, right = left[:-1], right + left[-1:]

    if need_debug:
        print('::: {} / {}'.format(left, right))

    ii_1 = []
    for l in left:
        if len(l) == 0:
            continue
        i = line.find(l)
        ii_1.append(ii_1)
        new_line = line[:i] + '|' + line[i+len(l):]
        if need_debug:
            print('\t{} [{}]: {} --> {}'.format(i, l, line, new_line))
        line = new_line

    for l in right:
        if len(l) == 0:
            continue
        i = line.rfind(l)
        if i < 0:
            return None
        if need_debug:
            print('\t{} [{}]: {} R'.format(i, l, line))
        line = line[:i] + '|' + line[i + len(l):]


    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]

    if need_debug:
        print('... {} --> {} --> {}'.format(start_line, deleters_in, line) )

    return line


from inspect import isclass

class _SmartMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(_SmartMeta, cls).__new__

        def check_bases(bases):
            for base in bases:
                if base == Smarter or issubclass(base, Smarter):
                    return True

        if 'Smarter' in globals() and 'SmarterProperty' in globals() and check_bases(bases) and name != 'Smarter':

            new_cls = super_new(cls, name, bases, attrs)

            base = bases[0]

            _LAST_GLOBALS = {} if base._GLOBALS == None else base._GLOBALS
            _GLOBALS = {}
            new_cls._GLOBALS = _GLOBALS

            for name in dir(new_cls):
                attr = getattr(new_cls, name)
                if name in _LAST_GLOBALS:
                    continue

                if isclass(attr) and type(attr) != type and issubclass(attr, SmarterProperty):
                    d = {}
                    attr = attr()
                    for nm in dir(attr):
                        if nm.startswith('_') or nm in ('mro',):
                            continue
                        d[nm] = getattr(attr, nm)
                    attr = _smart(**d)

                _GLOBALS[name] = attr

            new_cls._GLOBALS.update(_LAST_GLOBALS)

            return new_cls

        return super_new(cls, name, bases, attrs)


class Smarter(object):

    __metaclass__ = _SmartMeta

    _GLOBALS = None
    OUT_START = []

    @classmethod
    def translate(cls, text, filename=None, remove_space_lines=False):
        _getter = _Line.init_instructs(cls._GLOBALS, filename=filename)[1]
        out_text = _getter(text)
        out_text = '\n'.join(cls.OUT_START) + out_text
        if remove_space_lines:
            out_text = cls._remove_space_lines(out_text)
        return out_text

    @classmethod
    def translate_file(cls, filename, to_filename=None, remove_space_lines=False):
        text = open(filename).read()
        out_text = cls.translate(text, filename=filename, remove_space_lines=remove_space_lines)
        if to_filename:
            with open(to_filename, 'w') as f:
                f.write(out_text)
        else:
            return out_text

    @classmethod
    def _remove_space_lines(cls, text):
        lines = [li for li in text.split('\n') if len(li.strip()) > 0]
        return '\n'.join(lines)

class SmarterProperty(object):

    __metaclass__ = _SmartMeta

    IN_FORMAT = None
    OUT_FORMAT = None
    INDEX = None
    tst = False
    locals = None
    init_locals = None
    TYPE_OUT = None
    on_init = lambda _, self: None
    on_init_end = lambda _, self: None
    on_try_instruction = lambda _, self, i, line: None
    on_instruction = lambda _, self, i, ins: ins
    on_block_start = lambda _, self, block: None
    on_block_before_start = lambda _, self, block: None
    on_get_tree = lambda _, self, text: text
    BLOCK_START = '{'
    BLOCK_END = '}'
    full_line = False
    IN = None
    OUT = None


Translater = Smarter

accord = _smart

Accord = SmarterProperty

