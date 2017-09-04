import sys
from os.path import abspath, dirname, join

HERE = dirname(abspath(__file__))
SITE_PACKAGES = join(HERE, '..', '..')

sys.path.insert(0, SITE_PACKAGES)

from coup.common.url import think
from coup.common.all import Common

lang = 'Javascript'
with open(join(HERE, 'py_code.py')) as fn:
    source_file = fn.read()

Py2Js = think(translater=Common, lang=lang)
out = Py2Js.translate(source_file, remove_space_lines=True)
for line in out.split('\n'):
    print(line)