# coding: utf-8
from ._Base import _Base
from ._Base import _Line
from ._InBase import _InBase
from ._smart_parsers import _ExpType, _ExpName

class EmptyPart:
    def get_tree(self):
        return ''


class _DefSkobkiPart(_InBase):
    IN_LEFT = '('
    IN_RIGHT = ')'

class _ClassSkobkiPart(_DefSkobkiPart):
    IN_LEFT_TO = ':'
    IN_RIGHT_TO = ''


class _DefBase(_Base):
    INDEX = _Base.FULL_LINE_PARENTER

    DEF_NAME = None
    DEF_NAME_TO = None
    _SKOBKI_CLS = _DefSkobkiPart
    RENAMER = {}
    _locals = {}

    def __init__(self, line, parent=None, line_number=0):
        super(_DefBase, self).__init__(line, parent, line_number)

        self._locals = {}

        def on_new_instruction(slf, ins):

            # FIXME
            creating_new_name = ins.is_creating_new_name() if hasattr(ins, 'is_creating_new_name') else None

            if creating_new_name:
                new_name, val = creating_new_name
                self._locals[ new_name ] = val

            # parent_class = self.get_parent_class()
            # print('||| {} --> {} | {}'.format(ins, new_name if new_name else '', parent_class))
            return ins

        self._SKOBKI_CLS.on_new_instruction = on_new_instruction

        lst = line.split(':')[0].split('(')
        self.name = lst[0].split(self.DEF_NAME+' ')[1].strip()
        self.skobki_part = self._SKOBKI_CLS('('+lst[1], parent=self) if len(lst) > 1 else EmptyPart()


    def __str__(self):
        return '{def_name}( {name} )'.format(def_name = self.__class__.__name__, name = self.name)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def is_instruction(cls, line, parent=None, line_number=None):
        if line.strip().startswith(cls.DEF_NAME + ' '):
            return True

    def get_tree_main(self):
        return ( self.DEF_NAME_TO+' ' + self.rename() +
                 self.skobki_part.get_tree() )

    def rename(self):
        return self.RENAMER.get(self.name, self.name)


class _SimpleReplacer(_Base):

    FIND_STRING = None
    TO = None
    line = ''

    def __init__(self, line, parent=None, line_number=0):
        super(_SimpleReplacer, self).__init__(line, parent, line_number)

        self.init_instructs(line)

        self.full_text = True

    def init_instructs(cls, line):
        pass

    @classmethod
    def is_instruction(cls, line, parent=None, line_number=None):
        if type(cls.FIND_STRING) is list:
            for fs in cls.FIND_STRING:
                if fs in line:
                    return True
            return False
        return cls.FIND_STRING in line

    def get_tree_main(self):
        return self.TO


class _LeftReplacerWithInstructs(_SimpleReplacer):

    @classmethod
    def is_instruction(cls, line, parent=None, line_number=None):
        return line.strip().startswith(cls.FIND_STRING)

    def get_full_findstring(self):
        return self.FIND_STRING

    def init_instructs(self, line):
        pass


class _ReLine(_Line):

    def re(self, new_line):
        self.new_line = new_line
        return self

    def get_tree_main(self):
        #print('================?', self.in_glob_adder, self.line, id(self))
        if self.in_glob_adder:
            self.in_glob_adder = False
            return self.new_line
        return self.line


class _LineDelete(_SimpleReplacer):
    TO = ''


def _make_lines_deleters(*lines, **kwargs):
    line_deleters = [0]
    def make_deleter(line):
        line_deleters[ 0 ] += 1
        class NewLineDeleter(_LineDelete):
            FIND_STRING = line
            @classmethod
            def to_str(cls):
                return '{}: {}'.format(cls.__name__, cls.FIND_STRING)
        name = 'NewLineDeleter{}'.format(line_deleters[ 0 ])
        kwargs['globals'][name] = NewLineDeleter
    for line in lines:
        make_deleter(line)


