# coding: utf-8
import sys
from os.path import join, dirname, abspath
from unittest import TestCase, main as unittest_main

HERE = dirname(abspath(__file__))
sys.path.insert(0, abspath(join(HERE, '..')))

from coup.common.url import url, thinking, think
from coup.objecter_core._Base import _Base
from coup import Translater, accord
from coup.common.all import Common

from examples_code import *


_Base._SHOW_ERRORS_IN_HTML = False
_Base._LOG_ENABLED = False


def make_lines(text):
    if sys.version_info[0] >= 3:
        text = text.decode('cp1251' if sys.platform.startswith('win') else 'utf-8')
    return [line.rstrip() for line in text.split('\n')]


class TestOne(TestCase):

    maxDiff = None

    def test_1(self):
        self.do_lang('Javascript', 'node', 'js')

    def test_2(self):
        self.do_lang('Php', 'php', 'php', '<?php\n{}\n?>', need_result=need_result_php, var_prefix='$', instance_point='->')

    def do_lang(self, lang, app, lang_ext, lang_form='{}', need_result=need_result_js, var_prefix='', instance_point='.'):
        Py2Js = think(translater=Common, lang=lang)
        Py2Js = think('''

            === Python ===                  === {lang} ===

    self.ids.mainInput.text   >>>       {var_prefix}this{instance_point}ids.mainInput.text  >>>     ThisIdsMainInputText
    mw.ids.mainInput.text     >>>       {var_prefix}mw{instance_point}ids.mainInput.text    >>>     MwIdsMainInputText

        '''.format(lang=lang, var_prefix=var_prefix, instance_point=instance_point), Py2Js, lang=lang)

        Py2Js.Class.init_dict = {'arg_to_instance': {'ids.mainInput.text':'ids.mainInput.text'} }

        out = Py2Js.translate(code, remove_space_lines=True)

        #self.assertEqual(make_lines(need_result), make_lines(out))

        outputs = []
        for prog, ext, text, form in (
                ('python', 'py', code, '{}'),
                (app, lang_ext, out, lang_form)
        ):
            text = text.replace('ids.mainInput.text', 'ids_mainInput_text')

            import os
            if not os.path.exists('build/tmp/'):
                os.makedirs('build/tmp/')

            filename = 'build/tmp/coup_tst.' + ext # FIXME !!!!
            print('[ FILE ] {}'.format(filename))
            with open(filename, 'w') as f:
                f.write( form.format(text) )

            from subprocess import Popen, CalledProcessError, PIPE
            from sys import stdout

            com = prog + ' ' + filename
            print('[ COM ] {}'.format(com))

            p = Popen(com, shell=True, stdout=PIPE)
            stdoutdata, stderrdata = p.communicate()

            outputs.append(make_lines( stdoutdata ))

            if p.returncode != 0:
                raise Exception('[ ERROR on COM: {} ]\n\t{}'.format(prog, stdoutdata))

            #os.remove(filename)

        self.assertEqual(outputs[0], outputs[1])



if __name__=='__main__':
    unittest_main()
