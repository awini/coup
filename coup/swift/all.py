# coding: utf-8
from ..objecter_core._common_classes import ( _Class, _NumberInt, _Str, _Substr,
                                              _Format, _ExpList, _DefBase, _NumberFloat )
from ..common.all import BasePython, url


BasePython = BasePython.connect_handlers([
    url('None',                     OUT='nil'),
    url('if <EXP>:',                OUT='if <EXP>'),
    url('[<EXP:LIST>]',             OUT='[<EXP:LIST>]'),
    url('[<EXP>, <EXP>, <EXP>]',    OUT='[<EXP>, <EXP>, <EXP>]'),
    url('else:',                    OUT='else'),
    url('print(<EXP>)',             OUT='Log.d("DEBUG", ""+<EXP>)'),
    url('range(<EXP>, <EXP>)',      OUT='<EXP>...<EXP>'),
    url('<EXP>#<EXP:TEXT>',         OUT='<EXP> // <EXP:TEXT>'),
    url('#<EXP:TEXT>',              OUT='// <EXP:TEXT>'),
    url('<EXP:NAME>[<EXP>]',        OUT='<EXP:NAME>[<EXP>]'),
    url('eval(<EXP>)',              OUT='Expression(<EXP>).eval()'),
    url('[<EXP>]',                  OUT='[<EXP>]'),

    url('for <EXP:NAME> in <EXP:^var>:',                OUT='for <EXP:NAME> in <EXP:^var>'),
    url('for <EXP:NAME>, <EXP:NAME> in <EXP:^var>:',    OUT='for <EXP:NAME>, <EXP:NAME> in <EXP:^var>')

])

class NumberInt(_NumberInt):
    TYPE_OUT = 'Int'

class NumberFloat(_NumberFloat):
    TYPE_OUT = 'Float'


# List = accord(
#     IN='[<EXP>]',
#     OUT='[<EXP>]',
#     INDEX=_Base.IN_LINE_CHILD_LAST
# )
#
# ForIn = accord(
#     IN='for <EXP:NAME> in <EXP:^var>:',
#     OUT='for <EXP:NAME> in <EXP:^var>',
#     INDEX=_Base.FULL_LINE_PARENTER
# )
#
# ForIn2 = accord(
#     IN='for <EXP:NAME>, <EXP:NAME> in <EXP:^var>:',
#     OUT='for <EXP:NAME>, <EXP:NAME> in <EXP:^var>',
#     INDEX=_Base.FULL_LINE_PARENTER
# )



# class Class(_Class):
#
#     DEF_NAME_TO = 'public class'
#
#     def _create_var(self, name, tip):
#         return 'var {name}:{tip}? = nil'.format(name=name, tip=tip)


# class Str(_Str):
#     TYPE_OUT = 'String'


# class Substr(_Substr):
#
#     def get_substring_text(self, start, end):
#         return '.substring({}, {})'.format(start, end)


# class Dottext(_Base):
#
#     INDEX = _Base.IN_LINE_CHILD_LAST + 1
#
#     @staticmethod
#     def is_instruction(line, parent=None, line_number=None):
#         return line.strip() == '.text'
#
#     def get_tree_main(self):
#         return '.getText().toString()'


# class ExpList(_ExpList):
#     pass


# class Format(_Format):
#
#     def get_format_text(self):
#         return 'java.lang.String.format("' + self.s + '", ' + self.in_instruction.get_tree() + ')'


# class Def(_DefBase):
#     DEF_NAME = 'def'
#     DEF_NAME_TO = 'public func'
