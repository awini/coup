# coding: utf-8
from ..objecter_core._SmartTemplate import template
from ..objecter_core._Base import _Base

from .url import url, Urler


class BasePython(Urler):

    Nonnne = template(
        IN='None')

    If = template(
        IN='if <EXP>:',
        INDEX=_Base.FULL_LINE_PARENTER,
        locals=lambda self:self.parent.get_locals())

    ExpList = template(
        IN='[<EXP:LIST>]')

    Exp3List = template(
        IN='[<EXP>, <EXP>, <EXP>]')

    # ------

    Else = template(
        IN='else:',
        INDEX=_Base.FULL_LINE_PARENTER)

    Print = template(
        IN='print(<EXP>)',
        INDEX=_Base.FULL_LINE_PARENTER)

    Range = template(
        IN='range(<EXP>, <EXP>)',
        INDEX=_Base.IN_LINE_PARENTER)

    Comment = template(
        IN='<EXP>#<EXP:TEXT>',
        INDEX=_Base.FULL_LINE_PARENTER)

    CommentFull = template(
        IN='#<EXP:TEXT>',
        INDEX=_Base.FULL_LINE_PARENTER)

    Index = template(
        IN='<EXP:NAME>[<EXP>]',
        INDEX=_Base.IN_LINE_CHILD_LAST + 1)

    Eval = template(
        IN='eval(<EXP>)',
        INDEX=_Base.FULL_LINE_PARENTER
    )

    # -----

    List = template(
        IN='[<EXP>]',
        INDEX=_Base.IN_LINE_CHILD_LAST)

    ForIn = template(
        IN='for <EXP:NAME> in <EXP:^var>:',
        INDEX=_Base.FULL_LINE_PARENTER)

    ForIn2 = template(
        IN='for <EXP:NAME>, <EXP:NAME> in <EXP:^var>:',
        INDEX=_Base.FULL_LINE_PARENTER)




