# ~=~ COUP ~=~
## -(= Translate engine =)-

It is very interesting to translate your programs to other languages.

```python
from coup import Translater, accord, Accord

class ToGO(Translater):

    OUT_START = [ 'package main',
                  'import "fmt"' ]

    Main = accord(
        IN = "if __name__ == '__main__':",
        OUT = 'func main()'
    )

    Print = accord(
        IN =  'print(<EXP>)',
        OUT = 'fmt.Println(<EXP>)',
    )

    class Str(Accord):
        IN = "'<EXP:TEXT>'"
        OUT = '"<EXP:TEXT>"'

```

Python file "main.py":
```
if __name__ == '__main__':
    print('Hello!')
```

And now translate is simple:

```python
new_text = ToGO.translate_file('main.py')
```

And you will get this text:
```
package main
import "fmt"

func main()
{
    fmt.Println("Hello!")

}
```

You can use classess oportunities a lot:

```python
class ToGO(ToGO):

    class Str(Accord):
        IN = "'<EXP:TEXT>'"
        OUT = '"<EXP:TEXT>"'

        def _hello(self):
            print('Hello!')

        def on_init(self, *args, **kwargs):
            print('on_init:', args, kwargs)
            self._hello()
```

Other example:
```python
from coup import Translater, Accord, accord

class SimpleTranslate(Translater):

    For = accord(
        IN_FORMAT='for <EXP:NAME> in <EXP>:',
        OUT_FORMAT='for <EXP:NAME> in <EXP>',
    )

    Lst = accord(
        IN_FORMAT='[<EXP:LIST>]',
        OUT_FORMAT='[<EXP:LIST>]',
    )

    If = accord(
        IN_FORMAT='if <EXP>:',
        OUT_FORMAT='if <EXP>'
    )

    Else = accord(
        IN_FORMAT='else:',
        OUT_FORMAT='else'
    )

    ElIf = accord(
        IN_FORMAT='elif <EXP>:',
        OUT_FORMAT='else if <EXP>'
    )

    Range = accord(
        IN_FORMAT='range(<EXP>, <EXP>)',
        OUT_FORMAT='<EXP>...<EXP>'
    )
```
