# coding: utf-8
from inspect import isclass
from os.path import dirname, abspath, join
import os

from ..objecter_core._SmartTemplate import template
from ..objecter_core._Smart import Translater, accord
from ..objecter_core._Base import _Block, _Base

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
                    #print(n, url.kwargs)
                    _needed_kwargs.append('{} | {}.{}'.format(url.IN, name, n))
                    continue

            if isclass(url.OUT):
                #print('-----> give _translater')
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

def _join_addon_lines(lines):
    i = 0
    while i < len(lines)-1:
        line = lines[i]
        next_line = lines[i+1]
        if '|||' in next_line:
            splitter = ':::' if ':::' in line else '>>>'
            lst = line.split(splitter)
            for j, a in enumerate(next_line.split('|||')):
                lst[j] = lst[j].strip() + a.strip()
            lines[i:i+2] = [splitter.join(lst)]
        else:
            i += 1
    #print(lines)
    return lines

def _find_addon_lines(lines):
    k = -1
    add_lines = []
    for i, line in enumerate(lines):
        if '|||' in line:
            if k < 0:
                k = i
            add_lines.append(line)
        elif k > 0:
            break
    return k, add_lines

def _add_lines_to_line(lines, k, addon_lines):
    lines = lines[:k] + lines[k+len(addon_lines):]

    lst = [ a.strip() for a in lines[k-1].split('>>>') ]
    for line in addon_lines:
        a_lst = [ a.strip() for a in line.split('|||') ]
        for i in range(len(lst)):
            lst[i] += a_lst[i]

    lines[k-1] = '>>>'.join(lst)

    return lines

