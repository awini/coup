# coding: utf-8
import sys
from os.path import join, dirname, abspath
from unittest import TestCase, main as unittest_main

HERE = dirname(abspath(__file__))
PROJ_DIR = abspath(join(HERE, '..'))
sys.path.insert(0, PROJ_DIR)

from coup import think


class Test8(TestCase):

    def test_1_simple(self):
        Py2Js = think('''
        print('Hello World!')   >>>   console.log('Hello World!');
        ''')

        out = Py2Js.translate('''
        print('Hello World!')
        ''')

        self.assertEqual('''console.log('Hello World!');'''.split('\n'), out.split('\n'))


if __name__=='__main__':
    unittest_main()