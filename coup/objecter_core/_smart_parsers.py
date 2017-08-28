# coding: utf-8
from ._Base import _Line, _GoodLine, _Block, _GlobalName, _Base

_t_name = lambda t: t.__class__.__name__ if hasattr(t, '__class__') else t.__name__

class _ExpString:
    def __init__(self, names_string, on_new_name=lambda self, name, line, line_number: None):
        self.try_exp_types(names_string)
        self.on_new_name = on_new_name

    def __str__(self):
        return '_ExpString(' + ','.join(str(t) if t==None else _t_name(t) for t in self.types) + ')'

    def __repr__(self):
        return self.__str__()

    def is_me(self, line, parent=None, line_number=None, parent_line=''):
        boo = False
        for t in self.types:
            if isinstance(t, _ExpToArg):
                boo = True
                #print('>>>>>>>>>> _ExpToArg >>>>>>>>>>>>\n\t{}'.format(self.types))
            if t and hasattr(t, 'is_me') and not t.is_me(line, parent=parent, line_number=line_number, parent_line=parent_line):
                return False
        if boo:
            self._ExpToArg = _ExpToArg
            #print('\t=====> !!! {}'.format(t))
            return t
        return True


    def try_exp_types(self, line):
        self.types = [ self.try_exp_type(a.strip()) for a in line.split(',') ]

    def try_exp_type(self, line):
        is_empty = line.strip() == ''
        for t in _ExpType.types:
            t = t.try_me(line)
            if t:
                return t

    def try_instruction(self, line, line_number, parent=None):
        _Line.log('_ExpString.try_instruction [{}]: '.format(line_number+1) + line)

        # if hasattr(self, 'need_debug') and self.need_debug:
        #     print('need_debug ' * 3)
        #
        # if hasattr(self, '_ExpToArg'):
        #     print('_ExpToArg'*5)
        #
        # for t in self.types:
        #     if isinstance(t, _ExpToArg):
        #         print('=================================')

        rets = []
        for t in self.types:
            ret = None
            if t == None:
                info_finder = line.strip() == 'a'
                ret = _ExpType.try_instruction(line, line_number=line_number, parent=parent, info_finder=info_finder)
                if ret and ret.__class__ == _GlobalName: #ret and ret.line.strip() == 'a':
                    if parent.is_method:
                        ret.line = _Block.method_format.format(ret.line)
                    else:
                        ret.line = _Block.var_format.format(ret.line)
            else:
                # if isinstance(t, _ExpToArg):
                #     print('========== _ExpToArg >>>>>>>>>>>>\n\t{}'.format(self.types))
                ret = t.try_instruction(line, line_number=line_number, parent=parent, exp_string=self)
            if ret:
                rets.append(ret)

        _Line.log('\tappended: {}'.format(rets))

        if len(rets):
            _Line.log('\treturn: {}'.format(rets[0]))
            return rets[0]

    def try_out_instruction(self, line, line_number, parent=None):
        rets = []
        for t in self.types:
            if hasattr(t, 'try_out_instruction'):
                ret = t.try_out_instruction(line, line_number=line_number, parent=parent)
                rets.append(ret)
        return rets[0] if len(rets) > 0 else line

class _ExpType:
    TEXT = None
    types = None

    @staticmethod
    def init(_globals):
        _ExpType.types = []
        for name in _globals:
            if not name.startswith('_Exp'):
                continue
            g = _globals[name]
            if g == _ExpType:
                continue
            if issubclass( g, _ExpType):
                _ExpType.types.append(g)

    @classmethod
    def try_me(cls, line):
        return cls if line == cls.TEXT else None

    @classmethod
    def try_instruction(cls, line, line_number, parent, info_finder=None):
        return _Line.try_instruction(line, line_number=line_number, parent=parent, info_finder=info_finder)

class _ExpIgnore(_ExpType):
    TEXT = 'ignore'

    def __init__(self, ign_text):
        self.ign_text = ign_text

    @classmethod
    def try_me(cls, line):
        lst = line.split('=')
        if lst[0] == cls.TEXT and len(lst) == 2:
            return _ExpIgnore(lst[1].strip())

    def try_instruction(self, line, line_number, parent, exp_string=None):

        if line.strip() == self.ign_text:
            #raise Exception("{}: ".format(line_number)+line)
            return _GoodLine(self.ign_text)

        return _ExpType.try_instruction(line, line_number, parent)

