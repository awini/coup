# coding: utf-8
from copy import copy
import sys as _sys
from os.path import abspath, join, dirname

try:
    from colorama import init
    from termcolor import colored
    init()
except ImportError:
    colored = lambda text, *args, **kwargs: text

PATH_TO_THIS_DIR = dirname(abspath(__file__))
PATH_TO_HIGHLIGHT_JS = join(PATH_TO_THIS_DIR, '..', 'external', 'highlight', 'highlight.pack.js')
PATH_TO_HIGHLIGHT_CSS = join(PATH_TO_THIS_DIR, '..', 'external', 'highlight', 'styles', 'default.css')


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
    _INSTRUCTION_LINE_ENDING = ''

    block = None
    in_block = None
    STANDART_OTSTUP = None

    _IS_CATCHING = 0
    _SHOW_ERRORS_IN_HTML = True
    _LOG_ENABLED = True

    def __init__(self, line, parent=None, line_number=0):
        self.line = line
        self.parent = parent
        self.line_number = line_number
        self.is_comment = False
        self.is_method = None

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

    def get_parent_class(self, full_name=False, or_last_true=False):
        parent = self.parent
        last_parent = self

        cls_name = lambda: parent.START_NAME if hasattr(parent, 'START_NAME') else parent.__class__.__name__

        check_cls = lambda: 'class' != cls_name().lower if full_name else 'class' not in cls_name().lower()

        while parent and check_cls():
            while parent and '_Block' != parent.__class__.__name__:
                #print('\t{}'.format(parent))
                parent = parent.parent
            if parent:
                parent = parent.start_instruction
            if parent:
                last_parent = parent
        if not parent and or_last_true:
            return last_parent
        return parent

    def get_block_level(self):
        i = 0
        parent = self
        while hasattr(parent, 'parent') and hasattr(parent.parent, 'start_instruction'):
            parent = parent.parent.start_instruction
            i += 1
        return i

    def get_locals(self):
        # print('......', self.block)
        # print('......', self.parent, self.parent.locals)
        # print('......', self, self.locals)
        if hasattr(self, 'locals') and self.locals:
            if hasattr(self.locals, '__call__'):
                return self.locals(self)
            return self.locals
        parent = self.parent
        if parent:
            #print('......', parent)
            if hasattr(parent, 'locals') and parent.locals:
                #print('.......', parent.locals)
                if hasattr(parent.locals, '__call__'):
                    return parent.locals(parent)
                return parent.locals
            return parent.get_locals()

    def find_def(self):
        obj = self
        while obj and not obj.is_def() and obj.parent:
            #print('......{}, locals: {}'.format(obj, obj.locals if hasattr(obj, 'locals') else '-'))
            obj = obj.parent.start_instruction
        return obj

    def is_def(self):
        return hasattr(self, 'locals') and self.locals != None      # FIXME

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
        return ' '*self.otstup + self.get_tree_main()

    def make_objects_tree_html(self):
        lines = []
        ids = []

        if _Base._IS_CATCHING > 0:
            return

        _Base._IS_CATCHING += 1

        def make_full_line(self, hidden=False):
            ids.append(self)
            _id = ids.index(self)
            _parent_id = ids.index(self.parent.start_instruction) if self.parent and hasattr(self.parent, 'start_instruction') and self.parent.start_instruction else '-'

            is_last_child = False
            if self.parent and hasattr(self.parent, 'blocks') and len(self.parent.blocks) > 0:
                last_parent_block = self.parent.blocks[-1]
                if self == last_parent_block or (hasattr(last_parent_block, 'start_instruction') and last_parent_block.start_instruction == self):
                    is_last_child = True

            if self.__class__ == _UnknownLine:
                self.init_otstup(self.line)

            padding_left = 4 + self.otstup * 4
            is_block_start = True if self.in_block else False
            childs_count = len(self.in_block.blocks) if is_block_start else 0
            make_line = lambda text, need_pad=True, hidden=False: '<span class="coup-line{add_class}"><span class="coup-freespace" style="width:{pad}px;"></span>'.format(
                pad=padding_left if need_pad else 0, add_class=' hidden' if hidden else '') + text + '</span>'

            if self.__class__ == _UnknownLine:
                _line_result = '_unk'
            else:
                try:
                    _line_result = self.get_tree_main() if self.__class__ != _Block else self.start_instrustion.get_tree_main()
                except:
                    _line_result = '-'

            if is_block_start:
                _line_result += ' ' + self._BLOCK_START
            elif is_last_child:
                _line_result += ' ' + self.parent._BLOCK_END


            _locals = self.get_locals()

            lines.append('<p id="p{}" class="child-of-p{}" style="{}" onclick="click_p(this);" onmouseover="show_info(this);">'.format(_id, _parent_id, 'display:none;' if False and hidden else '') +
                         '<span style="min-width:30px;display:inline-block;">{} ({}):</span>'.format(self.line_number, childs_count) +
                         make_line(self.line, need_pad=False, hidden=True) +
                         make_line(str(self).replace('<','[').replace('>',']').replace('[31m','<span class="red">').replace('[0m','</span>'), hidden=True) +
                         make_line(_line_result) +
                         make_line(str(_locals), hidden=True) +
                         '</p>')

        make_full_line(self)
        if self.in_block:
            for bins in self.in_block.instuctions_lines_gen():
                make_full_line(bins, hidden=True)

        return '\n'.join([ line for line in lines if line.__class__ != _ToDeleteLine ])

    def get_tree_main(self):
        inss = self.parent.instructions if self.parent else ''
        self.show_tree_into_html()
        raise NotImplementedError('in: {} in {}\n\t{}'.format(self, self.parent, inss))

    def show_tree_into_html(self):
        if not _Base._SHOW_ERRORS_IN_HTML:
            return

        root_class = self.get_parent_class(or_last_true=True)

        import os
        if not os.path.exists('build'):
            os.makedirs('build')

        execute_log = ''
        if os.path.exists('build/execute_android.log'):
            execute_log = open('build/execute_android.log').read().replace('>', ']').replace('<','[').replace('\n', '<br>')

        html = '''<html>
<head>
<meta charset="UTF-8">
<style>
html, body {
    _min-width:3000px;
    margin: 0; padding: 0;
    width: 100%; height: 100%;
}
.top-panel {
    margin: 0; padding: 0;
    width: 100%; height: 80%;
}
.code-haver {
    margin: 0; padding: 0;
    width: 50%; height: 100%;
    overflow: auto;
    float:left;
}
.log-haver {
    margin: 0; padding: 0;
    height: 100%; width: 50%;
    overflow: auto;
    float:left;
    halign:left;
}
.code-haver p {margin:0; padding:0; height:14px; border-bottom_:1px solid #aaa; font-family_:"Helvetica"; color:#333; font-size:12px;}
.code-haver p:hover {
    background: #a2c7e3; /* Цвет фона под ссылкой */
    color: #08406b; /* Цвет ссылки */
}
.code-haver p .coup-line {
    border-right:1px solid #aaa;
    min-width:800px;display:inline-block;
    width:800px;
    overflow:hidden;
    height:14px;
}
.code-haver p .hidden {
    display: none;
}
.code-haver p .coup-freespace {
    display:inline-block;
}
.red {color:#ff0000;}
</style>
<link rel="stylesheet" href="{highlight_css}">
<script src="{highlight_js}"></script>
<script>hljs.initHighlightingOnLoad();</script>
</head>
<script>
function click_p(p) {
    var i;
    var _id = p.id;
    console.log('p:', p);
    var pps = document.getElementsByTagName("p");
    for (i=0; i<pps.length;i++) {
        var ch = pps[i];
        //console.log('parent:', ch.className);
        if (ch.className == 'child-of-'+_id) {
            console.log('child:', ch);
            ch.style.display = 'block';
        }
    }
}
function show_info(p) {
    info.innerHTML = 'source: ' + p.children[1].innerHTML + '<br>result: ' + p.children[3].innerHTML + '<br>object: ' + p.children[2].innerHTML + '<br>locals: ' + p.children[4].innerHTML;
}
</script>
<body>
<div class=top-panel>
    <div class='code-haver'>
        <pre><code class="python">
            '''.replace('{highlight_js}', PATH_TO_HIGHLIGHT_JS).replace(
                    '{highlight_css}', PATH_TO_HIGHLIGHT_CSS) + root_class.make_objects_tree_html() + '''
        </code></pre>
    </div>
    <div class='log-haver'>
        <p>{log_text}</p>
    </div>
</div>
<div id='info'>
</div>
</body>'''.replace('{log_text}', execute_log)
        with open('build/coup_errors.html', 'w') as f:
            f.write(html)

        import os, sys
        from subprocess import Popen

        com = os.path.abspath(os.path.join('build', 'coup_errors.html'))
        if sys.platform == 'darwin':
            com = 'open ' + com
        elif sys.platform.startswith('win'):
            path = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            if os.path.exists(path):
                com = r'"{}" '.format(path) + com
            # ret = call(com2, shell=True)
            # if ret < 0:
            #     call(com, shell=True)
            # return

        Popen(com, shell=True)

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
    def is_instruction(cls, line, parent=None, line_number=None):
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
    _logger = None

    def __init__(self, line, parent=None, line_number=0, new_name=False):
        super(_Line, self).__init__(line, parent, line_number)
        line = line.strip()
        self.in_glob_adder = False
        if len(line) > 0 and new_name:
            if line not in self._GLOBALS:
                #print('----------->', line, id(self))
                self.in_glob_adder = True
            self.line = line
            self._GLOBALS[ line ] = self

    def __eq__(self, other):
        return isinstance(other, _Line) and other.line.strip() == self.line.strip()

    def __str__(self):
        return self.__class__.__name__+'("'+ self.line +'")'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def log(text):
        if _Line._logger:
            _Line._logger.write(text + '\n')

    @staticmethod
    def init_instructs(_globals, filename=None, only_tree=False, logger=None):
        _Line._filename = filename
        _Line._logger = logger

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
        b.locals = {}
        #print('>>>>>> main locals: {}'.format(id(b.locals)))
        lines = text.split('\n')
        b.add_lines(lines, [0, len(text)])
        return b

    @staticmethod
    def try_instruction(line, line_number, parent, no_instructs_react=None, info_finder=None):
        return _Line.try_instruction_base(line, _Line._INSTRUCTS, line_number=line_number,
                                          parent = parent,
                                          no_instructs_react=no_instructs_react,
                                          info_finder = info_finder)

    @staticmethod
    def try_instruction_base(line, instructers, parent=None, line_number=0,
                             no_instructs_react=None, info_finder=None):

        got_instructs = []
        was_unknown = copy(_UnknownLine._unknown_lines)

        # if info_finder:
        #     print('>> !')

        for ins in instructers:
            if ins.is_instruction(line, parent=parent, line_number=line_number):
                #print(ins)
                try:
                    ins_o = ins(line, parent=parent, line_number=line_number)
                    # if info_finder:
                    #     print('got ins_o: "{}" from "{}"'.format(ins_o, ins))
                except Exception:
                    #_UnknownLine._unknown_lines.append(_UnknownLine(line))
                    return
                ins_o.init_otstup(line)

                unknown = ins_o.get_unknown_instructions()
                if len(unknown) == 0:
                    _UnknownLine._unknown_lines = was_unknown
                    return ins_o
                else:
                    got_instructs.append((ins_o, len(unknown), unknown))

        if len(got_instructs) > 0:
            gt = sorted(got_instructs, key=lambda *g:g[0][1])[0]
            gi = gt[0]
            _UnknownLine._unknown_lines = was_unknown
            _UnknownLine._unknown_lines += gt[2]


        ln = len(line.strip())
        is_space = ln == 0
        if is_space:
            return _Line(line, line_number=line_number, parent=parent)

        stripped = line.strip()
        if stripped in _Line._GLOBALS: # FIXME what with locals????

            # if info_finder:
            #     print('>> stripped in _Line._GLOBALS', _Line._GLOBALS[ stripped ])

            return _GlobalName(_Line._GLOBALS[ stripped ].line)

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

