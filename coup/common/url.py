# coding: utf-8
from inspect import isclass

from ..objecter_core._SmartTemplate import template
from ..objecter_core._Smart import Translater


class url:

    def __init__(self, IN, OUT, **kwargs):
        self.IN = IN
        self.OUT = OUT
        self.kwargs = kwargs

class Needed:
    pass


class Urler:

    @classmethod
    def connect_handlers(cls, lst):
        _d = {}
        for name in dir(cls):
            o = getattr(cls, name)
            if o.__class__ == template:
                o._name = name
                _d[o.get_in()] = o

        class NewTranslater(Translater):
            pass

        _unknown_exps = []
        _error_lst = []
        _needed_kwargs = []

        for url in lst:
            if url.IN not in _d:
                _unknown_exps.append(url.IN)
                continue
                # raise Exception('Unknown exp: {}'.format(url.IN))
            o = _d[url.IN]
            name = o._name
            for n, val in o._kwargs.items():
                if val == Needed and n not in url.kwargs:
                    print(n, url.kwargs)
                    _needed_kwargs.append('{} | {}.{}'.format(url.IN, name, n))
                    continue

            if isclass(url.OUT):
                print('-----> give _translater')
                url.OUT._translater = NewTranslater

            _d[url.IN] = o.make(OUT=url.OUT, **url.kwargs)
            setattr(NewTranslater, name, _d[url.IN])

        if len(_needed_kwargs) > 0:
            _error_lst.append('Needed kwargs:\n\t{}'.format('\n\t'.join(_needed_kwargs)))

        if len(_unknown_exps) > 0:
            _error_lst.append('Unknown exps:\n\t{}'.format('\n\t'.join(_unknown_exps)))

        templates = ['{:<16} | {}'.format(_d[name]._name, name) for name in _d if _d[name].__class__ == template]

        if len(templates) > 0:
            _error_lst.append('Need make these templates:\n\t{}'.format('\n\t'.join(templates)))

        if len(_error_lst):
            raise Exception('\n\n'.join(_error_lst))

        return NewTranslater
