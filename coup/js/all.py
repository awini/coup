# coding: utf-8
from ..objecter_core._common_classes import ( _Class, _NumberInt, _Str, _Substr,
                                              _Format, _ExpList, _DefBase, _NumberFloat )
from ..common.all import BasePython, url
from ..common.url import think


BasePython = BasePython.connect_handlers([
    url('None',                     OUT='null'),
    url('if <EXP>:',                OUT='if (<EXP>)'),
    url('[<EXP:LIST>]',             OUT='[<EXP:LIST>]'),
    url('[<EXP>, <EXP>, <EXP>]',    OUT='[<EXP>, <EXP>, <EXP>]'),
    url('else:',                    OUT='else'),
    url('print(<EXP>)',             OUT='console.log(""+<EXP>)'),
    url('range(<EXP>, <EXP>)',      OUT='[...Array(<EXP[1]>).keys()].slice(<EXP[0]>)'),
    url('<EXP>#<EXP:TEXT>',         OUT='<EXP> // <EXP:TEXT>'),
    url('#<EXP:TEXT>',              OUT='// <EXP:TEXT>'),
    url('<EXP:NAME>[<EXP>]',        OUT='<EXP:NAME>[<EXP>]'),
    url('eval(<EXP>)',              OUT='eval(<EXP>)'),
    url('[<EXP>]',                  OUT='[<EXP>]'),

    url('for <EXP:NAME> in <EXP:^var>:',                OUT='for (var <EXP:NAME> in <EXP:^var>)'),
    url('for <EXP:NAME>, <EXP:NAME> in <EXP:^var>:',    OUT='for (var <EXP:NAME>, <EXP:NAME> in <EXP:^var>)')
])

class NumberInt(_NumberInt):
    TYPE_OUT = 'Int'

class NumberFloat(_NumberFloat):
    TYPE_OUT = 'Float'


