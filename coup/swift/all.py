# coding: utf-8
from ..objecter_core._common_classes import ( _Class, _NumberInt, _Str, _Substr,
                                              _Format, _ExpList, _DefBase, _NumberFloat )
from ..objecter_core._Smart import accord
from ..objecter_core._Base import _Base


Nonnne = accord(
    IN='None',
    OUT='nil',
)

If = accord(
    IN='if <EXP>:',
    OUT='if <EXP>',
    INDEX=_Base.FULL_LINE_PARENTER
)

Else = accord(
    IN='else:',
    OUT='else',
    INDEX=_Base.FULL_LINE_PARENTER
)

Print = accord(
    IN='print(<EXP>)',
    OUT='Log.d("DEBUG", ""+<EXP>)',
    INDEX=_Base.FULL_LINE_PARENTER
)

Range = accord(
    IN='range(<EXP>, <EXP>)',
    OUT=' <EXP>...<EXP>',
    INDEX=_Base.IN_LINE_PARENTER
)

Comment = accord(
    IN='<EXP>#<EXP:TEXT>',
    OUT='<EXP> // <EXP:TEXT>',
    INDEX=_Base.FULL_LINE_PARENTER
)

CommentFull = accord(
    IN='#<EXP:TEXT>',
    OUT='// <EXP:TEXT>',
    INDEX=_Base.FULL_LINE_PARENTER
)

Index = accord(
    IN='<EXP:NAME>[<EXP>]',
    OUT='<EXP:NAME>[<EXP>]',
    INDEX=_Base.IN_LINE_CHILD_LAST+1
)

Eval = accord(
    IN='eval(<EXP>)',
    OUT='Expression(<EXP>).eval()',
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


List = accord(
    IN='[<EXP>]',
    OUT='[<EXP>]',
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


ForIn = accord(
    IN='for <EXP:NAME> in <EXP:^var>:',
    OUT='for <EXP:NAME> in <EXP:^var>',
    INDEX=_Base.FULL_LINE_PARENTER
)


class Def(_DefBase):
    DEF_NAME = 'def'
    DEF_NAME_TO = 'public func'