class _ExpVar(_ExpType):
    TEXT = 'VAR'
    VAR_PREFIX = 'var '

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        if 'self.' in line:
            return _Line(line, line_number=line_number, new_name=True, parent=parent)
        return _ReLine(line,line_number=line_number, new_name=True, parent=parent).re(cls.VAR_PREFIX + line)


class _OperatorBase(_Base):

    OPERATOR = None
    OPERATORS = set()

    def __init__(self, line, parent=None, line_number=0):
        super(_OperatorBase, self).__init__(line, parent, line_number)

        parent_name = parent.__class__.__name__
        is_in_def_skobki = 'DefSkobki' in parent_name
        #print('>>>>', parent.__class__.__name__)

        exp_cls = _ExpName if is_in_def_skobki else _ExpVar


        self.instructions = [ _Line.try_instruction(s, line_number, parent = self,
                                no_instructs_react = exp_cls.try_instruction if i == 0 and self.OPERATOR == '=' else None
                                ) for i, s in enumerate(line.split(self.OPERATOR)) ]

    @classmethod
    def is_instruction(cls, line, parent=None, line_number=None):
        #print(cls.OPERATOR, line)
        if cls.OPERATOR in line:
            #print(cls.OPERATOR, line)
            for o in _OperatorBase.OPERATORS:
                if o in cls.OPERATOR:
                    continue
                if o in line:
                    return False
            return True

    def get_tree_main(self):
        #print(self.instructions, self.line)
        return self.join_instructions_trees([ ins.get_tree() for ins in self.instructions ])

    def join_instructions_trees(self, trees):
        return (' {op}'.join(trees)).format(op=self.OPERATOR) if len(trees) > 1 else trees[0]



class _OperatorToMethodAbility:
    INDEX = _Base.IN_LINE_PARENTER
    FIND_ATTR = None
    METHOD_FORMAT = None

    def __init__(self, line, parent=None, line_number=0):
        line = line.strip()
        _OperatorBase.__init__(self, line, parent, line_number)

        first_ins = self.instructions[0]
        self.is_me = hasattr(first_ins, 'find_method') and first_ins.find_method == self.FIND_ATTR
        if self.is_me:
            first_ins.full_text = False

        first_ins_line = first_ins.line.strip()
        if first_ins_line.count('.') == 1 and first_ins_line.startswith('self.'):
            self.on_self(first_ins_line)

    def on_self(self, trees):
        pass

    def join_instructions_trees(self, trees):
        # if trees[0].count('.') == 1 and trees[0].startswith('self.'):
        #     self.on_self(trees)
        if self.is_me:
            return trees[0] + self.METHOD_FORMAT.format(trees[1].strip())
        return _OperatorBase.join_instructions_trees(self, trees)


class _Str(_Base):

    def __init__(self, line, parent=None, line_number=0):
        super(_Str, self).__init__(line, parent, line_number)
        #print('SSSSS', line)
        st = line.strip()
        self.s = st[1:-1]

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        return _Str.tst_line_for_str(line)

    @staticmethod
    def tst_line_for_str(line):
        st = line.strip()
        for k in ("'", '"'):
            if (st.startswith(k) and st.endswith(k)):
                #print('^^^^^^^^^^^', line)
                return True

    def get_tree_main(self):
        return '"' + self.s + '"'


class _Comment(_Base):

    def __init__(self, line, parent=None, line_number=0):
        super(_Comment, self).__init__(line, parent, line_number)
        self.s = line.strip()

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        st = line.strip()
        return st.startswith('#')

    def get_tree_main(self):
        return self.make_comment( self.s[1:] )

    def make_comment(self, s):
        raise NotImplementedError



