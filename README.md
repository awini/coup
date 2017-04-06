# ~=~ COUP ~=~
## -(= Translate engine =)-

*It is very interesting to translate your programs to other languages.*

Imagine we have program code on **Python** like (file **"main.py"**):
```
if __name__ == '__main__':
    print('Hello!')
```
Now we want auto translater that can translate it ro **Golang**. In **Golang**
this program code will be like:
```Golang
package main
import "fmt"

func main()
{
    fmt.Println("Hello!")
}
```

OK, this task is created for this tool!
Now let's try to write our new translate engine in simple syntax. It wil be like this:

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
OK
------
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
