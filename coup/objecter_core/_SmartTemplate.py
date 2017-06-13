# coding: utf-8
from copy import copy

from ._Smart import accord
from ._Base import _Base


class template:

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def make(self, **kwargs):
        d = copy(self._kwargs)
        d.update(kwargs)
        return accord(**d)

    def get_in(self):
        return self._kwargs['IN']


def urls(*args):
    pass


if __name__=='__main__':

    If = template(
        IN='if <EXP>:',
        INDEX=_Base.FULL_LINE_PARENTER,
        locals=lambda self: self.parent.get_locals()
    )

    urls(
        ('None', template()),
        ('if <EXP>:', If),
    )
