# ~=~ COUP ~=~
## Общая кодовая база на многих языках.

Три простых шага для начала:

1. Создайте файл **langs.abc** и в нем добавьте описание перевода в следующем формате:
```
class `New:Name`:           >>>     class `New:Name`            >>>     class `New:Name`              >>>     Class   | arg_to_instance = {}, my_objects = {}
                                    {                                   {
    def `new:name`(self):   >>>         `new:name`() {          >>>         function `new:name`() {   >>>     Method
        print(`exp`)        >>>             console.log(`exp`)  >>>             print(`exp`)          >>>     Print
                                        }                                   }
                                    }                                   }
```
В начале файла добавьте следующую строку:
```
=== Python ===      === Javascript ===      === Php ===
```
Таким образом вы зададите описание сразу 3-х языков перевода.

2. Создайте файл **translate.py** и добавьте в него следующие строки:
```
Py2Js = think(lang='Javascript')
out = Py2Js.translate(code, remove_space_lines=True)
```
Таким образом вы переведете код из многострочного текста code на языке Python в многосточный текст out на языке Javascript. Естественно только если код состоит из описанных конструкций =)
Если нет, то будет выдан список неизвестных конструкций.
