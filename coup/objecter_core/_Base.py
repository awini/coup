# coding: utf-8
from copy import copy
import sys as _sys

try:
    from colorama import init
    from termcolor import colored
    init()
except ImportError:
    colored = lambda *args, **kwargs: None


class _OtstupAbility:

    otstup = 0

    @staticmethod
    def get_otstup(line):
        stripped = line.lstrip()
        if len(stripped) > 0:
            return len(line) - len(line.lstrip())
        return 0 #-1

    def init_otstup(self, line):
        if _Base.STANDART_OTSTUP != None:
            self.otstup = _Base.STANDART_OTSTUP
            return
        self.otstup = self.get_otstup(line)

    def otstup_string(self, add_otstup=0):
        return ' ' * (self.otstup + add_otstup)


def _base_bases():
    if _sys.version_info.major >= 3:
        return _OtstupAbility
    class _BaseBase(object, _OtstupAbility):
        pass
    return _BaseBase


class _Base(_base_bases()):
    r'''Base class for all translate classes.

Implement those methods in child:

    def get_tree_main(self): - for return translated text

    @classmethod
    def is_instruction(cls, line): - for check if line is those instruction
    '''

    FULL_LINE_PARENTER = 1  # print(), for-in...
    IN_LINE_PARENTER = 2  # x = "", [ for-in ]...
    IN_LINE_CHILD = 3
    IN_LINE_CHILD_LAST = 9999999999

    INDEX = IN_LINE_CHILD # для порядка / приоритета между классами

    TYPE_IN = None # тип выходного значения инструкции (на языке источнике) - по-умолчания без типа
    TYPE_OUT = None # тип выходного значения инструкции (на языке назначения) - по-умолчания без типа

    _BLOCK_START = '{'
    _BLOCK_END = '}'

    block = None
    in_block = None
    STANDART_OTSTUP = None

    def __init__(self, line, parent=None, line_number=0):
        self.line = line
        self.parent = parent
        self.line_number = line_number

    @classmethod
    def to_str(cls):
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__ #+'({})'.format(id(self))

    def __repr__(self):
        return self.__str__()

    def get_unknown_instructions(self):
        if hasattr(self, 'instructions'):
            return [ ins for ins in self.instructions if type(ins) == _UnknownLine ]
        return []

    def find_type_instruction(self, tip):
        for ins in self.instructions:
            if isinstance(ins, list) or isinstance(ins, tuple):
                for ii in ins:
                    if type(ii) == tip:
                        return ii
            if type(ins) == tip:
                return ins

    def get_parent_class(self, full_name=False):
        parent = self.parent

        cls_name = lambda: parent.START_NAME if hasattr(parent, 'START_NAME') else parent.__class__.__name__

        check_cls = lambda: 'class' != cls_name().lower if full_name else 'class' not in cls_name().lower()

        while parent and check_cls():
            while parent and '_Block' != parent.__class__.__name__:
                #print('\t{}'.format(parent))
                parent = parent.parent
            if parent:
                parent = parent.start_instruction
        return parent

    def find_def(self):
        obj = self
        while obj and not obj.is_def() and obj.parent:
            #print('......{}, locals: {}'.format(obj, obj.locals if hasattr(obj, 'locals') else '-'))
            obj = obj.parent.start_instruction
        return obj

    def is_def(self):
        return hasattr(self, 'locals') and self.locals != None

    def get_parent_block(self, child_blocker=None):
        if child_blocker:
            child_blocker[0] = self
        parent = self.parent
        while parent and parent.__class__.__name__ != '_Block':
            if child_blocker:
                child_blocker[0] = parent
            parent = parent.parent
        return parent

    def get_children(self):
        return [ a for a in self.get_children_all() if a.__class__ != _Line ]

    def get_children_all(self):
        if self.in_block:
            return self.in_block.children
        return []

    def set_block(self, block):
        self.block = block
        block.children.append(self)
        return self

    def get_parent(self):
        return self.block.start_instruction if self.block else None

    def get_tree(self):
        #print('log: {}'.format(self))
        return ' '*self.otstup + self.get_tree_main()

    def get_tree_main(self):
        raise NotImplementedError

    def print_tree_base(self):
        raise NotImplementedError

    def print_tree(self):
        print(self.get_tree())

    def is_param_line(self, line):
        return False

    def add_param_line(self, line):
        raise NotImplementedError

