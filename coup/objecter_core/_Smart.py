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
from inspect import isclass

from copy import copy

from ._Base import _Base, _Line, _GoodLine, _Block
from ._smart_parsers import _ExpParser, _ExpToArg


def _smart(IN_FORMAT = None, OUT_FORMAT = None, INDEX = None,
           tst=False, locals=None, instance_attrs=None, TYPE_OUT=None,
           on_init=lambda self:None,
           on_init_end=lambda self:None,
           on_try_instruction=lambda self, i, line: None,
           on_instruction=lambda self,i,ins:ins,
           on_block_start=lambda self, block:None,
           on_block_before_start=lambda self, block:None,
           on_block_end=lambda self, block:None,
           on_get_tree=lambda self, text:text,
           on_good_line=lambda self, line:line,
           on_is_instruction=lambda cls, line, line_number:None,
           on_new_name=lambda self, name, line, line_number:None,
           BLOCK_START=None, BLOCK_END=None, INSTRUCTION_LINE_ENDING='',
           full_line=False, IN=None, OUT=None, SEARCH_IN=None, SEARCH_OUT=None,
           arg_maker=None, my_objects=None, is_comment=False, is_method=None,
           LINES_SPLITTER='\n', USE_OTSTUP=True, to_level_0=False):

    if BLOCK_START == None:
        BLOCK_START = _Base._BLOCK_START
    if BLOCK_END == None:
        BLOCK_END = _Base._BLOCK_END

    if IN != None:
        IN_FORMAT = IN

    if arg_maker and '^arg_to_instance' not in IN_FORMAT:
        raise Exception('It has no "<EXP:^arg_to_instance>" so you should not set "arg_maker"')

    if '^arg_to_instance' in IN_FORMAT and not arg_maker:
        raise Exception('You want "<EXP:^arg_to_instance>" but I need "arg_maker" for it')

    _handler = None
    if isclass(OUT) or OUT.__class__.__name__.endswith('Handler'):
        _handler = OUT
        OUT = _handler.OUT

    if OUT != None:
        OUT_FORMAT = OUT

    if OUT_FORMAT == None:
        OUT_FORMAT = IN_FORMAT

    _SEARCH_IN = _smart(IN = SEARCH_IN, OUT = SEARCH_IN if not SEARCH_OUT else SEARCH_OUT) if SEARCH_IN else None

    def _arg(name, default):
        value = default
        if _handler and hasattr(_handler, name):
            value = getattr(_handler, name)
            #print('GOT: {}.{} = {}'.format(_handler.__name__, name, value))
        return value

    _INDEX = _arg('INDEX', INDEX)
    _TYPE_OUT = _arg('TYPE_OUT', TYPE_OUT)
    _on_block_start = _arg('on_block_start', on_block_start)
    _on_block_before_start = _arg('on_block_before_start', on_block_before_start)
    _on_block_end = _arg('on_block_end', on_block_end)
    _on_init = _arg('on_init', on_init)
    _on_init_end = _arg('on_init_end', on_init_end)
    _on_good_line = _arg('on_good_line', on_good_line)
    _arg_maker = _arg('arg_maker', arg_maker)
    _on_is_instruction = _arg('on_is_instruction', on_is_instruction)
    _on_new_name = _arg('on_new_name', on_new_name)
    _on_instruction = _arg('on_instruction', on_instruction)
    _instance_attrs = _arg('instance_attrs', instance_attrs)
    _my_objects = _arg('my_objects', my_objects)
    _locals = _arg('locals', locals)
    _BLOCK_END = BLOCK_END

    def make_smart(IN_FORMAT):

        _DOC_ADD.append(
'''  {:>3}. {}
       {}
'''.format(len(_DOC_ADD), IN_FORMAT, OUT_FORMAT))

        start_name = IN_FORMAT.split('<')[0].strip()

        class _Exper:

            deleters_in = _ExpParser(IN_FORMAT)
            need_search = [0]

            if _INDEX == None:
                INDEX = (-sum([len(d) for d in deleters_in])*20 + len(deleters_in.exps)) + (
                    -1000 if full_line else 0)
            else:
                INDEX = _INDEX

            _starts_with_deleter = len(deleters_in) > 0 and len(deleters_in[0]) > 0 and IN_FORMAT.startswith(deleters_in[0])

            instance_attrs = None
            arg_maker = _arg_maker

            def on_new_name(self, name, line, line_number):
                _on_new_name(self, name, line, line_number)

            def init_exps(self, line, on_instruction):

                try:

                    self.deleters_in.on_new_name = self.on_new_name

                    need_debug = False or "self.errors_info_label.text = ''" in line #'readonly' in line #self.deleters_in.line == 'self.<EXP:TEXT>.<EXP:TEXT>'

                    out_format = OUT_FORMAT(self) if callable(OUT_FORMAT) else OUT_FORMAT
                    self.deleters_out = _ExpParser(out_format)

                    if need_debug: #and OUT_FORMAT == '':
                        print('--------')
                        print('SELF: {}'.format(self))
                        print('line: {}'.format(line))
                        print('deleters_in:', self.deleters_in, line)
                        print('deleters_in.exps:', self.deleters_in.exps)
                        print('deleters_out:', self.deleters_out, line)
                        print('deleters_out.exps:', self.deleters_out.exps)

                    line = line.strip()

                    _SPLITTER = '~;@:&'

                    new_line = _line_to_slashs(line, self.deleters_in, need_debug=need_debug, splitter=_SPLITTER)
                    if new_line == None:
                        raise Exception('cant be {}: {}'.format(self, line))
                    line = new_line

                    lst = line.split(_SPLITTER)
                    if need_debug:
                        print('line:', line)

                    _tmp_line = self.line

                    def eo_try(ei_result, eo):
                        if eo and hasattr(eo, 'try_out_instruction'):
                            return eo.try_out_instruction(ei_result, line_number=self.line_number, parent=self)
                        return ei_result

                    def pr(ei, e, i):
                        _need_debug = need_debug or hasattr(ei, '_ExpToArg')
                        if _need_debug:
                            if ei:
                                ei.need_debug = True
                            #print('...pr', ei, e, self)
                        ins = on_try_instruction(self, i, e)

                        if (i > len(self.deleters_out.exps)-1) and i not in self.deleters_out.exps_poses:
                            if _need_debug:
                                print('\t--> ""')
                                if ei:
                                     ei_result = ei.try_instruction(e, line_number=self.line_number, parent=self)
                                #     eo_try(ei_result, eo)

                            return _Line('')

                        if type(ins) == str:
                            e = ins
                        elif ins:
                            if _need_debug:
                                print('\t--> ins')
                            return ins

                        ret = ei.try_instruction(e, line_number=self.line_number, parent=self)
                        if ret == None:
                            print('\n\n\t[ ERROR ] cant get ins from: {}\n\tby: {}'.format(e, self))
                            print('\tline: {}, line_number: {}\n'.format(line, self.line_number))
                            raise Exception('...')
                        # ret = eo_try(ret, eo)
                        # if ret == None:
                        #     print('\n\n\t[ ERROR ] cant get ins from (eo): {}\n\tby: {}\n'.format(e, self))
                        #     raise Exception('...')
                        else:
                            if _need_debug:
                                print('\tret: {}'.format(ret))
                        return ret

                    in_exps = self.deleters_in.exps
                    out_exps = self.deleters_out.exps
                    # for i, pos in enumerate(self.deleters_out.exps_poses):
                    #     if pos != None:
                    #         in_exps[i] = self.deleters_in.exps[pos]
                    #
                    # if in_exps != self.deleters_in.exps:
                    #     raise Exception('{} != {}\n{}\n{}'.format(in_exps, self.deleters_in.exps, _tmp_line, self.deleters_out.exps_poses))
                    for ie in in_exps:
                        if hasattr(ie, '_ExpToArg'):
                            need_debug = True
                            #print('(((((((((((((((\n\t{}\n\t{}'.format(lst,in_exps))

                    self.instructions = [ on_instruction(i, pr(ei, e, i)) for i, (e, ei) in enumerate(zip(lst, in_exps)) ]

                    instructions = self.instructions[::]
                    out_ins_append = {}

                    #new_inses = []
                    pos_now = -1
                    for i, pos in enumerate(self.deleters_out.exps_poses):
                        pos_now += 1
                        if pos == None:
                            pass
                            # try:
                            #     new_inses.append(self.instructions[pos_now])
                            # except:
                            #     print('line: {}'.format(line))
                            #     print('deleters_in:', self.deleters_in, line)
                            #     print('deleters_in.exps:', self.deleters_in.exps)
                            #     print('deleters_out:', self.deleters_out, line)
                            #     print('deleters_out.exps:', self.deleters_out.exps)
                                #raise
                        else:
                            #new_inses.append(self.instructions[pos])

                            if i < len(instructions):
                                instructions[i] = self.instructions[pos]
                            else:
                                out_ins_append[i] = self.instructions[pos]
                                instructions.append(self.instructions[pos])

                    # for i in range(len(new_inses), len(self.deleters_out.exps)):
                    #     new_inses.append(self.instructions[i])
                    #
                    # instructions = new_inses

                    if len(self.deleters_out.exps) < len(instructions):
                        # if need_debug:
                        #     print('len(self.deleters_out.exps) < len(instructions) | {} < {}'.format(len(self.deleters_out.exps), len(instructions)))
                        instructions = instructions[:len(self.deleters_out.exps)]

                    in_out_exps, other_out_exps = self.deleters_out.exps[:len(instructions)], self.deleters_out.exps[len(instructions):]
                    for i, eo in enumerate(in_out_exps):
                        if eo and hasattr(eo, 'try_out_instruction'):
                            eo_ret = eo.try_out_instruction('', line_number=self.line_number, parent=self)
                            if eo_ret and eo_ret != '':
                                eo_ret.in_exp = instructions[i]
                                instructions[i] = eo_ret

                    for i, eo in enumerate(other_out_exps):
                        if eo and hasattr(eo, 'try_out_instruction'):
                            eo_ret = eo.try_out_instruction('', line_number=self.line_number, parent=self)
                            if eo_ret and eo_ret != '':
                                instructions.append(eo_ret)
                                #print('\t&&&', instructions, self.instructions)

                    for i, ins in sorted(out_ins_append.items(), key=lambda a: a[0]):
                        if i >= len(instructions):
                            instructions.append(ins)

                    if instructions != self.instructions:
                        self.instructions = instructions
                        # raise Exception('{} != {}\n{}\n{}'.format(instructions, self.instructions, _tmp_line,
                        #                                           self.deleters_out.exps_poses))

                    # if need_debug:
                    #     print('>>>>>>', self.instructions)

                    self.line = _tmp_line

                    if need_debug:
                        print('\tinstructions: {}'.format(instructions))

                except Exception as e:
                    print('ERROR: {}'.format(e))
                    import traceback, sys
                    traceback.print_exc(file=sys.stdout)
                    raise

            @classmethod
            def is_instruction(cls, line, parent=None, line_number=None):
                ret = cls._is_instruction(line, parent=parent, line_number=line_number)
                return ret

            @classmethod
            def _is_instruction(cls, line, parent=None, line_number=None):
                need_debug = False #or "func([1, 2], func_2())" == line and '<EXP>(<EXP:LIST>)' in IN_FORMAT
                need_debug_false = False #or "func([1, 2], func_2())" == line and '<EXP>(<EXP:LIST>)' in IN_FORMAT

                if need_debug:
                    print('self: {} line: {}'.format(IN_FORMAT, line))

                if hasattr(parent, '_exp_equal__list'):
                    del parent._exp_equal__list

                def _print(result, comment):
                    if len(line.strip()):
                        p = '++' if result else '--'
                        #print('\t{} is me: {} ? {} --> {} ({})'.format(p, line, IN_FORMAT, result, comment))
                    return result

                if _Base._LOG_ENABLED:
                    _Line.log('[ {} ].is_instruction [{}]: '.format(IN_FORMAT, line_number + 1) + line)

                if cls.need_search[0]:
                    if _Base._LOG_ENABLED:
                        _Line.log('\tTRUE: need_search: {}'.format(cls.need_search[0]))
                    if need_debug:
                        print('\tTRUE by search')
                    return True

                _on_is_instruction(cls, line, line_number)

                if OUT_FORMAT == NotImplemented:
                    if _Base._LOG_ENABLED:
                        _Line.log('\tFALSE: OUT_FORMAT == NotImplemented')
                    if need_debug_false:
                        print('\tFALSE by OUT_FORMAT == NotImplemented')
                    return _print(False, 'OUT_FORMAT == NotImplemented')

                if len(cls.deleters_in.exps) == 0:
                    #print('-'*100)
                    #print('****** {} ??? {} --> {}'.format(line.strip(), cls._IN_FORMAT.strip(), line.strip() == cls._IN_FORMAT.strip()))
                    #print('-' * 100)
                    ret = line.strip() == cls._IN_FORMAT.strip()
                    if need_debug and ret:
                        print('\tlen(cls.deleters_in.exps) == 0 ===> TRUE')
                    if need_debug_false and not ret:
                        print('\tlen(cls.deleters_in.exps) != 0 ===> FALSE')
                    return ret

                line = line.strip()

                pos = -1
                last_pos = 0
                i = -1
                exp_i = -1

                not_empty_deleters = len([d for d in cls.deleters_in if len(d.strip()) > 0 ])

                last_i = len(cls.deleters_in) - 1

                if len(cls.deleters_in.exps) == 0:
                    if need_debug:
                        print('\tline.strip() == IN_FORMAT.strip()')
                    if need_debug_false:
                        print('\tline.strip() == IN_FORMAT.strip() ==> {}'.format(line.strip() == IN_FORMAT.strip()))
                    return _print(line.strip() == IN_FORMAT.strip(), 'line.strip() == IN_FORMAT.strip()')

                for i, part in enumerate(cls.deleters_in):
                    if len(part) == 0:
                        new_pos = len(line)
                    else:
                        new_pos = line.find(part, pos+1)

                    # if i == last_i and len(part):
                    #     new_pos2 = line.find(part, -1)
                    #     if new_pos2 > new_pos:
                    #         #raise Exception(line +"\n\t{}:{}:{}".format(part, new_pos, new_pos2))
                    #         new_pos = new_pos2
                    #print('>>>>>', line, '>>', cls.deleters_in, '>>', part, ':', pos)

                    if new_pos > last_pos:
                        exp_i += 1
                        if len(cls.deleters_in.exps) > exp_i:
                            exp = cls.deleters_in.exps[exp_i]

                            _is_me = True
                            if hasattr(exp, 'is_me'):

                                is_me_tmp = exp.is_me(line[last_pos:new_pos], parent=parent, line_number=line_number, parent_line=line)
                                if isinstance(is_me_tmp, _ExpToArg):
                                    need_debug = True
                                    #print('..................\n\t {}'.format(cls.deleters_in.exps))

                                if not is_me_tmp:
                                    _Line.log('\tFALSE: not is_me by exp: {},\n\tline: {}'.format(exp, line[last_pos:new_pos]))
                                    _is_me = False

                            if not _is_me:
                                _text = 'not _is_me: ' + line[last_pos:new_pos] + ' ({})'.format(exp)
                                if need_debug_false:
                                    print('not _is_me ==> FALSE')
                                return _print(False, _text)

                    last_pos = new_pos + len(part)

                    pos = new_pos

                    if pos < 0:
                        if need_debug_false:
                            print('\tFALSE: pos < 0')
                        _Line.log('\tFALSE: pos < 0')
                        return _print(False, 'pos < 0')

                    if i == 0 and cls._starts_with_deleter:
                        if pos != 0:
                            if need_debug_false:
                                 print('\tFALSE: pos != 0')
                            _Line.log('\tFALSE: pos != 0')
                            return _print(False, 'i == 0 and cls._starts_with_deleter')

                    pos += len(part) #len(part)-1

                pos -= len(part)
                if True: #i < len(cls.deleters_in.exps) and i < not_empty_deleters: #need_debug or
                    if line[pos:] == cls.deleters_in[-1]:
                        if need_debug:
                            print('\tTRUE 1')
                        _Line.log('\tTRUE: line[pos:] == cls.deleters_in[-1]')
                        return _print(True, 'line[pos:] == cls.deleters_in[-1]')

                    if need_debug_false:
                        print('\tFALSE 2 : {} ?= {}'.format(line[pos:], cls.deleters_in[-1]))

                    if len(cls.deleters_in) == 2 and len(cls.deleters_in.exps) in (1, 2):
                        #print('\tstack: {}'.format(cls.deleters_in.stack))
                        ttt = []
                        last_pos = 0
                        _last_exp = None
                        center = len(cls.deleters_in.stack) / 2.0
                        for i, dl in enumerate(cls.deleters_in.stack):
                            if dl.__class__.__name__ == '_ExpString':
                                _last_exp = dl
                                continue
                            if i <= center:
                                pos = line.find(dl, last_pos)
                                add_text = line[last_pos:pos]
                                last_pos = pos + len(dl)
                            else:
                                if last_pos < center:
                                    pos = line.find(dl, len(line), -1)
                                    add_text = line[last_pos:pos]
                                else:
                                    pos = line.find(dl, last_pos, -1)
                                    add_text = line[pos:last_pos]
                                last_pos = pos - 1
                            if len(add_text):
                                ttt.append(add_text)

                        #print('\t: {}'.format(ttt))
                        if len(ttt) > 0:
                            boos = []
                            for exp in cls.deleters_in.exps:
                                if hasattr(exp, 'is_me'):
                                    boos.append(exp.is_me(ttt[0], parent=parent, line_number=line_number, parent_line=line))
                                else:
                                    boos.append(True)
                            return all(boos)
                        else:
                            return False

                    _Line.log('\tFALSE: need_debug or i < len(cls.deleters_in.exps) and i < not_empty_deleters')
                    return _print(False, 'need_debug or i < len(cls.deleters_in.exps) and i < not_empty_deleters')

                if need_debug:
                    print('\tTRUE: return True')
                _Line.log('\tTRUE: return True')

                return _print(True, 'return True')

            def get_tree_main(self):
                need_debug = False or "self.errors_info_label.text = ''" in self.line
                if need_debug:
                    print('[ get_tree_main ] {} <-- exps: {}'.format(self, self.deleters_in.exps))
                    print('\t{}'.format(self.instructions))

                try:
                    trees = [ ins.get_tree() for ins in self.instructions ] #line = '|'.join()
                except Exception:
                    print('[EXCEPTION] line: {}\ninss: {}'.format(self.line, self.instructions))
                    import traceback, sys
                    traceback.print_exc(file=sys.stdout)
                    raise

                if len(trees) < len(self.deleters_out):
                    plus = lambda tree, d : d + tree
                else:
                    plus = lambda tree, d: tree + d

                cor = lambda ex, p: ex.funcer(p) if hasattr(ex, 'funcer') else p

                line = ''.join( cor(ex, plus(tree, d)) for tree, d, ex in izip_longest(trees, self.deleters_out, self.deleters_out.exps, fillvalue='') )

                if need_debug:
                    print('\t--> {}'.format(line))

                if not _Base._IS_CATCHING:

                    if self.instance_attrs:
                        i = 0
                        for name, handler in self.instance_attrs.items():
                            #print('+++++++')
                            self.in_block.blocks.insert(i, _GoodLine(self.otstup_string(4)+handler.arg_maker(name, handler.tip))) #'var {}:{}? = nil'.format(name, tip)))
                            i += 1
                        if i > 0:
                            self.in_block.blocks.insert(i, _GoodLine(''))

                    #line = '\n'.join([ 'var {}:{}?'.format(name, tip)
                    #                   for name, tip in self.arg_to_instance.items() ]) + line

                return on_get_tree(self, line)

        class Smart(_Exper, _Base):

            #INDEX = _INDEX
            START_NAME = start_name
            locals = None
            TYPE_OUT = _TYPE_OUT

            _IN_FORMAT = IN_FORMAT
            _OUT_FORMAT = OUT_FORMAT

            smarter = None
            name_in_smarter = None
            my_objects = _my_objects

            on_block_start = _on_block_start
            on_block_before_start = _on_block_before_start
            on_block_end = _on_block_end
            _BLOCK_START = BLOCK_START
            _BLOCK_END = BLOCK_END
            _INSTRUCTION_LINE_ENDING = INSTRUCTION_LINE_ENDING
            init_dict = None

            _LINES_SPLITTER = LINES_SPLITTER
            _USE_OTSTUP = USE_OTSTUP
            _to_level_0 = to_level_0

            def __init__(self, line, parent=None, line_number=0):
                self.locals = copy(_locals)
                self.instance_attrs = _instance_attrs

                if self.init_dict:
                    for name, val in self.init_dict.items():
                        setattr(self, name, val)

                super(Smart, self).__init__(line, parent, line_number)
                self.is_comment = is_comment
                self.is_method = is_method

                if _SEARCH_IN:
                    self.need_search[0] += 1
                    if self.need_search[0] == 1:
                        _Block._ignore_start_block = True
                    else:
                        is_search = _SEARCH_IN.is_instruction(line, parent=parent, line_number=line_number)
                        if is_search:
                            self.instructions = [_SEARCH_IN(line, line_number=self.line_number, parent=self)]
                            self.need_search[0] = 0
                            _Block._ignore_start_block = False
                            print('>>>>>>>>> FIN need_search')
                        else:
                            self.instructions = [_GoodLine(_on_good_line(self, line))]

                        self.get_tree = self.instructions[0].get_tree
                        return

                _on_init(self)

                def on_my_instruction(i, ins):
                    return _on_instruction(self, i, ins)

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
                return self.make_my_str(self.smarter, self.name_in_smarter)

            @classmethod
            def make_my_str(cls, smarter, name_in_smarter):
                smarter_name = smarter.__name__ if smarter else ''
                name = (smarter_name + '.' + name_in_smarter) if name_in_smarter else smarter_name
                return cls.__name__ + '(' + str(name) + ': ' + IN_FORMAT + ')'

            @classmethod
            def test_string(cls, line):
                print('{}: {} --> {}'.format(cls.make_my_str(), line, cls.is_instruction(line)))

        return Smart

    if type(IN_FORMAT) not in (list, tuple):
        return make_smart(IN_FORMAT)

    ins_list = [make_smart(a) for a in IN_FORMAT]
    current = [ ins_list[0] ]

    def _install_current(cur):
        current[ 0 ] = cur

    class FooType(type):

        def __getattr__(cls, key):
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
        def is_instruction(cls, line, parent=None, line_number=None):
            for ins in ins_list:
                if ins.is_instruction(line, parent=parent, line_number=line_number):
                    _install_current( ins )
                    return True

    return SmartList