class _ExpInsertInstance(_ExpType):
    TEXT = '^instance'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        got = _Line.try_instruction(line, line_number=line_number, parent=parent)

        if hasattr(parent, 'current_locals_name'):
            locals, name = parent.current_locals_name
            locals[name] = got

        return got

class _ExpName(_ExpType):
    TEXT = 'NAME'

    @classmethod
    def try_me(cls, line):
        if line.strip() == cls.TEXT:
            return _ExpName()

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        stripped = line.strip()
        return ' ' not in stripped and '.' not in stripped

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):

        locals = None
        parent.current_locals_name = None

        block = parent.get_parent_block()

        locals = block.get_locals()
        # FIXME !!!!
        # if hasattr(parent, 'locals') and parent.locals != None:
        #     if hasattr(parent.locals, '__call__'):
        #         #print('!!!!!!!!!!!!!!!!!!!')
        #         locals = parent.locals(parent)
        #     else:
        #         locals = parent.locals
        # else:
        #     locals = parent.get_locals()

        if parent and hasattr(parent, 'my_objects') and parent.my_objects != None:
            parent.my_objects[line.strip()] = parent

        if locals != None:
            name = line.split('=')[0].split(':')[0].strip().replace('*', '')  # FIXME
            locals[ name ] = None
            parent.current_locals_name = (locals, name)

            if exp_string:
                exp_string.on_new_name(name, line, line_number)

        else:
            raise Exception('''
    {} have no "locals",
    line: {}
    line_number: {}

            '''.format(parent, line, line_number))

        return _GoodLine(line, line_number=line_number, new_name=True, parent=parent)

class _InstructList(list):

    out_splitter = ', '

    def get_tree(self):
        return self.out_splitter.join(a.get_tree() for a in self)

    @property
    def line_number(self):
        return self[0].line_number

class _ExpTreeWay(_ExpType):
    TEXT = 'TREE_WAY'
    splitter = None

    @classmethod
    def try_me(cls, line):
        stripped = line.lstrip()
        if stripped == cls.TEXT:
            return _ExpTreeWay()
        if stripped.startswith('TREE_WAY='):
            w = _ExpTreeWay()
            val_lst = stripped[len(cls.TEXT)+1:].split('=')
            w.splitter = val_lst[0]
            for s in ("'", '"'):
                if w.splitter.startswith(s) and w.splitter.endswith(s):
                    w.splitter = w.splitter[1:-1]
            return w

    try_instruction = None

    def try_out_instruction(self, line, line_number, parent, exp_string=None):

        lst = _InstructList()
        for name in line.split(','):
            lst.append( _ExpName.try_instruction(name.strip(), line_number, parent, exp_string=exp_string) )

        ret = _TreeWay(line, line_number=line_number, parent=parent)
        ret.splitter = self.splitter
        return ret

class _TreeWay(_Line):
    splitter = None

    def get_tree_main(self):
        lst = []
        if self.in_exp:
            lst.insert(0, self.in_exp.get_tree_main())
        if self.parent:
            parent = self.parent
            while parent.parent:
                if hasattr(parent, 'line'):
                    pass
                elif parent.start_instruction:
                    a = parent.start_instruction.get_tree_main()
                    splitter = self.splitter.strip()
                    if a.startswith(splitter):
                        a = a[len(splitter):]
                    lst.insert(0, a)
                parent = parent.parent
        return self.splitter.join(a for a in lst)

class _ExpList(_ExpType):
    TEXT = 'NAMES_LIST'

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        for name in line.split(','):
            name = name.strip()
            if ' ' in name:
                return False
        return True

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):

        lst = _InstructList()
        for name in line.split(','):
            lst.append( _ExpName.try_instruction(name.strip(), line_number, parent, exp_string=exp_string) )

        return lst