class _BlockStartBase(_Base):

    NAME = None

    def __init__(self, line, parent=None, line_number=0):
        super(_BlockStartBase, self).__init__(line, parent, line_number)

    @classmethod
    def is_instruction(cls, line):
        stripped = line.strip()
        if type(cls.NAME) in (list, tuple):
            for waited_name in cls.NAME:
                ret = cls.check_name(stripped, waited_name)
                if ret:
                    return ret
        else:
            #print(cls, stripped)
            ret = cls.check_name(stripped, cls.NAME)
            if ret:
                return ret

    @staticmethod
    def check_name(name, waited_name):
        if name == waited_name + ':':
            return name
        if waited_name.count('{NAME}') == 1:
            lst = waited_name.split('{NAME}')
            name_into = name[len(lst[0]):-len(lst[1])-1]
            #print(name, waited_name, name_into)
            if name == waited_name.format(NAME = name_into) + ':':
                return name

class _ImportsAbility:

    _BLOCK_IMPORT = []
    _imports = set()

    @property
    def _BLOCK_PREFIX(self):
        if not self.is_need_show_imports():
            return ''
        return '\n'.join(_ImportsAbility._imports) + '\n'

    def is_need_show_imports(self):
        return len(_ImportsAbility._imports) > 0

    def get_prefix(self):
        bp = self._BLOCK_PREFIX
        pref = (bp + self.otstup_string()) if len(bp) else ''
        if len(pref) > 0:
            return pref + '\n'
        return ''

    def init_imports(self):
        if len(self._BLOCK_IMPORT):
            for b in self._BLOCK_IMPORT:
                _ImportsAbility._imports.add(b)

    def otstup_string(self):
        raise NotImplementedError


class _BlockStartCounting(_BlockStartBase, _ImportsAbility):

    perem_num = None
    _perems_count = 0

    @staticmethod
    def init_counting():
        _BlockStartCounting._perems_count = 0

    @staticmethod
    def init_instructs(_globals, filename=None):
        def _restarter(func):
            def new_func(*args, **kwargs):
                _BlockStartCounting.init_counting()
                return func(*args, **kwargs)
            return new_func
        printer, getter = _Line.init_instructs(_globals, filename=filename)
        return _restarter(printer), _restarter(getter)

    def __init__(self, line, parent=None, line_number=0):
        super(_BlockStartCounting, self).__init__(line, parent, line_number)

        _BlockStartCounting._perems_count += 1
        self.perem_num = _BlockStartCounting._perems_count

        self.init_imports()

    def is_need_show_imports(self):
        return self.perem_num == 1 and _ImportsAbility.is_need_show_imports(self)


