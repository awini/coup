# coding: utf-8
from coup.objecter_core._Smart import _smart
from coup.objecter_core._Base import _Block, _Line, _Base, _GoodLine
from coup.swift.all import NumberInt
from unittest import TestCase, main


def upper_to_lower(name):
    b = []
    last_lower = False
    for a in name:
        if a.islower():
            last_lower = True
            b.append(a)
        else:
            if last_lower:
                b.append('_' + a.lower())
            else:
                b.append(a.lower())
            last_lower = False
    return ''.join(b)



class TextTryer(object):

    def __init__(self, **kwargs):
        self.all = kwargs

    def parse(self, text):
        getter = _Line.init_instructs(self.all, only_tree=True)[1]
        self.b = getter(text)
        return self

    def get_tree_text(self):
        return '\n---] '.join(self.b.get_tree().split('\n'))

    @property
    def first_ins(self):
        return self.b.blocks[0]#.blocks[0]

    @property
    def first_ins_params(self):
        first_ins = self.first_ins
        return type(first_ins), first_ins.instructions


class TestAll(TestCase):

    def test_00(self):
        t = TextTryer(
            NumberInt=NumberInt,
            Object=_smart(
                IN_FORMAT='object',
                OUT_FORMAT=''
            ),
            Class=_smart(
                IN_FORMAT='class <EXP:NAME>(<EXP:LIST>):',
                OUT_FORMAT='public class <EXP:NAME>:<EXP:LIST>',
                locals={},
                init_locals={},
            ),
            RavnoText=_smart(
                IN_FORMAT='<EXP:NAME>=<EXP>',
                OUT_FORMAT='<EXP:NAME>=<EXP>',
                INDEX=_Base.FULL_LINE_PARENTER - 1,
            ),
        ).parse('''x = 10
class Hello(object):
        ''')
        self.assertEqual( [_Line('x'), NumberInt('10')], t.b.blocks[0].instructions )
        self.assertEqual( [_Line('Hello'), [_smart(
                IN_FORMAT='object',
                OUT_FORMAT=''
            )('object')]], t.b.blocks[1].instructions)

    def test_0(self):
        RavnoText = _smart(
            IN_FORMAT='<EXP:NAME>=<EXP>',
            OUT_FORMAT='<EXP:NAME>=<EXP>',
            INDEX=_Base.FULL_LINE_PARENTER - 1,
        )

        first_type, instructs = TextTryer(
            NumberInt = NumberInt,
            RavnoText = RavnoText,
        ).parse('x = 10\n').first_ins_params

        self.assertEqual(first_type, RavnoText)
        self.assertEqual([_Line('x '), NumberInt('10')], instructs)


    def test_1(self):
        Def = _smart(
            IN_FORMAT='def <EXP:NAME>(self, <EXP:NAME>):',
            OUT_FORMAT='public func <EXP:NAME>(<EXP:NAME>)',
            INDEX=_Base.FULL_LINE_PARENTER - 1,
        )

        first_type, instructs = TextTryer(
            NumberInt=NumberInt,
            Def=Def,
        ).parse('def hello(self, name):\n').first_ins_params

        self.assertEqual(first_type, Def)
        self.assertEqual([ _Line('hello'), _Line('name')], instructs)

    def test_2(self):
        Def = _smart(
            IN_FORMAT='def <EXP:NAME>(self,<EXP:NAMES_LIST>):',
            OUT_FORMAT='public func <EXP:NAME>(<EXP:NAMES_LIST>)',
            INDEX=_Base.FULL_LINE_PARENTER - 1,
            locals = {'self':None}
        )

        first_ins = TextTryer(
            NumberInt=NumberInt,
            Def=Def,
        ).parse('def hello(self, name):\n').first_ins

        self.assertEqual( {'name':None, 'hello':None, 'self':None}, first_ins.locals )

        self.assertTrue( len(first_ins.get_tree()) > 0 )

    def test_3(self):
        BoxLayout = _smart(
            IN_FORMAT=['BoxLayout', 'AnchorLayout'],
            OUT_FORMAT='Fragment, View.OnClickListener'
        )

        Pass = _smart(
            IN_FORMAT='pass',
            OUT_FORMAT=''
        )

        Object = _smart(
            IN_FORMAT='object',
            OUT_FORMAT=''
        )

        def on_class_instruction(self, i, ins):
            #print('---', ins, self)
            #if type(ins) == BoxLayout:
            #    self.in_block.blocks.insert(0, _Line('!!!'))
            return ins

        def on_class_block_start(self, block):
            if self.find_type_instruction(BoxLayout):
                block.blocks.insert(0, _Line('''    var rootView:View? = nil

    public override func onCreateView(_ inflater: LayoutInflater!, _ container: ViewGroup!, _ savedInstanceState: Bundle!) -> View?
    {
        rootView = inflater.inflate(R.layout.{layout}, container, false) as! View
        return rootView
    }
    '''.replace('{layout}', upper_to_lower(self.instructions[0].line.strip()))))

        Class = _smart(
            IN_FORMAT='class <EXP:NAME>(<EXP:LIST>):',
            OUT_FORMAT='public class <EXP:NAME>:<EXP:LIST>',
            locals={},
            init_locals={},
            on_instruction = on_class_instruction,
            on_block_start = on_class_block_start,
        )

        Def = _smart(
            IN_FORMAT='def <EXP:NAME>(self,<EXP:NAMES_LIST>):',
            OUT_FORMAT='public func <EXP:NAME>(<EXP:NAMES_LIST>)',
            locals={'self': Class}
        )

        DefStart = _smart(
            IN_FORMAT='self.<EXP:self.Def>(<EXP:LIST>)', # FIXME
            OUT_FORMAT='self.<EXP>(<EXP:LIST>)',
        )

        SelfRavno = _smart(
            IN_FORMAT='self.<EXP:NAME,^init_locals> = <EXP:^type>',
            OUT_FORMAT='self.<EXP:NAME> = <EXP>',
        )

        SelfText = _smart(
            IN_FORMAT='self.text = <EXP>',
            OUT_FORMAT='self.setText( <EXP> )',
        )

        Str = _smart(
            IN_FORMAT='"<EXP:TEXT>"',
            OUT_FORMAT='"<EXP:TEXT>"',
            TYPE_OUT='String',
        )

        t = TextTryer(
            NumberInt=NumberInt,
            BoxLayout=BoxLayout,
            SelfText=SelfText,
            SelfRavno=SelfRavno,
            Str=Str,
            DefStart=DefStart,
            Pass=Pass,
            Object=Object,
            Class=Class,
            Def=Def,
        ).parse('''
class Hi(AnchorLayout):
    def hello(self, name, age):
        pass
    def click_hello(self, x, y):
        self.hello("hello", 13)
        self.ttt = "ttt"
        self.text = "ttt"''')

        #print( '\n---] '.join(t.b.get_tree().split('\n')) )

    def test_4(self):
        Comment = _smart(
            IN_FORMAT='<EXP>#<EXP:TEXT>',
            OUT_FORMAT='<EXP> // <EXP:TEXT>',
        )

        CommentFull = _smart(
            IN_FORMAT='#<EXP:TEXT>',
            OUT_FORMAT='// <EXP:TEXT>',
        )

        t = TextTryer(
            NumberInt=NumberInt,
            Comment=Comment,
            CommentFull=CommentFull,
        ).parse('# coding: utf-8')

        self.assertEqual(type(t.b.blocks[0]), CommentFull)

    def test_6(self):
        Def = _smart(
            IN_FORMAT='def <EXP:NAME>(self):',
            OUT_FORMAT='public func <EXP:NAME>()',
            #locals={'self': Class}
        )

        Comment = _smart(
            IN_FORMAT='<EXP>#<EXP:TEXT>',
            OUT_FORMAT='<EXP> // <EXP:TEXT>',
        )

        CommentFull = _smart(
            IN_FORMAT='#<EXP:TEXT>',
            OUT_FORMAT='// <EXP:TEXT>',
        )

        Ravno = _smart(
            IN_FORMAT='<EXP:NAME> = <EXP>',
            OUT_FORMAT='<EXP:NAME> = <EXP>',
        )

        Str = _smart(
            IN_FORMAT='"<EXP:TEXT>"',
            OUT_FORMAT='"<EXP:TEXT>"',
            TYPE_OUT='String',
        )

        Str2 = _smart(
            IN_FORMAT="'<EXP:TEXT>'",
            OUT_FORMAT='"<EXP:TEXT>"',
            TYPE_OUT='String',
        )

        Lst = _smart(
            IN_FORMAT='[<EXP:LIST>]',
            OUT_FORMAT='[<EXP:LIST>]',
        )

        SelfPlusRavno = _smart(
            IN_FORMAT='self.R.<EXP:NAME>.text += <EXP>',
            OUT_FORMAT='R.<EXP:NAME>.append(<EXP>)',
        )

        Element = _smart(
            IN_FORMAT='<EXP>[<EXP>]',
            OUT_FORMAT='<EXP>[<EXP>]',
        )

        t = TextTryer(
            Element=Element,
            SelfPlusRavno=SelfPlusRavno,
            Str=Str,
            Str2=Str2,
            Lst=Lst,
            Ravno=Ravno,
            Def=Def,
            NumberInt=NumberInt,
            Comment=Comment,
            CommentFull=CommentFull,
        ).parse('''
def click_delit(self):
    z = [" / ", " / ", " / "]
    self.R.mainInput.text += z[1] #" / "
    #self.R.mainInput.text += z[1] #" / " FIXME
        ''')
        print( t.get_tree_text() )
        #self.assertEqual(type(t.b.blocks[0]), CommentFull)

    def test_5(self):
        Comment = _smart(
            IN_FORMAT='<EXP>#<EXP:TEXT>',
            OUT_FORMAT='<EXP> // <EXP:TEXT>',
        )

        CommentFull = _smart(
            IN_FORMAT='#<EXP:TEXT>',
            OUT_FORMAT='// <EXP:TEXT>',
            INDEX=-1000,
        )

        BoxLayout = _smart(
            IN_FORMAT=['BoxLayout', 'AnchorLayout'],
            OUT_FORMAT='Fragment, View.OnClickListener'
        )

        Pass = _smart(
            IN_FORMAT='pass',
            OUT_FORMAT=''
        )

        Object = _smart(
            IN_FORMAT='object',
            OUT_FORMAT=''
        )

        def on_class_instruction(self, i, ins):
            # print('---', ins, self)
            # if type(ins) == BoxLayout:
            #    self.in_block.blocks.insert(0, _Line('!!!'))
            return ins

        def on_class_block_start(self, block):
            if self.find_type_instruction(BoxLayout):
                #print('!!!!!', self, block, self.instructions)
                block.blocks.insert(0, _GoodLine('''    var rootView:View? = nil

    public override func onCreateView(_ inflater: LayoutInflater!, _ container: ViewGroup!, _ savedInstanceState: Bundle!) -> View?
    {
        rootView = inflater.inflate(R.layout.{layout}, container, false) as! View
        return rootView
    }
        '''.replace('{layout}', upper_to_lower(self.instructions[0].line.strip()))))

        Class = _smart(
            IN_FORMAT='class <EXP:NAME>(<EXP:LIST>):',
            OUT_FORMAT='public class <EXP:NAME>:<EXP:LIST>',
            locals={},
            init_locals={},
            on_instruction=on_class_instruction,
            on_block_start=on_class_block_start,
        )

        def on_def_simple_instruction(self,i,ins):
            if ins.line.startswith('click_'):
                if not '_ v:View?' in self.deleters_out[-1]:
                    self.deleters_out[-1] = self.deleters_out[-1][:-1] + '_ v:View?)'
            return ins

        DefSimple = _smart(
            IN_FORMAT='def <EXP:NAME>(self):',
            OUT_FORMAT='public func <EXP:NAME>()',
            locals={'self': Class},
            on_instruction=on_def_simple_instruction,
        )

        Def = _smart(
            IN_FORMAT='def <EXP:NAME>(self,<EXP:NAMES_LIST>):',
            OUT_FORMAT='public func <EXP:NAME>(<EXP:NAMES_LIST>)',
            locals={'self': Class}
        )

        DefStart = _smart(
            IN_FORMAT='self.<EXP:self.Def>(<EXP:LIST>)',
            OUT_FORMAT='self.<EXP>(<EXP:LIST>)',
        )

        #get_local

        SelfRavno = _smart(
            IN_FORMAT='self.<EXP:NAME,^init_locals> = <EXP:^type>',
            OUT_FORMAT='self.<EXP:NAME> = <EXP>',
        )

        Self = _smart(
            IN_FORMAT='self.<EXP:^get_local>',
            OUT_FORMAT='self.<EXP>',
        )

        # SelfRavno = _smart(
        #     IN_FORMAT='self.<EXP:NAME,^init_locals> = <EXP:^type>',
        #     OUT_FORMAT='self.<EXP:NAME> = <EXP>',
        # )

        def on_self_plus_ravno_get_tree(self, text):
            name = self.instructions[0].line
            if name.endswith('Label'):
                tip = 'TextView'
            elif name.endswith('Input'):
                tip = 'EditText'
            #print(self, text, tip)
            text = text.replace('{tip}', tip)
            return text

        SelfRavnoText = _smart(
            IN_FORMAT='self.R.<EXP:NAME>.text = <EXP>',
            OUT_FORMAT='((rootView as! View).findViewById(R.id.<EXP:NAME>) as! {tip}).setText(<EXP>)',
            on_get_tree=on_self_plus_ravno_get_tree,
        )

        SelfPlusRavno = _smart(
            IN_FORMAT='self.R.<EXP:NAME>.text += <EXP>',
            OUT_FORMAT='((rootView as! View).findViewById(R.id.<EXP:NAME>) as! {tip}).append(<EXP>)',
            on_get_tree=on_self_plus_ravno_get_tree,
        )

        SelfText = _smart(
            IN_FORMAT='self.text = <EXP>',
            OUT_FORMAT='self.setText( <EXP> )',
        )

        Element = _smart(
            IN_FORMAT='<EXP>[<EXP>]',
            OUT_FORMAT='<EXP>[<EXP>]',
        )

        # FIXME
        # Str = _smart(
        #     IN_FORMAT=['"<EXP:TEXT>"', "'<EXP:TEXT>'"],
        #     OUT_FORMAT='"<EXP:TEXT>"',
        #     TYPE_OUT='String',
        # )

        Str = _smart(
            IN_FORMAT='"<EXP:TEXT>"',
            OUT_FORMAT='"<EXP:TEXT>"',
            TYPE_OUT='String',
        )

        Str2 = _smart(
            IN_FORMAT="'<EXP:TEXT>'",
            OUT_FORMAT='"<EXP:TEXT>"',
            TYPE_OUT='String',
        )

        Del1 = _smart(
            IN_FORMAT='from kivy.uix.boxlayout import BoxLayout',
            OUT_FORMAT='',
        )

        For = _smart(
            IN_FORMAT='for <EXP:NAME> in <EXP>:',
            OUT_FORMAT='for <EXP:NAME> in <EXP>',
        )

        Lst = _smart(
            IN_FORMAT='[<EXP:LIST>]',
            OUT_FORMAT='[<EXP:LIST>]',
        )

        Print = _smart(
            IN_FORMAT='print(<EXP:LIST>)',
            OUT_FORMAT='print(<EXP:LIST>)',
        )

        Ravno = _smart(
            IN_FORMAT='<EXP:NAME> = <EXP>',
            OUT_FORMAT='<EXP:NAME> = <EXP>',
        )

        Range = _smart(
            IN_FORMAT='range(<EXP:LIST>)',
            OUT_FORMAT='range(<EXP:LIST>)',
        )

        # FIXME
        # def on_tochka_try_instruction(self, i, line):
        #     print('---.', line, self)
        #     if line == 'self':
        #         return _Line('self')
        #     if line == 'R':
        #         return _Line('R')
        #     if line.endswith('Label') or line.endswith('Input'):
        #         return _Line(line)
        #     return None
        #
        # Tochka = _smart(
        #     IN_FORMAT='<EXP>.<EXP>',
        #     OUT_FORMAT='<EXP>.<EXP>',
        #     on_try_instruction=on_tochka_try_instruction,
        # )

        t = TextTryer(
            Self=Self,
            Element=Element,
            Range=Range,
            #Tochka=Tochka,
            Ravno=Ravno,
            Print=Print,
            NumberInt=NumberInt,
            Lst=Lst,
            For=For,
            Del1=Del1,
            Comment=Comment,
            CommentFull=CommentFull,
            BoxLayout=BoxLayout,
            SelfText=SelfText,
            SelfRavno=SelfRavno,
            SelfRavnoText=SelfRavnoText,
            SelfPlusRavno=SelfPlusRavno,
            Str=Str,
            Str2=Str2,
            DefStart=DefStart,
            Pass=Pass,
            Object=Object,
            Class=Class,
            DefSimple=DefSimple,
            Def=Def,
        ).parse('''
# coding: utf-8
from kivy.uix.boxlayout import BoxLayout

class CalcWidget(BoxLayout):

    def click_ac(self):
        for a in [1, 2, 3]:
            print( a )
        self.R.mainLabel.text = ""
        self.R.mainInput.text = ""

    def click_break(self):
        for a in range(0, 10):
            pass
        self.R.mainLabel.text = ""
        self.R.mainInput.text = self.R.mainInput.text[:-1] # FIXME

    def click_delit(self):
        z = [" / ", " / ", " / "]
        self.R.mainInput.text += z[1] #" / "

    def click_multiply(self):
        self.ttt = "hello"
        self.R.mainInput.text += " * "
        print(self.ttt)

    def click_minus(self):
        self.R.mainInput.text += " - "

    def click_plus(self):
        self.R.mainInput.text += " + "

    def click_zapyata(self):
        self.R.mainInput.text += ","

    def click_skobki(self):
        self.R.mainLabel.text = "( )"

    def click_count(self):
        self.R.mainLabel.text = '{:.2f}'.format( eval(self.R.mainInput.text) )

    def click_0(self):
        self.R.mainLabel.text = "000"
        self.R.mainInput.text += "0"

    def click_1(self):
        self.R.mainLabel.text = "111"
        self.R.mainInput.text += "1"

    def click_2(self):
        self.R.mainLabel.text = "222"
        self.R.mainInput.text += "2"

    def click_3(self):
        self.R.mainLabel.text = "333"
        self.R.mainInput.text += "3"

    def click_4(self):
        self.R.mainLabel.text = "444"
        self.R.mainInput.text += "4"

    def click_5(self):
        self.R.mainLabel.text = "555"
        self.R.mainInput.text += "5"

    def click_6(self):
        self.R.mainLabel.text = "666"
        self.R.mainInput.text += "6"

    def click_7(self):
        self.R.mainLabel.text = "777"
        self.R.mainInput.text += "7"

    def click_8(self):
        self.R.mainLabel.text = "888"
        self.R.mainInput.text += "8"

    def click_9(self):
        self.R.mainLabel.text = "999"
        self.R.mainInput.text += "9"
''')

        print( '\n---] '.join(t.b.get_tree().split('\n')) )




if __name__=='__main__':

    main()