class _ExpSimpleList(_ExpType):
    TEXT = 'LIST'
    splitter = ','
    out_splitter = ', '
    tryer = _Line
    min_count = 0

    @classmethod
    def try_me(cls, line):
        stripped = line.lstrip()
        if stripped == cls.TEXT:
            return _ExpSimpleList()
        if stripped.startswith('LIST='):
            lst = _ExpSimpleList()
            val_lst = stripped[5:].split('=')
            lst.splitter = val_lst[0]
            if len(val_lst) > 1:
                lst.out_splitter = val_lst[1]
            if lst.splitter.startswith("'") and lst.splitter.endswith("'"):
                lst.splitter = lst.splitter[1:-1]
            if lst.out_splitter.startswith("'") and lst.out_splitter.endswith("'"):
                lst.out_splitter = lst.out_splitter[1:-1]
            return lst

    def try_instruction(self, line, line_number, parent, exp_string=None):

        lst = _InstructList()
        lst.out_splitter = self.out_splitter
        for sub in line.split(self.splitter):
            ins = self.tryer.try_instruction(sub.strip(), line_number=line_number, parent=parent)
            lst.append( ins )

        return lst

class _ExpDel(_ExpType):
    TEXT = 'DEL'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        return _Line('', line_number=line_number, parent=parent)

class _ExpText(_ExpType):
    TEXT = 'TEXT'

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        parent_line = parent_line.strip()
        start = parent_line[0]

        if line.count(start) > 0:
            return False

        if parent_line.count(start) > 2:
            return False

        if parent_line.count(start) == 2 and parent_line[-1] != start: # FIXME more good algoritm
            return False

        return True

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        return _GoodLine(line, line_number=line_number, parent=parent)


class _ExpRawText(_ExpType):
    TEXT = 'RAW_TEXT'

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        return len(line.strip()) > 0

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        return _GoodLine(line, line_number=line_number, parent=parent)


class _ExpTextWithoutSpaces(_ExpType):
    TEXT = 'TEXT_WITHOUT_SPACES'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        if ' ' in line.strip():

            #if line.strip() == 'self.users_checked and str(id) != str(self.main_root.api.user_id)':
            raise Exception(line)

            return None
        return _GoodLine(line, line_number=line_number, parent=parent)

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        return ' ' not in line


class _SmartLine(_Line):

    def __init__(self, line, parent=None, line_number=0, new_name=False):
        super(_SmartLine, self).__init__(line, parent, line_number, new_name=new_name)
        self.right_line = None

    def __add__(self, other):
        if self.right_line:
            self.right_line += other
        else:
            self.right_line = other
        return self

    def get_tree_main(self):
        ret = super(_SmartLine, self).get_tree_main()
        if self.right_line:
            ret += self.right_line.get_tree()
        return ret

class _ExpInsertVar(_ExpType):
    TEXT = '^var'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        got = _Line.try_instruction(line, line_number=line_number, parent=parent)

        if not hasattr(got, 'START_NAME') or got.START_NAME not in ('[',):
            return got

        child_blocker = [None]
        block = parent.get_parent_block(child_blocker)

        index = block.get_block_index( child_blocker[0] )
        if index < 0:
            index = 0
        start_instruction = block.start_instruction

        let_generated, generated = block.new_let_generated() #'let _generated_1', '_generated_1'

        r = ( _SmartLine(line=block.otstup_string()+let_generated, line_number=line_number, new_name=True, parent=parent) +
              _SmartLine(line=' = ', line_number=line_number, parent=parent) + got )
        r._INSTRUCTION_LINE_ENDING = start_instruction._INSTRUCTION_LINE_ENDING

        block.blocks.insert(0, r)

        return _GoodLine(line=generated, line_number=line_number, new_name=True, parent=parent)

class _ExpGetSimpleLocal(_ExpType):
    TEXT = 'local'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        stripped = line.strip()
        _locals = parent.get_locals()

        # if hasattr(_locals, '__call__'):
        #     return None
        # while hasattr(_locals, '__call__'):
        #     _locals = _locals(parent)

        if stripped in _locals:
            return _GoodLine(line, line_number=line_number, parent=parent)

        return None

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        try:
            stripped = line.strip()
            _locals = parent.get_locals()

            if hasattr(_locals, '__call__'):
                _locals = _locals(parent)
                _Line.log('_ExpGetSimpleLocal._locals: {}'.format(_locals))
                # return None

            if hasattr(_locals, '__call__'):
                _Line.log('_ExpGetSimpleLocal._locals is callable: {}'.format(_locals))
                return None

            _Line.log('\tstripped( {} ) in _locals = {}'.format(stripped, stripped in _locals))
        except:
            return False

        if stripped in _locals:
            print('!!!!!!!! local:', stripped)

        return stripped in _locals