class _Line(_Base):
    r'''Representer of clean line and main instructs tryer.

    You need no subclass by this class.

        '''

    _INSTRUCTS = None
    _GLOBALS = {}
    _filename = None

    def __init__(self, line, parent=None, line_number=0, new_name=False):
        super(_Line, self).__init__(line, parent, line_number)
        line = line.strip()
        self.in_glob_adder = False
        if len(line) > 0 and new_name:
            if line not in self._GLOBALS:
                #print('----------->', line, id(self))
                self.in_glob_adder = True
            self._GLOBALS[ line ] = self

    def __eq__(self, other):
        return isinstance(other, _Line) and other.line.strip() == self.line.strip()

    def __str__(self):
        return '_Line("'+ self.line +'")'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def init_instructs(_globals, filename=None, only_tree=False):
        _Line._filename = filename

        _Line._INSTRUCTS = [ v for name, v in _globals.items()
                             if not name.startswith('_') and hasattr(v, 'is_instruction') ]
        _Line._INSTRUCTS = sorted( _Line._INSTRUCTS, key = lambda ins: ins.INDEX )
        #print('\n'.join('{} = {}'.format(i, i.INDEX) for i in _Line._INSTRUCTS))
        return _Line._print_text_tree, ( _Line._get_objects_tree if only_tree else _Line._get_text_tree )

    @staticmethod
    def _print_text_tree(text=None):
        if text:
            b = _Block()
            b.add_lines(text.split('\n'), [0, len(text)])
            b.print_tree()
        else:
            for ins in sorted(_Line._INSTRUCTS, key=lambda ins:ins.INDEX):
                print('{:>12}. {}'.format(ins.INDEX, ins.to_str()))

    @staticmethod
    def _get_text_tree(text):
        b = _Line._get_objects_tree(text)
        ret = b.get_tree()
        return ret

    @staticmethod
    def _get_objects_tree(text, debug=False):
        _Block._debug = debug
        _Block.clear_errors()
        b = _Block()
        lines = text.split('\n')
        b.add_lines(lines, [0, len(text)])
        return b

    @staticmethod
    def try_instruction(line, line_number, parent, no_instructs_react=None):
        return _Line.try_instruction_base(line, _Line._INSTRUCTS, line_number=line_number,
                                          parent = parent,
                                          no_instructs_react=no_instructs_react)

    @staticmethod
    def try_instruction_base(line, instructers, parent=None, line_number=0,
                             no_instructs_react=None):

        got_instructs = []
        was_unknown = copy(_UnknownLine._unknown_lines)

        for ins in instructers:
            if ins.is_instruction(line):
                #print(ins)
                ins_o = ins(line, parent=parent, line_number=line_number)
                ins_o.init_otstup(line)

                unknown = ins_o.get_unknown_instructions()
                if len(unknown) == 0:
                    #print(ins_o, '!!!!!!!!>>>>>>>>>!!!!!!!!', unknown)
                    _UnknownLine._unknown_lines = was_unknown
                    return ins_o
                else:
                    got_instructs.append((ins_o, len(unknown), unknown))

        if len(got_instructs) > 0:
            gt = sorted(got_instructs, lambda g:g[1])[0]
            gi = gt[0]
            _UnknownLine._unknown_lines = was_unknown
            _UnknownLine._unknown_lines += gt[2]


        ln = len(line.strip())
        is_space = ln == 0
        if is_space:
            return _Line(line, line_number=line_number, parent=parent)

        stripped = line.strip()
        if stripped in _Line._GLOBALS:
            return _Line._GLOBALS[ stripped ]

        #print('...', parent)
        block = parent if isinstance(parent, _Block) else parent.get_parent_block()

        ins_o = block.try_local_instruction(line, line_number, parent)
        if ins_o:
            return ins_o

        if no_instructs_react:
            ret = no_instructs_react(stripped, line_number, parent=parent)
            if ret:
                return ret

        #_Block.errors.append(str('\n\n\tDont know instruction: "{}", line: {}, len: {}'.format(line, line_number+1, len(line.strip()))))
        # raise Exception(colored('\n\n\tDont know instruction: "{}", line: {}, len: {} ( {filename} )'.format(
        #     line, line_number+1, len(line.strip()), filename=_Line._filename), 'red'))
        #return _Line(line)
        return _UnknownLine(line, parent=parent, line_number=line_number)

    def get_tree_main(self):
        return self.line


class _GoodLine(_Line):
    pass

class _ToDeleteLine(_Line):
    def __add__(self, other):
        return _ToDeleteLine(self.line+other)
    def __radd__(self, other):
        return _ToDeleteLine(other+self.line)
    def split(self, s):
        return []

class _UnknownLine(_Base):

    _unknown_lines = []

    def __init__(self, line, parent=None, line_number=0):
        super(_UnknownLine, self).__init__(line, parent, line_number)
        _UnknownLine._unknown_lines.append(self)

    def __str__(self):
        return '_UnknownLine: {}, line: {}'.format(
            colored(self.line.strip(), 'red'), self.line_number+1)
            #    self.line.line_number if hasattr(self.line, 'line_number') else '-')

    def __repr__(self):
        return self.__str__()