def think(text='@langs', translater=None, lang=None, BLOCK_START='{', BLOCK_END='}'): # FIXME

    lines = text.split('\n')

    if lines[0].startswith('@'):
        stripped_0 = lines[0].strip()
        pathes = [ abspath(os.getcwd()) ]
        if HERE not in pathes:
            pathes.append(HERE)
        for p in pathes:
            filename = join(p, stripped_0.replace('@','')+'.abc')
            if os.path.exists(filename):
                with open(filename) as f:
                    lines[:1] = f.read().split('\n')

    lines = _join_addon_lines(lines)
    # k, addon_lines = _find_addon_lines(lines)
    # if k >= 0:
    #     lines = _add_lines_to_line(lines, k, addon_lines)

    if translater == None:
        translater = Translater

    if translater:
        if issubclass(translater, Translater):

            class NewTranslater(translater):
                pass

            langs = None
            lang_pos = 1
            was_langs_line = False

            templates = {}

            #add_count = 0
            for pos, line in enumerate(lines):
                # if add_count > 0:
                #     add_count -= 1
                #     continue

                if not langs and line.strip().startswith('==='):
                    lst = line.split('===')
                    langs = [ a.strip().lower() for a in lst if len(a.strip()) > 0 ]
                    if lang:
                        lang = lang.lower()
                        lang_pos = langs.index(lang)

                        # if lang != 'javascript':
                        #     raise Exception('{} --> {} from: {}'.format(lang, lang_pos, langs))

                    lang = langs[lang_pos]
                    was_langs_line = True
                    continue

                if was_langs_line:
                    if ':::' in line:
                        lst = line.split(':::')

                        # add_count = 0
                        # add_pos = pos + 1
                        # while add_pos < len(lines):
                        #     print('.')
                        #     print(lines[add_pos])
                        #     if '|||' not in lines[add_pos]:
                        #         break
                        #     print('!!!!!!! ||| {}'.format(lines[add_pos]))
                        #     for j, part in enumerate(lines[add_pos].split('|||')):
                        #         lst[j] = lst[j].strip() + part.strip()
                        #     add_count += 1
                        #     add_pos += 1

                        stripped_0 = lst[0].strip()

                        if '<EXP:TEMPLATE:' in line:
                            template_name = lst[0].split('<EXP:TEMPLATE:')[1].split('>')[0]
                            templates[template_name] = lst[lang_pos].strip()
                        else:
                            param_line = lst[lang_pos].strip()
                            if stripped_0.startswith('.') and param_line.startswith('.'):
                                src = stripped_0[1:]
                                dst = param_line[1:].replace(stripped_0, '<EXP>')
                                if '|' in dst:
                                    dst = [ a.strip() for a in dst.split('|')]
                                    _dst = []
                                    for i, d in enumerate(dst):
                                        dl = d.split('=.')
                                        if len(dl) > 1:
                                            fin_d = dl[-1]
                                            fin_val = fin_d.split('=')[1]
                                            dl = [ (d + '=' + fin_val) for d in dl[:-1] ] + [fin_d]
                                            #dl[0] = dl[0][1:]
                                        else:
                                            if dl[0].startswith('.'):
                                                dl[0] = dl[0][1:]
                                            #dl = [ d[1:] if d.startswith('.') else ('.'+d) for d in dl ]
                                        _dst += dl
                                    dst = tuple(_dst)

                                print('\n\n\t{} ---> {}\n\n'.format(src, dst))

                                _Base._ARGS_RENAMER[src] = dst
                            else:
                                if '=' in param_line:
                                    lang_param_name, lang_param_value = [ a.strip() for a in param_line.split('=') ]
                                    _Block.set_main_tune(lang_param_name, lang_param_value)
                        continue
                    else:
                        was_langs_line = False


                if '>>>' in line:

                    _inner = None

                    for template_name in templates:
                        templ = '<EXP:' + template_name + ':'
                        templ_out = templates[template_name]

                        if templ in line:
                            kwargs = {}

                            while True:
                                start = line.find(templ)
                                if start < 0:
                                    break
                                end = line.find('>', start + 1)

                                next_exp = line.find('<EXP:', start+1)
                                if next_exp >= 0:
                                    next_exp_fin = line.find('>', next_exp+1)
                                    while 0 <= end <= next_exp_fin:
                                        end = line.find('>', end + 1)

                                _templ_out = templ_out
                                args = line[start+len(templ):end].split(',')
                                print('ARGS:', args)

                                for i in range(len(args)):
                                    arg = args[i]
                                    if arg == 'EXP':
                                        arg = '<EXP[0]>'
                                    if '<ARG_{}>'.format(i) in _templ_out:
                                        _templ_out = _templ_out.replace('<ARG_{}>'.format(i), arg)
                                    if '=' in arg:
                                        lst = arg.split('=')
                                        lst = [lst[0], '='.join(lst[1:])]
                                        if lst[0] == 'INNER':
                                            _inner = lst[1]
                                        else:
                                            kwargs[lst[0]] = lst[1]

                                line = line[:start] + _templ_out + line[end+1:]

                            kwargs_line = ' '.join((name + '=' + val) for name, val in kwargs.items())
                            if len(kwargs_line) > 0:
                                kwargs_line = ' ' + kwargs_line
                            line = line.replace('<KWARGS>', kwargs_line + ' <EXP:kwargs>')

                            print('LINE: {}'.format(line))

                            #line = line.replace(templ, templates[template_name])
                            break

                    if not langs:
                        raise Exception('Need have "=== Lang ====" instructions at start of text.')

                    line, kwargs = to_exps(line)
                    lst = line.split('>>>')
                    src, dst = [ a.strip() for a in [lst[0], lst[lang_pos]] ]

                    if len(lst) <= len(langs):
                        raise Exception('Need have ">>> name" instruction at end of line: \n\t{}'.format(line.strip()))

                    lst = lst[-1].split('#')[0].split('|')
                    name = lst[0].strip()
                    kwargs_text = lst[1].strip() if len(lst) > 1 else ''
                    lst = kwargs_text.split(',')
                    for s in lst:
                        tt = s.split('=')
                        if len(tt) > 1:
                            kwargs[tt[0].strip()] = eval(tt[1].strip())

                    if len(BLOCK_START) > 0:
                        if dst.endswith(BLOCK_START):
                            dst = dst[:-len(BLOCK_START)]
                    if len(BLOCK_END) > 0:
                        if dst.startswith(BLOCK_END):
                            dst = dst[len(BLOCK_END):]
                    #print(':::: ' + src + ' >>> ' + dst)
                    #urls.append(url(src, OUT=dst))

                    dst_lst = dst.split('|')
                    if len(dst_lst) > 1:
                        dst = dst_lst[0].strip()
                        for a in dst_lst[1].split(','):
                            #print('\t..{}'.format(a))
                            lst = a.split('=')
                            #print('\t__{}'.format(lst))
                            if len(lst) == 2:
                                #print('**{} = {}'.format(lst[0].strip(), eval(lst[1].strip())))
                                kwargs[lst[0].strip()] = eval(lst[1].strip())

                    if '<EXP:INNER>' in dst:
                        if _inner:
                            dst = dst.replace('<EXP:INNER>', _inner)
                            print('------', dst)
                        else:
                            dst, kwargs['BLOCK_END'] = dst.split('<EXP:INNER>')

                    setattr(NewTranslater, name, accord(IN=src, OUT=dst, **kwargs))

            class NewTranslater(NewTranslater):
                pass

            return NewTranslater

    # FIXME it s for old idea...

    urls = []
    for line in lines:
        if '>>>' in line:
            line, kwargs = (line)
            src, dst = [ a.strip() for a in line.split('>>>') ]
            if len(BLOCK_START) > 0:
                if dst.endswith(BLOCK_START):
                    dst = dst[:-len(BLOCK_START)]
            if len(BLOCK_END) > 0:
                if dst.startswith(BLOCK_END):
                    dst = dst[len(BLOCK_END):]
            #print(':::: ' + src + ' >>> ' + dst)
            urls.append(url(src, OUT=dst, **kwargs))

    if translater:
        if issubclass(translater, Urler):
            translater = translater.connect_handlers(urls)
            return translater
        else:
            raise Exception('Why you are trying add this translater?\n\t{}'.format(translater.__class__.__name__))

    return urls


