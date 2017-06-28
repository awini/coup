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


_Base._SHOW_ERRORS_IN_HTML = False
_Base._LOG_ENABLED = False

code = '''# coding: utf-8

class MainWidget:

    def click_ac(self):
        for a in [1, 2, 3]:
            print( a )
        self.ids.mainInput.text = ""

    def click_break(self):
        for a in range(0, 10):
            pass
        self.ids.mainInput.text = self.ids.mainInput.text[:-1]

    def click_delit(self):
        z = [" / ", " / ", " / "]
        self.ids.mainInput.text += z[1] # " / "

    def click_multiply(self):
        self.ttt = 'hello'
        self.ids.mainInput.text += " * "
        print(self.ttt)

    def click_plus(self):
        self.ids.mainInput.text += " + "

    def click_skobki(self):
        self.ids.mainInput.text = "(" + self.ids.mainInput.text + ")"

    def click_count(self):
        text = self.ids.mainInput.text
        text2 = eval(text)
        text3 = '{:.2f}'.format( text2 )
        self.ids.mainInput.text = text3.replace(',', '.')

    def click_1(self):
        self.ids.mainInput.text += "1"

mw = MainWidget()
mw.click_ac()
mw.click_1()
mw.click_plus()
mw.click_1()
print(mw.ids.mainInput.text)
'''

need_result = '''// coding: utf-8
class MainWidget
{
    click_ac()
    {
        for (var i=0,lst=[1,  2,  3],a=lst[i];i<lst.length;i++,a=lst[i])
        {
            console.log(a)
        }
        this.ids.mainInput.text = ""
    }
    click_break()
    {
        for (var i=0,lst=[...Array(10).keys()].slice(0),a=lst[i];i<lst.length;i++,a=lst[i])
        {
        }
        this.ids.mainInput.text = this.ids.mainInput.text.slice(-1)
    }
    click_delit()
    {
        var z = [" / ",  " / ",  " / "]
        this.ids.mainInput.text += z[1] // " / "
    }
    click_multiply()
    {
        this.ttt = 'hello'
        this.ids.mainInput.text += " * "
        console.log(this.ttt)
    }
    click_plus()
    {
        this.ids.mainInput.text += " + "
    }
    click_skobki()
    {
        this.ids.mainInput.text = "(" + this.ids.mainInput.text + ")"
    }
    click_count()
    {
        var text = this.ids.mainInput.text
        var text2 = eval(text)
        var text3 = '{:.2f}' + text2
        this.ids.mainInput.text = text3.replace(',', '.')
    }
    click_1()
    {
        this.ids.mainInput.text += "1"
    }
}
var mw = new MainWidget()
mw.click_ac()
mw.click_1()
mw.click_plus()
mw.click_1()
console.log(mw.ids.mainInput.text)'''


def make_lines(text):
    return [line.rstrip() for line in text.split('\n')]


class TestOne(TestCase):

    maxDiff = None

    def test_1(self):
        self.do_lang('Javascript', 'node', 'js')

    def test_2(self):
        self.do_lang('Php', 'php', 'php')

    def do_lang(self, lang, app, lang_ext):
        Py2Js = think(translater=Common)
        Py2Js = think('''

            === Python ===                  === {lang} ===

    mw.ids.mainInput.text     >>>     mw.ids.mainInput.text     >>>     ThisIdsMainInputText

        '''.format(lang=lang), Py2Js, lang=lang)

        Py2Js.Class.init_dict = {'arg_to_instance': {'ids.mainInput.text':'ids.mainInput.text'} }

        out = Py2Js.translate(code, remove_space_lines=True)

        self.assertEqual(make_lines(need_result), make_lines(out))

        outputs = []
        for prog, ext, text in (
                ('python', 'py', code),
                (app, lang_ext, need_result)
        ):
            text = text.replace('ids.mainInput.text', 'ids_mainInput_text')

            import os
            if not os.path.exists('build/tmp/'):
                os.makedirs('build/tmp/')

            filename = 'build/tmp/coup_tst.' + ext # FIXME !!!!
            with open(filename, 'w') as f:
                f.write(text)

            from subprocess import check_output
            outputs.append( make_lines(check_output(prog + ' ' + filename, shell=True)) )

            os.remove(filename)

        self.assertEqual(outputs[0], outputs[1])



if __name__=='__main__':
    unittest_main()
