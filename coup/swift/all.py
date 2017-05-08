# coding: utf-8
from ..objecter_core._common_classes import ( _Class, _NumberInt, _Str, _Substr,
                                              _Format, _ExpList, _DefBase, _NumberFloat )
#from ..objecter_core._smart_parsers import _ExpList
from ..objecter_core._Smart import _smart
from ..objecter_core._Base import _Base

Nonnne = _smart(
    IN_FORMAT='None',
    OUT_FORMAT='nil',
)

If = _smart(
    IN_FORMAT='if <EXP>:',
    OUT_FORMAT='if <EXP>',
    INDEX=_Base.FULL_LINE_PARENTER
)

Else = _smart(
    IN_FORMAT='else:',
    OUT_FORMAT='else',
    INDEX=_Base.FULL_LINE_PARENTER
)

Print = _smart(
    IN_FORMAT='print(<EXP>)',
    OUT_FORMAT='Log.d("DEBUG", ""+<EXP>)',
    INDEX=_Base.FULL_LINE_PARENTER
)

Range = _smart(
    IN_FORMAT='range(<EXP>, <EXP>)',
    OUT_FORMAT=' <EXP>...<EXP>',
    INDEX=_Base.IN_LINE_PARENTER
)

Comment = _smart(
    IN_FORMAT='<EXP>#<EXP:TEXT>',
    OUT_FORMAT='<EXP> // <EXP:TEXT>',
    INDEX=_Base.FULL_LINE_PARENTER
)

CommentFull = _smart(
    IN_FORMAT='#<EXP:TEXT>',
    OUT_FORMAT='// <EXP:TEXT>',
    INDEX=_Base.FULL_LINE_PARENTER
)

Index = _smart(
    IN_FORMAT='<EXP:NAME>[<EXP>]',
    OUT_FORMAT='<EXP:NAME>[<EXP>]',
    INDEX=_Base.IN_LINE_CHILD_LAST+1
)

Eval = _smart(
    IN_FORMAT='eval(<EXP>)',
    OUT_FORMAT='Expression(<EXP>).eval()',
    INDEX=_Base.FULL_LINE_PARENTER
)


class Class(_Class):

    DEF_NAME_TO = 'public class'

    def _create_var(self, name, tip):
        return 'var {name}:{tip}? = nil'.format(name=name, tip=tip)


class NumberInt(_NumberInt):
    TYPE_OUT = 'Int'

class NumberFloat(_NumberFloat):
    TYPE_OUT = 'Float'


class Str(_Str):
    TYPE_OUT = 'String'


class Substr(_Substr):

    def get_substring_text(self, start, end):
        return '.substring({}, {})'.format(start, end)


List = _smart(
    IN_FORMAT='[<EXP>]',
    OUT_FORMAT='[<EXP>]',
    INDEX=_Base.IN_LINE_CHILD_LAST
)


class Dottext(_Base):

    INDEX = _Base.IN_LINE_CHILD_LAST + 1

    @staticmethod
    def is_instruction(line):
        return line.strip() == '.text'

    def get_tree_main(self):
        return '.getText().toString()'


class ExpList(_ExpList):
    pass


class Format(_Format):

    def get_format_text(self):
        return 'java.lang.String.format("' + self.s + '", ' + self.in_instruction.get_tree() + ')'


ForIn = _smart(
    IN_FORMAT='for <EXP:NAME> in <EXP:^var>:',
    OUT_FORMAT='for <EXP:NAME> in <EXP:^var>',
    INDEX=_Base.FULL_LINE_PARENTER
)


class Def(_DefBase):
    DEF_NAME = 'def'
    DEF_NAME_TO = 'public func'
