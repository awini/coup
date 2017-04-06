# coding: utf-8
from ._Base import _Line, _GoodLine

class _ExpString:
    def __init__(self, names_string):
        self.try_exp_types(names_string)

    def __str__(self):
        return '_ExpString(' + ','.join(str(t) if t==None else t.__name__ for t in self.types) + ')'

    def __repr__(self):
        return self.__str__()

    def try_exp_types(self, line):
        self.types = [ self.try_exp_type(a.strip()) for a in line.split(',') ]
        #print(self.types)

    def try_exp_type(self, line):
        for t in _ExpType.types:
            if t.try_me(line):
                return t

    def try_instruction(self, line, line_number, parent=None):
        #print(self, line)
        rets = []
        for t in self.types:
            ret = None
            if t == None:
                ret = _ExpType.try_instruction(line, line_number=line_number, parent=parent)
            else:
                ret = t.try_instruction(line, line_number=line_number, parent=parent)
            if ret:
                rets.append(ret)
        if len(rets):
            return rets[0]

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
        return line == cls.TEXT

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        return _Line.try_instruction(line, line_number=line_number, parent=parent)

class _ExpName(_ExpType):
    TEXT = 'NAME'

    @classmethod
    def try_instruction(cls, line, line_number, parent):

        #print('..', parent.locals, line)
        if hasattr(parent, 'locals') and parent.locals != None:
            name = line.split('=')[0].split(':')[0].strip().replace('*','') # FIXME
            #print('[ NAME ] {} --> {}'.format(name, parent))
            parent.locals[ name ] = None

        return _GoodLine(line, line_number=line_number, new_name=True, parent=parent)

class _InstructList(list):

    def get_tree(self):
        return ', '.join(a.get_tree() for a in self)


class _ExpList(_ExpType):
    TEXT = 'NAMES_LIST'

    @classmethod
    def try_instruction(cls, line, line_number, parent):

        lst = _InstructList()
        for name in line.split(','):
            lst.append( _ExpName.try_instruction(name.strip(), line_number, parent) )

        return lst

class _ExpSimpleList(_ExpType):
    TEXT = 'LIST'

    @classmethod
    def try_instruction(cls, line, line_number, parent):

        lst = _InstructList()
        for sub in line.split(','):
            ins = _Line.try_instruction(sub, line_number=line_number, parent=parent)
            lst.append( ins )

        return lst

class _ExpDel(_ExpType):
    TEXT = 'DEL'

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        return _Line('', line_number=line_number, parent=parent)

class _ExpText(_ExpType):
    TEXT = 'TEXT'

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        return _GoodLine(line, line_number=line_number, parent=parent)

class _SmartLine(_Line):

    def __init__(self, line, parent=None, line_number=0, new_name=False):
        super(_SmartLine, self).__init__(line, parent, line_number, new_name=new_name)
        self.right_line = None

    def __add__(self, other):
        #print('&&', self, other)
        if self.right_line:
            self.right_line += other
        else:
            self.right_line = other
        return self

    def get_tree_main(self):
        #print('&& GT', self, self.right_line)
        ret = super(_SmartLine, self).get_tree_main()
        if self.right_line:
            ret += self.right_line.get_tree()
        return ret

class _ExpInsertVar(_ExpType):
    TEXT = '^var'

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        got = _Line.try_instruction(line, line_number=line_number, parent=parent)

        #print('got:', got, got.START_NAME)

        if not hasattr(got, 'START_NAME') or got.START_NAME not in ('[',):
            return got

        child_blocker = [None]
        block = parent.get_parent_block(child_blocker)
        #print(block.children, block.blocks)
        index = block.get_block_index( child_blocker[0] )
        if index < 0:
            index = 0
        #print('!!!', block, child_blocker[0], index)

        r = ( _SmartLine(line=block.otstup_string()+'let _generated_1', line_number=line_number, new_name=True, parent=parent) +
              _SmartLine(line=' = ', line_number=line_number, parent=parent) + got )

        block.blocks.insert(0, r)

        return _GoodLine(line='_generated_1', line_number=line_number, new_name=True, parent=parent)


class _ExpGetLocal(_ExpType):
    TEXT = '^get_local'

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        #got = _Line.try_instruction(line, line_number=line_number, parent=parent)
        parent_class = parent.get_parent_class()
        #print( '-----', parent_class, line )
        if line in parent_class.init_locals:
            return _GoodLine(line, line_number=line_number, parent=parent)

        return None

class _ExpInsertLocal(_ExpType):
    TEXT = '^init_locals'

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        #got = _Line.try_instruction(line, line_number=line_number, parent=parent)
        parent_class = parent.get_parent_class()
        #print( '-----', parent_class, line )
        parent_class.init_locals[ line ] = None
        parent_class.init_locals_last = line

class _ExpInsertLocalType(_ExpType):
    TEXT = '^type'

    @classmethod
    def try_instruction(cls, line, line_number, parent):
        got = _Line.try_instruction(line, line_number=line_number, parent=parent)

        parent_class = parent.get_parent_class()

        #print( '::::::', parent_class, got, line )
        parent_class.init_locals[ parent_class.init_locals_last ] = got.TYPE_OUT
        parent_class.init_locals_last = None

        #parent_class.init_locals[ line ] = None
        return _ExpType.try_instruction(line, line_number, parent)


_ExpType.init(globals())


class _ExpParser(list):

    def __init__(self, line):
        deleters = self.split_line(line)
        self.line = line
        super(_ExpParser, self).__init__(deleters)

    def split_line(self, line):
        need_debug = False #'#<EXP:TEXT>' == line
        exps = []
        deleters = []
        main_lst = line.split('<EXP')

        if need_debug:
            print('**** MAIN_LST:', main_lst, line)

        for i, ex in enumerate(main_lst):
            lst = ex.split('>')
            if i == 0:
                if len(main_lst[0]) > 0: #and False:
                    #print('!!!', main_lst, lst[0])
                    deleters.append(ex)#lst[0])
                    #exps.append( _ExpString('') )
            else:
                es_in = lst[0].split(':')[-1]
                es = _ExpString(es_in)
                #print('>>>', es, es_in)
                exps.append( es )
                if len(lst) > 1:
                    deleters.append( '>'.join(lst[1:]) )

        if need_debug:
            print('**** DELETERS:', deleters)

        self.exps = exps

        if need_debug:
            print(exps, '--', line)

        #print('**** DELETERS:', deleters)

        self.exps = exps
        #print(exps, '--', line)

        return deleters
