# coding: utf-8
import sys
from os.path import join, dirname, abspath
from unittest import TestCase, main as unittest_main

HERE = dirname(abspath(__file__))
PROJ_DIR = abspath(join(HERE, '..'))
sys.path.insert(0, PROJ_DIR)

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
        #print(out) #print(out.decode('utf-8').encode('cp866'))
        self.assertEqual('''console.log("Привет!")'''.split('\n'), out.split('\n'))


class Test5(TestCase):

    def test_5_list_in_list(self):
        Py2Js = think('''
        @:extends:Common
        @langs''', lang='Javascript')
        out = Py2Js.translate('''
a = [1, 2, 3]
b = [1, 2, [3, 4, 5]]
print(a + b)
        ''', remove_space_lines=True)
        self.assertEqual('''var a = [1, 2, 3]
var b = [1, 2, [3, 4, 5]]
console.log(a + b)'''.split('\n'), out.split('\n'))


class Test6(TestCase):

    def test_6_list_in_list_in_list(self):
        Py2Js = think('''
        @:extends:Common
        @langs''', lang='Javascript')
        out = Py2Js.translate('''
a = [1, 2, 3]
b = [[1, "2"], [[3, "4"], 5], ["1, 7", 9]]
print(a + b)
        ''', remove_space_lines=True)
        self.assertEqual('''var a = [1, 2, 3]
var b = [[1, "2"], [[3, "4"], 5], ["1, 7", 9]]
console.log(a + b)'''.split('\n'), out.split('\n'))


class Test7(TestCase):

    def test_7_list_in_list(self):
        Py2Js = think('''
        @:extends:Common
        @langs
    def <EXP:+NAME>():                  >>>     function <EXP:+NAME>() {                    >>>     >>>     func_0
    def <EXP:+NAME>(<EXP:+NAMES_LIST>): >>>     function <EXP:+NAME>(<EXP:+NAMES_LIST>) {   >>>     >>>     func_2
    <EXP>()                             >>>     <EXP>()                                     >>>     >>>     func_start_0
    <EXP>(<EXP:LIST>)                   >>>     <EXP>(<EXP:LIST>)                           >>>     >>>     func_start_2
    ''', lang='Javascript')
        out = Py2Js.translate('''
def func(a, b):
    pass
def func_2():
    pass
func([1, 2], func_2())
        ''', remove_space_lines=True)
        self.assertEqual('''function func(a, b)
{
}
function func_2()
{
}
func([1, 2], func_2())'''.split('\n'), out.split('\n'))

class Test8(TestCase):

    def test_8_fact(self):
        Py2Js = think('''
        @:extends:Common
        @langs
    def <EXP:+NAME>(<EXP:+NAME>):       >>>     function <EXP:+NAME>(<EXP:+NAME>) {         >>>     >>>     func_1          | locals = {}
    def <EXP:+NAME>(<EXP:+NAMES_LIST>): >>>     function <EXP:+NAME>(<EXP:+NAMES_LIST>) {   >>>     >>>     func_2          | locals = {}
    <EXP>(<EXP>)                        >>>     <EXP>(<EXP>)                                >>>     >>>     func_start_1
    <EXP>(<EXP:LIST>)                   >>>     <EXP>(<EXP:LIST>)                           >>>     >>>     func_start_2
    while <EXP>:                        >>>     while (<EXP>) {                             >>>     >>>     While
    <EXP> <= <EXP>                      >>>     <EXP> <= <EXP>                              >>>     >>>     Lower
    <EXP> * <EXP>                       >>>     <EXP> * <EXP>                               >>>     >>>     Mnoz
    return <EXP>                        >>>     return <EXP>                                >>>     >>>     ReturnVal
    print(<EXP>)                        >>>     console.log(<EXP>)                          >>>     >>>     Print
    ''', lang='Javascript')
        in_code = '''
def fact(num):
    rval = 1
    i = 2
    while i <= num:
        rval = rval * i
        i += 1
    return rval
print(fact(7))
        '''
        out = Py2Js.translate(in_code, remove_space_lines=True)
        self.assertEqual('''function fact(num)
{
    var rval = 1
    var i = 2
    while (i <= num)
    {
        rval = rval * i
        i += 1
    }
    return rval
}
console.log(fact(7))'''.split('\n'), out.split('\n'))


if __name__=='__main__':
    unittest_main()