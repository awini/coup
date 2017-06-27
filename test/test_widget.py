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

class MainWidget(BoxLayout):

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

class TestOne(TestCase):

    def test_4(self):
        Py2Js = think(translater=Common)
        Py2Js = think('''

            === Python ===                  === Javascript ===

    self.ids.mainInput.text     >_>     this.ids.mainInput.text     >_>     ThisIdsMainInputText

        ''', Py2Js)
        Py2Js.Class.init_dict = {'arg_to_instance': {'ids.mainInput.text':'ids.mainInput.text'} }

        out = Py2Js.translate(code, remove_space_lines=True)
        self.maxDiff = None

        def make_lines(text):
            return [ line.rstrip() for line in text.split('\n') ]

        need_result = '''// coding: utf-8
class MainWidget // BoxLayout
{
    click_ac()
    {
        for (var a in [1,  2,  3])
        {
            console.log(a)
        }
        this.ids.mainInput.text = ""
    }
    click_break()
    {
        for (var a in [...Array(10).keys()].slice(0))
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
}'''
        self.assertEqual(make_lines(need_result), make_lines(out))



if __name__=='__main__':
    unittest_main()