class _ExpSomeName(_ExpType):
    TEXT = 'some_name'
    TST_STRING = 'qwertyuiopasdfghjklzxcvbnm'
    TST_STRING += TST_STRING.upper() + '1234567890_'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        return _GoodLine(line.strip(), line_number=line_number, parent=parent)

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):

        if line_number == 37: #and line.strip() == 'main_root':
            raise Exception('37: {}\n\tparent: {}'.format(line, parent))

        for a in line:
            if a not in cls.TST_STRING:
                return False
        return True

class _ExpInt(_ExpType):
    TEXT = 'int'

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        stripped = line.strip()
        return stripped.isdigit()

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        return _GoodLine(line, line_number=line_number, parent=parent)


class _ExpGetLocal(_ExpType):
    #TEXT = '^get_local' FIXME
    TEXT = 'attribute'

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        stripped = line.strip()
        for a in ' []:-+/&^%$#@()=':
            if a in stripped:
                return False
        return True

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        #got = _Line.try_instruction(line, line_number=line_number, parent=parent)
        parent_class = parent.get_parent_class()

        if line in parent_class.instance_attrs:
            return _GoodLine(line, line_number=line_number, parent=parent)

        return None

class _ExpInsertLocal(_ExpType):
    TEXT = '^arg_to_instance'

    @classmethod
    def is_me(cls, line, parent=None, line_number=None, parent_line=''):
        stripped = line.strip()
        for a in ' []:-+/&^%$#@()=':
            if a in stripped:
                return False
        return True

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        #got = _Line.try_instruction(line, line_number=line_number, parent=parent)
        parent_class = parent.get_parent_class()

        try:

            class _ArgMakerHandler:
                tip = None

                @staticmethod
                def arg_maker(name, tip):
                    return parent.arg_maker(name, tip)

            parent_class.instance_attrs[ line ] = _ArgMakerHandler
            parent_class.instance_attrs_last = line

        except Exception as e:
            print('error: {}'.format(e))
            import traceback, sys
            traceback.print_exc(file=sys.stdout)

        return _GoodLine(line, line_number=line_number, parent=parent)


class _ExpArgToParent(_ExpType):
    TEXT = 'parent^.'

    def __init__(self, arg_name):
        self.arg_name = arg_name

    @classmethod
    def try_me(cls, line):
        stripped = line.strip()
        if stripped.startswith(cls.TEXT):
            return cls(stripped.split(cls.TEXT)[1])

    def try_instruction(self, line, line_number, parent, exp_string=None):
        parent_object = parent.parent.start_instruction

        try:

            if not hasattr(parent_object, 'instance_attrs') or parent_object.instance_attrs == None:
                parent_object.instance_attrs = {}

            class _ArgMakerHandler:
                tip = None

                @staticmethod
                def arg_maker(name, tip):
                    return line

                def __str__(self):
                    return '_ExpArgToParent.maker[{}]'.format(line)

                def __repr__(self):
                    return self.__str__()

            parent_object.instance_attrs[ self.arg_name ] = _ArgMakerHandler
            parent_object.instance_attrs_last = self.arg_name

        except Exception as e:
            print('error: {}'.format(e))
            import traceback, sys
            traceback.print_exc(file=sys.stdout)

        return _GoodLine(line, line_number=line_number, parent=parent)

class _ExpMyArg(_ExpType):
    TEXT = '.'

    def __init__(self, arg_name):
        lst = arg_name.split('=')
        self.arg_name = lst[0]
        self.default_value = lst[1] if len(lst) > 1 else None

    @classmethod
    def try_me(cls, line):
        stripped = line.strip()
        if stripped.startswith(cls.TEXT):
            return cls(stripped.split(cls.TEXT)[1])

    # @classmethod
    # def is_me(cls, line, parent=None, line_number=None, parent_line=''):
    #     stripped = line.strip()
    #     for a in ' []:-+/&^%$#@()=':
    #         if a in stripped:
    #             return False
    #     return True

    def try_instruction(self, line, line_number, parent, exp_string=None):
        parent_class = parent.get_parent_class()

        try:
            line = parent_class.instance_attrs[ self.arg_name ]
        except Exception as e:
            print('error: {}'.format(e))
            import traceback, sys
            traceback.print_exc(file=sys.stdout)

        return _GoodLine(line, line_number=line_number, parent=parent)

    def try_out_instruction(self, line, line_number, parent, exp_string=None):
        parent_object = parent.parent.start_instruction
        print('--- _ExpMyArg - {} - {}'.format(parent_object, parent))
        w = WaitTreeForArg(line, line_number=line_number, parent=parent)
        w.arg_name = self.arg_name
        w.default_value = self.default_value
        print('\t---> default_value: {}'.format(self.default_value))
        return w