def to_exps(line):
    kwargs = {}

    while line.count('`') >= 2:
        start = line.find('`')
        stop = line.find('`', start+1)
        lst = line[start+1:stop].lower().split('|')
        maker_text = lst[1] if len(lst) > 1 else None
        exp_text = lst[0]
        exp_lst = exp_text.replace(':',' ').split(' ')
        tip = []
        if 'name' in exp_lst:
            tip.append('NAME')
        if 'type' in exp_lst:
            tip.append('^type')
        if 'text' in exp_lst:
            tip.append('TEXT')
        if '+attribute' in exp_lst:
            tip.append('^arg_to_instance')
            if maker_text != None:
                kwargs['arg_maker'] = lambda self,name,tip: maker_text.replace('{name}', str(name)).replace('{tip}', str(tip))
        if 'index=' in exp_text:
            _index = int(exp_text.split('index=')[1].split(':')[0])
            kwargs['INDEX'] = _index

        tip = ','.join(tip)
        if len(tip) > 0:
            tip = ':' + tip
        line = line[:start] + '<EXP' + tip + '>' + line[stop+1:]
    return line, kwargs

def kwargs_to_object(obj, kwargs):
    for name, val in kwargs.items():
        setattr(obj, name, val)

def thinking(text):
    lines = text.split('\n')
    class Thinking(Urler):
        pass
    for line in lines:
        if '>>>' in line:
            line, kwargs = to_exps(line)
            src, name = [ a.strip() for a in line.split('>>>') ]
            #print('??? ' + src + ' >>> ' + name)
            setattr(Thinking, name, template(IN=src, **kwargs))
    return Thinking