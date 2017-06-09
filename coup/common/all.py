# coding: utf-8
from ..objecter_core._SmartTemplate import template
from ..objecter_core._Base import _Base


Nonnne = template(
    IN='None',
)

If = template(
    IN='if <EXP>:',
    INDEX=_Base.FULL_LINE_PARENTER,
    locals=lambda self:self.parent.get_locals()
)
