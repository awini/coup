# coding: utf-8
import sys
from os.path import join, dirname, abspath
from unittest import TestCase, main as unittest_main

from coup.common.url import think
from coup.objecter_core._Base import _Base


_Base._SHOW_ERRORS_IN_HTML = False
_Base._LOG_ENABLED = False


def make_lines(text):
    if sys.version_info[0] >= 3:
        text = text.decode('cp1251' if sys.platform.startswith('win') else 'utf-8')
    return [line.rstrip() for line in text.split('\n')]


class Test1(TestCase):

    def test_1_if_or_ravno_ravno(self):

        Py2Js = think('''
        @:extends:Common
        @langs

        <EXP> == <EXP>      >>>     <EXP> == <EXP>      >>>     <EXP> == <EXP>      >>>     RavnoRavno
        <EXP> or <EXP>      >>>     <EXP> || <EXP>      >>>     <EXP> || <EXP>      >>>     Or

        ''', lang='Javascript')

        out = Py2Js.translate('''
x = 2
if x == 1 or x == 2:
    print('Okkk!!!')

        ''', remove_space_lines=True)

        self.assertEqual('''var x = 2
if (x == 1 || x == 2)
{
    console.log('Okkk!!!')
}'''.split('\n'), out.split('\n'))

class Test2(TestCase):

    def test_2_var(self):

        Py2Js = think('''
        @:extends:Common
        @langs

    def <EXP:+NAME>():       >>>     function <EXP:+NAME>() {     >>>         >>>     Func  | locals = {}

        ''', lang='Javascript')

        out = Py2Js.translate('''

def func():
    x = 1
    x = 2
    print(x)

        ''', remove_space_lines=True)

        self.assertEqual('''function func()
{
    var x = 1
    x = 2
    console.log(x)
}'''.split('\n'), out.split('\n'))


class Test3(TestCase):

    def test_3_var(self):

        Py2Js = think('''
        @:extends:Common
        @langs

    def <EXP:+NAME>():       >>>     function <EXP:+NAME>() {     >>>         >>>     Func  | locals = {}

        ''', lang='Javascript')

        out = Py2Js.translate('''

def func():
    x = 1
    x = 2
    print(x)

def func2():
    x = 3

        ''', remove_space_lines=True)

        self.assertEqual('''function func()
{
    var x = 1
    x = 2
    console.log(x)
}
function func2()
{
    var x = 3
}'''.split('\n'), out.split('\n'))


class Test4(TestCase):

    def test_4_utf8(self):
        Py2Js = think('''@langs''', lang='Javascript')
        out = Py2Js.translate('''print("Привет!")''', remove_space_lines=True)
        #print(out.decode('utf-8').encode('cp866'))
        self.assertEqual('''console.log("Привет!")'''.split('\n'), out.split('\n'))


if __name__=='__main__':
    unittest_main()