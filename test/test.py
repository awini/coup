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


Py2Js = thinking('''

            === Python ===

    '<EXP:TEXT>'                        >>>     String

    class `NewName`(`ParentName`):      >>>     Class

        def `new_name`(self):           >>>     Def

            print(`'string'`)           >>>     Print

''')


Py2Js = think('''

            === Python ===                            === Javascript ===

    '<EXP:TEXT>'                        >>>     '<EXP:TEXT>'

    if <EXP>:                           >_>     if <EXP> {
        sorted(<EXP>)                   >_>         <EXP>.sorted()
    elif <EXP>:                         >_>     else if {
        pass                            >_>
    else:                               >_>     } else {
        `x_name` = `17`                 >_>         var `x_name` = `17`
                                                }

    for `a_name` in <EXP>:              >_>     for `a_name` in <EXP> {
        pass
                                                }

    class `NewName`(`ParentName`):      >>>     class `NewName` // `ParentName`
                                                {
        def `new_name`(self):           >>>         `new_name`() {
            print(`'string'`)           >>>             console.log(`'string'`)
                                                    }
                                                }
    ''', translater=Py2Js)

Py2JsNew = think(translater=Translater)

class Other(Translater):

    String = accord(
        IN="'<EXP:TEXT>'")

    Print = accord(
        IN='print(<EXP>)')

class TestOne(TestCase):

    def test_1(self):
        self.assertTrue(Py2Js.String.is_instruction("'Hello!'"))
        self.assertTrue(Py2Js.Print.is_instruction("print('Hello!')"))
        Py2Js.String("'Hello!'")
        Py2Js.String("'Hello!'")

    def test_2(self):
        Other.translate('''
print('Hello!')
        ''')

    def test_3(self):
        out = Py2Js.translate('''
print('Hello!')
        ''', remove_space_lines=True)
        self.assertEqual(out, "console.log('Hello!')")

    def test_4(self):
        out = Py2JsNew.translate('''
print('Hello!')
        ''', remove_space_lines=True)
        self.assertEqual(out, "console.log('Hello!')")



if __name__=='__main__':
    unittest_main()

