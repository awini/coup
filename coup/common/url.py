# coding: utf-8
from inspect import isclass
from os.path import dirname, abspath, join
import os

from ..objecter_core._SmartTemplate import template
from ..objecter_core._Smart import Translater, accord

HERE = dirname(abspath(__file__))

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

        class NewTranslaterBase(Translater):
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
                url.OUT._translater = NewTranslaterBase

            _d[url.IN] = o.make(OUT=url.OUT, **url.kwargs)
            setattr(NewTranslaterBase, name, _d[url.IN])

        if len(_needed_kwargs) > 0:
            _error_lst.append('Needed kwargs:\n\t{}'.format('\n\t'.join(_needed_kwargs)))

        if len(_unknown_exps) > 0:
            _error_lst.append('Unknown exps:\n\t{}'.format('\n\t'.join(_unknown_exps)))

        templates = ['{:<16} | {}'.format(_d[name]._name, name) for name in _d if _d[name].__class__ == template]

        if len(templates) > 0:
            _error_lst.append('Need make these templates:\n\t{}'.format('\n\t'.join(templates)))

        if len(_error_lst):
            raise Exception('\n\n'.join(_error_lst))

        class NewTranslater(NewTranslaterBase):
            pass

        return NewTranslater


def think(text='@langs', translater=None, lang=None, BLOCK_START='{', BLOCK_END='}'): # FIXME

    if text.startswith('@'):
        pathes = [ abspath(os.getcwd()) ]
        if HERE not in pathes:
            pathes.append(HERE)
        for p in pathes:
            filename = join(p, text.replace('@','')+'.abc')
            if os.path.exists(filename):
                text = open(filename).read()

    lines = text.split('\n')

    if translater:
        if issubclass(translater, Translater):

            class NewTranslater(translater):
                pass

            langs = None
            lang_pos = 1
            for line in lines:
                if not langs and line.strip().startswith('==='):
                    lst = line.split('===')
                    langs = [ a.strip().lower() for a in lst if len(a.strip()) > 0 ]
                    if lang:
                        lang = lang.lower()
                        lang_pos = langs.index(lang)
                    lang = langs[lang_pos]
                    continue

                if '>>>' in line:
                    if not langs:
                        raise Exception('Need have "=== Lang ====" instructions at start of text.')

                    line = to_exps(line)
                    lst = line.split('>>>')
                    src, dst = [ a.strip() for a in [lst[0], lst[lang_pos]] ]

                    if len(lst) <= len(langs):
                        raise Exception('Need have ">>> name" instruction at end of line: \n\t{}'.format(line.strip()))

                    name = lst[-1].strip()

                    if len(BLOCK_START) > 0:
                        if dst.endswith(BLOCK_START):
                            dst = dst[:-len(BLOCK_START)]
                    if len(BLOCK_END) > 0:
                        if dst.startswith(BLOCK_END):
                            dst = dst[len(BLOCK_END):]
                    #print(':::: ' + src + ' >>> ' + dst)
                    #urls.append(url(src, OUT=dst))
                    setattr(NewTranslater, name, accord(IN=src, OUT=dst))

            class NewTranslater(NewTranslater):
                pass

            return NewTranslater

    urls = []
    for line in lines:
        if '>>>' in line:
            line = to_exps(line)
            src, dst = [ a.strip() for a in line.split('>>>') ]
            if len(BLOCK_START) > 0:
                if dst.endswith(BLOCK_START):
                    dst = dst[:-len(BLOCK_START)]
            if len(BLOCK_END) > 0:
                if dst.startswith(BLOCK_END):
                    dst = dst[len(BLOCK_END):]
            #print(':::: ' + src + ' >>> ' + dst)
            urls.append(url(src, OUT=dst))

    if translater:
        if issubclass(translater, Urler):
            translater = translater.connect_handlers(urls)
            return translater
        else:
            raise Exception('Why you are trying add this translater?\n\t{}'.format(translater.__class__.__name__))

    return urls


def to_exps(line):
    while line.count('`') >= 2:
        start = line.find('`')
        stop = line.find('`', start+1)
        exp_text = line[start+1:stop].lower()
        tip = []
        if 'name' in exp_text:
            tip.append('NAME')
        if 'text' in exp_text:
            tip.append('TEXT')
        tip = ','.join(tip)
        if len(tip) > 0:
            tip = ':' + tip
        line = line[:start] + '<EXP' + tip + '>' + line[stop+1:]
    return line


def thinking(text):
    lines = text.split('\n')
    class Thinking(Urler):
        pass
    for line in lines:
        if '>>>' in line:
            line = to_exps(line)
            src, name = [ a.strip() for a in line.split('>>>') ]
            #print('??? ' + src + ' >>> ' + name)
            setattr(Thinking, name, template(IN=src))
    return Thinking