class _ExpToArg(_ExpType):
    TEXT = '+.'

    def __init__(self, arg_name):
        self.arg_name = arg_name

    @classmethod
    def try_me(cls, line):
        stripped = line.strip()
        if stripped.startswith(cls.TEXT):
            ret = cls(stripped.split(cls.TEXT)[1])
            return ret

    def try_instruction(self, line, line_number, parent, exp_string=None):
        if True:
            parent_object = parent.parent.start_instruction
            try:

                if not hasattr(parent_object, 'instance_attrs') or parent_object.instance_attrs == None:
                    parent_object.instance_attrs = {}

                _line = line

                class _ArgMakerHandler:
                    tip = None
                    line = _line

                    @staticmethod
                    def arg_maker(name, tip):
                        return ''

                    def __str__(self):
                        return '_ExpToArg.maker[{}]'.format(_line)

                    def __repr__(self):
                        return self.__str__()

                parent_object.instance_attrs[self.arg_name] = _ArgMakerHandler()
                parent_object.instance_attrs_last = self.arg_name

            except Exception as e:
                print('error: {}'.format(e))
                import traceback, sys
                traceback.print_exc(file=sys.stdout)

        return _GoodLine('', line_number=line_number, parent=parent)

class _ExpKwargs(_ExpType):
    TEXT = 'kwargs'

    # def __init__(self):
    #     print('\t~')

    @classmethod
    def try_me(cls, line):
        stripped = line.strip()
        if stripped == cls.TEXT:
            return cls()

    try_instruction = None

    def try_out_instruction(self, line, line_number, parent, exp_string=None):
        parent_object = parent.parent.start_instruction
        return WaitTree(line, line_number=line_number, parent=parent)


class WaitTree(_Line):

    def get_tree_main(self):
        #print('=== KWARGS')

        kwargs = {}

        if True:
            parent_object = self.parent #.parent.start_instruction
            try:
                if hasattr(parent_object, 'instance_attrs') and parent_object.instance_attrs != None:
                    kwargs = parent_object.instance_attrs
            except Exception as e:
                print('error: {}'.format(e))
                import traceback, sys
                traceback.print_exc(file=sys.stdout)

        return ' '.join('{}="{}"'.format(_Base._ARGS_RENAMER.get(a, a),b.line) for a,b in kwargs.items())

class WaitTreeForArg(_Line):

    arg_name = None
    default_value = None

    def __str__(self):
        return 'WaitTreeForArg[{}={}]'.format(self.arg_name, self.get_value())

    def __repr__(self):
        return self.__str__()

    def get_tree_main(self):
        return self.get_value()

    def get_value(self):
        kwargs = {}

        if True:
            parent_object = self.parent  # .parent.start_instruction
            try:
                if hasattr(parent_object, 'instance_attrs') and parent_object.instance_attrs != None:
                    kwargs = parent_object.instance_attrs
            except Exception as e:
                print('error: {}'.format(e))
                import traceback, sys
                traceback.print_exc(file=sys.stdout)

        maker = kwargs.get(self.arg_name)
        ret = maker.line if maker else maker
        if ret == None:
            ret = self.default_value
        return ret


import sys

if sys.version_info[0] < 3:
    class __ExpObject(object, _ExpType):
        pass
else:
    __ExpObject = _ExpType


