# coding: utf-8
import sys
from os.path import join, dirname, abspath
from unittest import TestCase, main as unittest_main

HERE = dirname(abspath(__file__))
sys.path.insert(0, abspath(join(HERE, '..')))

from coup.common.url import url, thinking, think
from coup.objecter_core._Base import _Base
from coup import Translater, accord


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
        self.ids.mainInput.text += z[1] #" / "

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
        text2 = '{:.2f}'.format( eval(text) )
        self.ids.mainInput.text = text2.replace(',', '.')

    def click_1(self):
        self.ids.mainInput.text += "1"
'''

class TestOne(TestCase):

    def test_4(self):
        Py2JsNew = think(translater=Translater)
        out = Py2JsNew.translate(code, remove_space_lines=True)
        #self.assertEqual(out, "console.log('Hello!')")
        print(out)



if __name__=='__main__':
    unittest_main()