class _Local(_Line):

    def __init__(self, line, parent=None, line_number=0):
        super(_Local, self).__init__(line, parent, line_number)

# class _TstList(list):
#     def jo

class _TstLine(str):
    line_number = 0

    def strip(self, chars=None):
        s = super(_TstLine, self).strip(chars)
        return _tst_line(s, self.line_number)

    def split(self, sep=None, maxsplit=-1):
        return [ _tst_line(s, self.line_number) for s in super(_TstLine, self).split(sep, maxsplit)]

    def __getitem__(self, key):
        #print('_________________ {}'.format(key))
        s = super(_TstLine, self).__getitem__(key)
        return _tst_line(s, self.line_number)

    def __add__(self, other):
        s = super(_TstLine, self).__add__(other)
        return _tst_line(s, self.line_number)


def _tst_line(s, line_number):
    if type(s) == _TstLine:
        return s
    t = _TstLine(s)
    t.line_number = line_number
    return t


class _Block(_OtstupAbility):
    r'''Main block finder and object of represent.

First of all _Block parses all text for inside blocks, then on got structer, starts searching of expressions (line translaters).

You need no subclass by this class.

    '''

    _debug = False
    errors = []

    @staticmethod
    def clear_errors():
        _Block.errors[:] = []


    blocker = True
    _BLOCKS_COUNT = 0

    _BLOCK_START = '{'
    _BLOCK_END = '}'

    insert_childs = True

    def __init__(self, line="", i=0, parent=None, start_instruction=None):
        _Block._BLOCKS_COUNT += 1
        self.b_id = _Block._BLOCKS_COUNT
        self.i = i
        self.parent = parent
        self.otstup = _Base.get_otstup(line)
        self.blocks = []
        self.last_instruction = None
        self.start_instruction = start_instruction
        if start_instruction:
            start_instruction.in_block = self
        self.children = []
        self.last_block = None

    def __str__(self):
        return self.__class__.__name__ +'[{}: {}]'.format(self.start_instruction, id(self))

    def __repr__(self):
        return self.__str__()

    def is_def(self):
        return False

    def get_tree(self):
        ln = len(_UnknownLine._unknown_lines)
        if ln > 0:
            text = ''
            for i, ul in enumerate(_UnknownLine._unknown_lines):
                text += '\n\t{:>2}. {}'.format(i+1, ul)
            raise Exception(colored('{} unknown instructions:'.format(ln), 'red')+text)

        if self.insert_childs:
            start, base, end = self.get_tree_start(), self.get_tree_base(), self.get_tree_end()
            if type(base) == _ToDeleteLine:
                return base
            return (
                ((start + '\n') if type(start) != _ToDeleteLine else '')
                + base +
                (('\n' + end) if type(end) != _ToDeleteLine else '')
            )

        else:
            self.get_tree_base() # needed
            return '\n'.join([
                self.get_tree_start(),
                self.get_tree_end()
            ])

    def print_tree(self):
        print(self.get_tree_start())
        print(colored(' ' * self.otstup + '[ block - {} ]'.format(self.b_id), 'green'))
        self.print_tree_base()
        print(colored(' ' * self.otstup + '[ block - {} - end]'.format(self.b_id), 'green'))
        print(self.get_tree_end())

    def print_tree_base(self):
        for b in self.blocks:
            b.print_tree()

    def get_tree_base(self):
        gen = ( b.get_tree() for b in self.blocks )
        return '\n'.join( b for b in gen if type(b) != _ToDeleteLine ) #+ '::: {} : {}'.format(self.blocks[-1], self.blocks[-1].line_number)

    def get_tree_start(self):
        try:
            return ' ' * (self.otstup-4) + (self.start_instruction._BLOCK_START if self.otstup > 0 else '')
        except Exception as e:
            print('------> {}'.format(self))
            raise

    def get_tree_end(self):
        return ' ' * (self.otstup-4) + (self.start_instruction._BLOCK_END if self.otstup > 0 else '')

    def get_locals(self):
        #return ( self.start_instruction.locals or {} ) if hasattr(self.start_instruction, 'locals') else {}

        func = self.start_instruction.find_def()
        #print('..def: {}'.format(func))

        return func.locals if hasattr(func, 'locals') else {}

    def add_line(self, line, line_number, parent, ignore=False):
        #print('[ {:>3} ]: {} | {}'.format(line_number, line, line.line_number))
        line_number = line.line_number
        if ignore:
            ins = ignore(line, line_number=line_number, parent=parent)
            self.last_instruction = ins
        else:
            ins = _Line.try_instruction(line, line_number, parent=parent)
            if not ins:
                ins = self.try_local_instruction(line, line_number, parent)
            if ins:
                if _Block._debug:
                    print('[ {} ] {}'.format(ins, line))
                self.blocks.append(ins.set_block(self))

                if type(ins) != _Line:
                    self.last_instruction = ins

    def try_local_instruction(self, line, line_number, parent):
        #print('[ !!! try_local_instruction ] {} | {}'.format(self, line))
        stripped = line.strip()
        for name, val in self.get_locals().items():
            #print('..local: {} = {}'.format(name, val))
            if stripped.startswith(name + '.') or stripped == name:
                return _Local(line, parent=parent, line_number=line_number)

    # ===================

    # def is_line_in_me(self, line):
    #     return len(line.strip()) == 0 or _Base.get_otstup(line) >= self.otstup

    def is_line_starts_block(self, line):
        return _Base.get_otstup(line) > self.otstup

    def is_line_continue_block(self, line):
        return _Base.get_otstup(line) == self.otstup or len(line.strip()) == 0

    # ===================

    def add_lines(self, lines, diapazon, ignore=False):
        tst_lines = [ _tst_line(line, i) for i, line in enumerate(lines) ]
        #tst_lines = _Lines(lines)
        #tst_lines = copy(lines)
        diapazon = copy(diapazon)
        #print('@@@ lines: {}:{}'.format(diapazon[0], diapazon[1]))

        #while not tst_lines.empty():
        while len(tst_lines):
            line = tst_lines[0]
            if self.is_line_starts_block(line):
                if self.last_block:
                    # FIXME
                    if ( len(self.last_block.blocks) > 0 and type(self.last_block.blocks[-1]) == _Line and
                                 len(self.last_block.blocks[-1].line.strip()) == 0 ):
                        del self.last_block.blocks[-1]

                b = _Block(parent=self, line=line,
                           start_instruction=self.last_instruction)
                self.last_block = b

                smart_ret = None
                if hasattr(self.last_instruction, 'on_block_before_start'):
                    smart_ret = self.last_instruction.on_block_before_start(b)

                after_in_lines = b.add_lines(tst_lines, diapazon, ignore or smart_ret)

                if hasattr(self.last_instruction, 'on_block_start'):
                    self.last_instruction.on_block_start(b)

                d = len(tst_lines) - len(after_in_lines)

                tst_lines = after_in_lines
                if d > 0:
                    diapazon[0] += d-1
                    self.blocks.append(b)
                else:
                    break
            else:
                last_lines = tst_lines
                tst_lines = tst_lines[1:]
                diapazon[0] += 1
                if self.start_instruction and self.start_instruction.is_param_line(line):
                    self.start_instruction.add_param_line(line)
                    continue
                if self.is_line_continue_block(line):
                    ret = self.add_line(line, diapazon[0]-1, self, ignore=ignore)
                else:
                    return last_lines

        return tst_lines

    def is_end(self, line):
        otstup = _Base.get_otstup(line)
        # print('... {} ( {} ) | {}'.format(otstup, self.otstup, line))
        if otstup >= 0 and otstup <= self.otstup:
            return ' ' * self.otstup + _Block._BLOCK_END+'\n' + line
        return False

    @staticmethod
    def is_start(line):
        if line.rstrip().endswith(':'):
            return True
        return False

    def get_block_index(self, block):
        return self.children.index(block) if block in self.children else -1

    #return __keyer.only_created(locals())