class _ExpObjectOf(__ExpObject):
    TEXT = 'object_of'

    def __init__(self, instance_class):
        super(_ExpObjectOf, self).__init__()
        self.instance_class = instance_class
        self.__name__ = self.__class__.__name__

    @classmethod
    def try_me(cls, line):
        if line.count('[') == 1 and line.count(']') == 1:
            lst = line.split('[')
            if lst[0] == cls.TEXT:
                text = lst[1].split(']')[0]
                return _ExpObjectOf(text.strip())

    def is_me(self, line, parent=None, line_number=None, parent_line=''):
        stripped = line.strip()
        smarter = None
        instance_class = False
        if hasattr(parent, 'smarter'):
            smarter = parent.smarter
            if smarter and hasattr(smarter, self.instance_class):
                instance_class = getattr(smarter, self.instance_class)
                my_objects = {}
                if hasattr(instance_class, 'my_objects'):
                    my_objects = instance_class.my_objects
                #instance_class = bool(my_objects.get(stripped))
                return stripped in my_objects

        return instance_class

    def try_instruction(self, line, line_number, parent, exp_string=None):
        return _GoodLine(line, line_number=line_number, parent=parent)


class _ExpInstanceOf(__ExpObject):
    TEXT = 'instance_of'

    def __init__(self, instance_class):
        super(_ExpInstanceOf, self).__init__()
        self.instance_class = instance_class
        self.__name__ = self.__class__.__name__

    @classmethod
    def try_me(cls, line):
        if line.count('[') == 1 and line.count(']') == 1:
            lst = line.split('[')
            if lst[0] == cls.TEXT:
                text = lst[1].split(']')[0]
                return _ExpInstanceOf(text.strip())

    #@classmethod
    def is_me(self, line, parent=None, line_number=None, parent_line=''):

        locals = parent.get_locals()

        inst = locals.get(line.strip())
        if inst:

            cls = inst.deleters_in.exps[0].types[0].instance_class

            return cls==self.instance_class

    def try_instruction(self, line, line_number, parent, exp_string=None):
        return _GoodLine(line, line_number=line_number, parent=parent)

class _ExpInsertLocalType(_ExpType):
    TEXT = '^type'

    @classmethod
    def try_instruction(cls, line, line_number, parent, exp_string=None):
        got = _Line.try_instruction(line, line_number=line_number, parent=parent)

        parent_class = parent.get_parent_class()

        parent_class.instance_attrs[ parent_class.instance_attrs_last ].tip = got.TYPE_OUT
        parent_class.instance_attrs_last = None

        return _ExpType.try_instruction(line, line_number, parent)


_ExpType.init(globals())

_EXP_FUNCERS = {
    'lower': lambda s:s.lower()
}

class _ExpParser(list):

    def __init__(self, line):
        deleters = self.split_line(line)
        self.line = line
        super(_ExpParser, self).__init__(deleters)

    @property
    def on_new_name(self):
        return None

    @on_new_name.setter
    def on_new_name(self, val):
        for exp in self.exps:
            exp.on_new_name = val

    def get_exps_positions(self, main_lst):
        poses = []
        if len(main_lst) > 1:
            for m in main_lst[1:]:
                pos = None
                if m.startswith('['):
                    i = m.find(']')
                    pos = int(m[1:i])
                poses.append(pos)
        return poses

    def split_line(self, line):
        need_debug = False #'<EXP:TEXT>.<EXP:TEXT>' in str(line) #'#<EXP:TEXT>' == line
        exps = []
        deleters = []
        main_lst = line.split('<EXP')
        poses = self.get_exps_positions(main_lst)

        if need_debug:
            print('**** MAIN_LST:', main_lst, line)

        for i, ex in enumerate(main_lst):
            lst = ex.split('>')
            if i == 0:
                if len(main_lst[0]) > 0:
                    deleters.append(ex)
            else:
                e_lst = lst[0].split(':')
                es_in = e_lst[1] if len(e_lst) > 1 else e_lst[-1]
                #print('>>>', id(self), type(self), hasattr(self, 'on_new_name'))
                es = _ExpString(es_in)
                if len(e_lst) > 2:
                    #print('>>>', es, e_lst)
                    fu = _EXP_FUNCERS.get(e_lst[2])
                    if fu:
                        es.funcer = fu
                        #print('\t--> {}'.format(fu))
                exps.append( es )
                if len(lst) > 1:
                    deleters.append( '>'.join(lst[1:]) )

        if need_debug:
            print('**** DELETERS:', deleters)

        self.exps = exps
        self.exps_poses = poses

        if need_debug:
            print(exps, '--', line)

        #print('**** DELETERS:', deleters)

        self.exps = exps
        #print(exps, '--', line)

        return deleters