def _line_to_slashs(line, deleters_in, need_debug=False, splitter='|'):
    line = line.strip()
    start_line = line

    left_gran = int(len(deleters_in)/2)+1
    right_gran = int(round(-len(deleters_in)/2))

    left = deleters_in[:left_gran]
    right = deleters_in[-1:right_gran:-1]

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
        new_line = line[:i] + splitter + line[i+len(l):]
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
        line = line[:i] + splitter + line[i + len(l):]


    if line.startswith(splitter):
        line = line[len(splitter):]
    if line.endswith(splitter):
        line = line[:-len(splitter)]

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

import sys

if sys.version_info[0] < 3:
    class SmarterBase(object):
        __metaclass__ = _SmartMeta
    class SmarterPropertyBase(object):
        __metaclass__ = _SmartMeta
else:
    SmarterBase = _SmartMeta(str('SmarterBase'), (), {})
    #class SmarterBase(metaclass=_SmartMeta):
    #    pass
    SmarterPropertyBase = _SmartMeta(str('SmarterPropertyBase'), (), {})

class Smarter(SmarterBase):

    _GLOBALS = None
    OUT_START = []

    @classmethod
    def translate(cls, text, filename=None, remove_space_lines=False, strip=False, logger=None,
                  only_tree=False, remove_double_space_lines=False):
        if cls._GLOBALS:
            for name, value in cls._GLOBALS.items():
                try:
                    value.smarter = cls
                    value.name_in_smarter = name
                except AttributeError:
                    pass
        _getter = _Line.init_instructs(cls._GLOBALS, filename=filename, logger=logger,
                                       only_tree=only_tree)[1]
        out_text = _getter(text)
        if only_tree:
            return out_text
        out_text = '\n'.join(cls.OUT_START) + out_text
        if remove_space_lines:
            out_text = cls._remove_space_lines(out_text)
        if remove_double_space_lines:
            while '\n\n\n' in out_text:
                out_text = out_text.replace('\n\n\n', '\n\n')
        if strip:
            out_text = out_text.strip()
        return out_text

    @classmethod
    def translate_file(cls, filename, to_filename=None, remove_space_lines=False, strip=False,
                       log_file=None, remove_double_space_lines=False, text=None):
        if text == None:
            text = open(filename).read()
        logger = open(log_file, 'w') if log_file else None

        out_text = cls.translate(text, filename=filename, remove_space_lines=remove_space_lines, strip=strip,
                                 logger=logger, remove_double_space_lines=remove_double_space_lines)
        if logger:
            logger.close()

        if to_filename:
            with open(to_filename, 'w') as f:
                f.write(out_text)
        else:
            return out_text

    @classmethod
    def find_by_name(cls, name):
        for _name, value in cls._GLOBALS.items():
            if _name == name:
                return value

    @classmethod
    def _remove_space_lines(cls, text):
        lines = [li for li in text.split('\n') if len(li.strip()) > 0]
        return '\n'.join(lines)

class SmarterProperty(SmarterPropertyBase):

    #__metaclass__ = _SmartMeta

    IN_FORMAT = None
    OUT_FORMAT = None
    INDEX = None
    tst = False
    locals = None
    instance_attrs = None
    TYPE_OUT = None
    on_init = lambda _, self: None
    on_init_end = lambda _, self: None
    on_try_instruction = lambda _, self, i, line: None
    on_instruction = lambda _, self, i, ins: ins
    on_block_start = lambda self, block: None
    on_block_before_start = lambda self, block: None
    on_block_end = lambda self, block: None
    on_get_tree = lambda _, self, text: text
    BLOCK_START = '{'
    BLOCK_END = '}'
    INSTRUCTION_LINE_ENDING = ''
    full_line = False
    IN = None
    OUT = None


Translater = Smarter

accord = _smart

Accord = SmarterProperty