class _Class(_DefBase):
    DEF_NAME = 'class'
    _SKOBKI_CLS = _ClassSkobkiPart

    def __init__(self, line, parent=None, line_number=0):
        super(_Class, self).__init__(line, parent, line_number)

        self.attrs = {}

    def get_tree_main(self):
        i = -1
        for i, name in enumerate(self.attrs):
            self.in_block.blocks.insert(i,
                _Line(self.otstup_string(4)+ self._create_var(name, self.attrs[name]),
                      self, self.line_number))
        i += 1
        self.in_block.blocks.insert(i, _Line(self.otstup_string(4)+self._get_constructor_text(),
                                             self, self.line_number))
        return super(_Class, self).get_tree_main()

    def _create_var(self, name, tip):
        raise NotImplementedError

    def _get_constructor_text(self):
        raise NotImplementedError


class _NumberInt(_Base):

    def __init__(self, line, parent=None, line_number=0):
        super(_NumberInt, self).__init__(line, parent, line_number)
        self.number = int(line.strip())

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        return line.strip().isdigit()

    def get_tree_main(self):
        return '{}'.format(self.number)

    def __eq__(self, other):
        return isinstance(other, _NumberInt) and other.number == self.number

    def __str__(self):
        return 'NumberInt({})'.format(self.number)

    def __repr__(self):
        return self.__str__()

class _NumberFloat(_Base):

    def __init__(self, line, parent=None, line_number=0):
        super(_NumberFloat, self).__init__(line, parent, line_number)
        self.number = float(line.strip())

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        return line.count('.') == 1 and all([ a.isdigit() for a in line.strip().split('.') ])

    def get_tree_main(self):
        return '{}'.format(self.number)

    def __eq__(self, other):
        return isinstance(other, _NumberFloat) and other.number == self.number

    def __str__(self):
        return '_NumberFloat({})'.format(self.number)

    def __repr__(self):
        return self.__str__()


class _Substr(_Base):

    INDEX = _Base.IN_LINE_CHILD_LAST

    def __init__(self, line, parent=None, line_number=0):
        super(_Substr, self).__init__(line, parent, line_number)

        lst = line.strip().split('[')
        self.left_instruction = _Line.try_instruction(lst[0], line_number=line_number, parent=self)
        get_range = lambda t: [ int(b) if len(b) > 0 and not b.isspace() else (len(t) if i == 1 else 0)
                                for i, b in enumerate(t) ]
        self.ranges = [ get_range(t.split(']')[0].split(':')) for t in lst[1:] ]

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        line = line.strip()
        return '[' in line and line.find('[') > 0 and line.count('[') == line.count(']') and ':' in line

    def get_tree_main(self):
        text = self.left_instruction.get_tree()
        for start, end in self.ranges:
            text += self.get_substring_text(start, end)
        return text

    def get_substring_text(self, start, end):
        raise NotImplementedError
        #return '.substring({}, {})'.format(start, end)


class _ExpList(_Base):

    INDEX = _Base.IN_LINE_CHILD_LAST + 2

    def __init__(self, line, parent=None, line_number=0):
        super(_ExpList, self).__init__(line, parent, line_number)

        lst = line.strip().split(',')
        self.instructions = [ _Line.try_instruction(a, line_number=line_number, parent=self) for a in lst ]

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        return ',' in line

    def get_tree_main(self):
        return ', '.join( ins.get_tree() for ins in self.instructions )



class _Format(_Base):

    REPLACE_POINT_TO = '%.'

    def __init__(self, line, parent=None, line_number=0):
        super(_Format, self).__init__(line, parent, line_number)

        lst = line.split('.format(')
        self.s = lst[0].strip()[1:-1].replace('{', '').replace('}', '').replace(':', '').replace('.', self.REPLACE_POINT_TO)
        self.in_instruction = _Line.try_instruction( lst[1].strip()[:-1], line_number=line_number, parent=self )

    @staticmethod
    def is_instruction(line, parent=None, line_number=None):
        line = line.strip()
        if '.format(' in line and line.endswith(')'):
            st = line.split('.format(')[0].strip()
            return _Str.tst_line_for_str(st)

    def get_tree_main(self):
        return self.get_format_text()
        #return 'java.lang.String.format("' + self.s + '", ' + self.in_instruction.get_tree() + ')'

    def get_format_text(self):
        raise NotImplementedError
