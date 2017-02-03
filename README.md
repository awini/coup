# ~=~ COUP ~=~
## -(= Translate engine =)-

It is very interesting to translate your programs to other languages.

```python
For = _smart(
    IN_FORMAT='for <EXP:NAME> in <EXP>:',
    OUT_FORMAT='for <EXP:NAME> in <EXP>',
)

Lst = _smart(
    IN_FORMAT='[<EXP:LIST>]',
    OUT_FORMAT='[<EXP:LIST>]',
)

If = _smart(
    IN_FORMAT='if <EXP>:',
    OUT_FORMAT='if <EXP>'
)

Else = _smart(
    IN_FORMAT='else:',
    OUT_FORMAT='else'
)

ElIf = _smart(
    IN_FORMAT='elif <EXP>:',
    OUT_FORMAT='else if <EXP>'
)

Range = _smart(
    IN_FORMAT='range(<EXP>, <EXP>)',
    OUT_FORMAT='<EXP>...<EXP>'
)

```