class _GlobalName(_GoodLine):
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
        _UnknownLine._unknown_lines[:] = []


    blocker = True
    _BLOCKS_COUNT = 0

    _BLOCK_START = '{'
    _BLOCK_END = '}'

    insert_childs = True
    _ignore_start_block = False
    simple_line_end = ''
    var_format = '{}'
    method_format = '{}'

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
                if i == 0:
                    ul.show_tree_into_html()
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
        gen = ( (b.get_tree(), b) for b in self.blocks )
        gen = ( (t, b) for t, b in gen if type(t) != _ToDeleteLine )
        make_end = lambda b: b._INSTRUCTION_LINE_ENDING if hasattr(b, '_INSTRUCTION_LINE_ENDING') and len(b._INSTRUCTION_LINE_ENDING) > 0 else _Block.simple_line_end
        make_text = lambda t, b: (t+make_end(b)) if len(t.strip()) and not isinstance(b, _Block) and not b.in_block and (not b.is_comment and (len(b.instructions)==0 or not b.instructions[-1].is_comment)) else t
        return '\n'.join( make_text(t,b) for t, b in gen ) #+ '::: {} : {}'.format(self.blocks[-1], self.blocks[-1].line_number)

    def instuctions_lines_gen(self):
        for b in self.blocks:
            if b.__class__ == _Block:
                for bb in b.instuctions_lines_gen():
                    yield bb
            else:
                yield b

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

        if not self.start_instruction:
            if hasattr(self, 'locals') and type(self.locals) == dict:
                return self.locals
            return {}

        func = self.start_instruction.find_def()
        #print('..def: {}'.format(func))
        locals = func.locals if hasattr(func, 'locals') else {}
        if hasattr(locals, '__call__'):
            locals = locals(func)
            # if len(locals) > 0:
            #     print('................', self.start_instruction, locals.keys())

        return locals

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
        # FIXME think, is it needed...
        return

        stripped = line.strip()
        for name, val in self.get_locals().items():
            #print('..local: {} = {}'.format(name, val))
            if stripped.startswith(name + '.') or stripped == name:
                return _Local(line, parent=parent, line_number=line_number)

    # ===================

    # def is_line_in_me(self, line):
    #     return len(line.strip()) == 0 or _Base.get_otstup(line) >= self.otstup

    def is_line_starts_block(self, line):
        if self._ignore_start_block:
            return False
        return _Base.get_otstup(line) > self.otstup

    def is_line_continue_block(self, line):
        if self._ignore_start_block:
            return True
        return _Base.get_otstup(line) == self.otstup or len(line.strip()) == 0

    # ===================

    def add_lines(self, lines, diapazon, ignore=False):
        tst_lines = [ _tst_line(line, i) for i, line in enumerate(lines) ]
        #tst_lines = _Lines(lines)
        #tst_lines = copy(lines)
        diapazon = copy(diapazon)
        #print('@@@ lines: {}:{}'.format(diapazon[0], diapazon[1]))

        b = None

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
                    try:
                        smart_ret = self.last_instruction.on_block_before_start(b)
                    except Exception:
                        print('GOT: {}, line_number: {}'.format(self.last_instruction, self.last_instruction.line_number))
                        raise

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
                    if b and hasattr(b.start_instruction, 'on_block_end'):
                        b.start_instruction.on_block_end(b)
                    return last_lines

        if b and hasattr(b.start_instruction, 'on_block_end'):
            b.start_instruction.on_block_end(b)

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