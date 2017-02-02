# coding: utf-8
from copy import copy

try:
    from colorama import init
    from termcolor import colored
    init()
except ImportError:
    colored = lambda *args, **kwargs: None


# class _FilePath(str):
#
#     def __init__(self, s, line_number):
#         super(_FilePath, self).__init__(s)
#         self.line_number = line_number

# class _CoreKeyer:
#
#     def __init__(self, _locals):
#         self.__start_keys = _locals
#
#     def only_created(self, _locals):
#         __fin_keys = {}
#         for key in locals().keys():
#             if key in self.__start_keys or key.startswith('__'):
#                 continue
#             __fin_keys[key] = _locals[key]
#         return __fin_keys
#
#
# def make_core():
#     __keyer = _CoreKeyer(locals())

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


class _Base(object, _OtstupAbility):
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

    def __str__(self):
        return self.__class__.__name__ #+'({})'.format(id(self))

    def __repr__(self):
        return self.__str__()

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

        # while parent and 'class' not in parent.__class__.__name__.lower():
        #     parent = parent.block
        #     if parent:
        #         parent = parent.start_instruction
        #         #print('\t\t{}'.format(parent))
        #     #print('\t{} - {}'.format(parent, parent.block if parent else ''))

        cls_name = lambda: parent.START_NAME if hasattr(parent, 'START_NAME') else parent.__class__.__name__

        check_cls = lambda: 'class' != cls_name().lower if full_name else 'class' not in cls_name().lower()

        while parent and check_cls():
            while parent and '_Block' != parent.__class__.__name__:
                #print('\t{}'.format(parent))
                parent = parent.parent
            if parent:
                parent = parent.start_instruction
        return parent

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
    def _print_text_tree(text):
        b = _Block()
        b.add_lines(text.split('\n'), [0, len(text)])
        b.print_tree()

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
        # if len(lines[-1].strip()) > 0:
        #     raise Exception('\n\n\tYou have no clear line at the end of file!'+
        #                     "\n\tLast line: '{}'".format(lines[-1])+
        #                     '\n\tPlease add clean line at the end.')
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
        #print('try ({}): {}'.format(line_number, line))
        for ins in instructers:
            if ins.is_instruction(line):
                #print(ins)
                ins_o = ins(line, parent=parent, line_number=line_number)
                ins_o.init_otstup(line)
                return ins_o
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
        raise Exception('\n\n\tDont know instruction: "{}", line: {}, len: {} ( {filename} )'.format(
            line, line_number+1, len(line.strip()), filename=_Line._filename))
        #return _Line(line)

    def get_tree_main(self):
        return self.line


class _GoodLine(_Line):
    pass


class _Local(_Line):

    def __init__(self, line, parent=None, line_number=0):
        super(_Local, self).__init__(line, parent, line_number)


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

    def get_tree(self):
        if self.insert_childs:
            return '\n'.join([
                    self.get_tree_start(),
                    self.get_tree_base(),
                    self.get_tree_end()
                ])
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
        return '\n'.join( b.get_tree() for b in self.blocks ) #+ '::: {} : {}'.format(self.blocks[-1], self.blocks[-1].line_number)

    def get_tree_start(self):
        return ' ' * (self.otstup-4) + (self.start_instruction._BLOCK_START if self.otstup > 0 else '')

    def get_tree_end(self):
        return ' ' * (self.otstup-4) + (self.start_instruction._BLOCK_END if self.otstup > 0 else '')

    def get_locals(self):
        return self.start_instruction._locals if hasattr(self.start_instruction, '_locals') else {}

    def add_line(self, line, line_number, parent):
        #print('add_line: {} | {} | {}'.format(line, line_number, self))
        #if self.is_line_in_me_only(line):
        if True:

            #print('LLL', self, line)
            ins = _Line.try_instruction(line, line_number, parent=parent)
            if not ins:
                ins = self.try_local_instruction(line, line_number, parent)
            if ins:
                if _Block._debug:
                    print('[ {} ] {}'.format(ins, line))
                #print('{:>3}: {}{} ({})'.format(ins.line_number, ins.otstup_string(), ins, ins.parent))
                #print('\tappend', line, ins)
                self.blocks.append(ins.set_block(self))
                #self.lines.append(line)

                if type(ins) != _Line: #or ins.line.strip() != 0:
                    self.last_instruction = ins

        #     return True
        # if len(line.strip()) == 0:
        #     return None
        # return False

    def try_local_instruction(self, line, line_number, parent):
        stripped = line.strip()
        for name, val in self.get_locals().items():
            if stripped.startswith(name + '.'):
                return _Local(line, parent=parent, line_number=line_number)

    def is_line_in_me(self, line):
        return len(line.strip()) == 0 or _Base.get_otstup(line) >= self.otstup

    def is_line_in_me_only(self, line):
        return _Base.get_otstup(line) == self.otstup or len(line.strip()) == 0

    def is_line_block(self, line):
        return _Base.get_otstup(line) > self.otstup

    def add_lines(self, lines, diapazon):
        tst_lines = copy(lines)
        diapazon = copy(diapazon)

        while len(tst_lines):
            line = tst_lines[0]
            #print('>>>', diapazon[0], line, self.is_line_block(line), id(self))
            if self.is_line_block(line):
                #print('INBLOCK')
                #print('# ^^^ ' +line)
                #print('#$$$ ', self.last_instruction.line)
                #self.blocks.append(_Line(self.otstup_string() + '[ BLOCK ] {}'.format(self.last_instruction.line)))

                if self.last_block:
                    # FIXME
                    if ( len(self.last_block.blocks) > 0 and type(self.last_block.blocks[-1]) == _Line and
                                 len(self.last_block.blocks[-1].line.strip()) == 0 ):
                        del self.last_block.blocks[-1]

                b = _Block(parent=self, line=line,
                           start_instruction=self.last_instruction)
                self.last_block = b
                #print(' '*b.otstup + '[ BLOCK ] {} ({})'.format(diapazon, id(b)))
                after_in_lines = b.add_lines(tst_lines, diapazon)

                #print('-'*10)
                #print( '\n'.join(after_in_lines) )

                if hasattr(self.last_instruction, 'on_block_start'):
                    self.last_instruction.on_block_start(b)

                d = len(tst_lines) - len(after_in_lines)

                tst_lines = after_in_lines
                # if len(after_in_lines) == 0:
                #     print( '{{{', len(tst_lines), d )
                #     break
                if d > 0:
                    #print('!!!!', d, tst_lines[d:], len(tst_lines[d:]), len(after_in_lines))
                    #self.blocks[-1].line = self.blocks[-1].line.replace(':', ' {') #+= ' {' # !!!
                    #tst_lines = tst_lines[d-1:]
                    diapazon[0] += d-1
                    self.blocks.append(b)
                else:
                    break

                #self.last_instruction = None

            else:
                #print('---', line)

                last_lines = tst_lines
                tst_lines = tst_lines[1:]
                diapazon[0] += 1
                if self.start_instruction and self.start_instruction.is_param_line(line):
                    self.start_instruction.add_param_line(line)
                    continue
                #print('....', line)
                if self.is_line_in_me_only(line):
                    ret = self.add_line(line, diapazon[0]-1, self)
                    # if ret == None:
                    #     #print('# --- {}'.format(line))
                    #     #print('\treturn {}'.format(len(tst_lines)))
                    #     return last_lines
                    # else:
                    #     print(':::', line)
                # elif len(line.strip()) == 0:
                #     pass
                else:
                    #print('***', line)
                    #last_lines.insert(0, line)
                    #self.blocks.append(_Line(self.otstup_string(-4) + '[ END ]'))

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