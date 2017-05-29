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
                arg_to_instance={},
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
            arg_to_instance={},
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
            IN_FORMAT='self.<EXP:NAME,^arg_to_instance> = <EXP:^type>',
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
            arg_to_instance={},
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

        _URLER_HAVER = [None]

        def _on_def_init_end(self):
            if _URLER_HAVER[ 0 ]:
                print('DEF INIT:', self, _URLER_HAVER[ 0 ])
                self.instructions = self.instructions[:1] + [_GoodLine('_ status: Status? = nil, _ data: String? = nil')]
                self._BLOCK_START = '    -> [String: String]!\n    {'

                func_name = self.instructions[0].line
                self.instructions[0].line += '_answer'

                self._URLER_OK = '''public func {FUNC_NAME}(_ view: View? = nil) {
        var params = self.{FUNC_NAME}_answer(Status(0, true), nil)

        // Instantiate the RequestQueue.
        var queue = Volley.newRequestQueue(self.getActivity())  // RequestQueue
        var url = "{URL}"   // String

        class ResponseListener: Response.Listener<String> {
            var me:{CLASS_NAME}
            init(_ me:{CLASS_NAME}) {
                self.me = me
            }
            func onResponse(_ response: String) {
                self.me.{FUNC_NAME}_answer(Status(200), response)
            }
        }

        class ErrorListener: Response.ErrorListener {
            var me:{CLASS_NAME}
            init(_ me:{CLASS_NAME}) {
                self.me = me
            }
            func onErrorResponse(_ error: VolleyError!) {
                var statusCode = error.networkResponse.statusCode
                var response:NetworkResponse = error.networkResponse
                var headers = response.headers
                if statusCode == 302 {
                    var queue2 = Volley.newRequestQueue(self.me.getActivity())  // RequestQueue
                    var url2 = headers["location"]   // String
                    var stringRequest2 = StringRequest(Request.Method.GET, url2,
                        ResponseListener(self.me), ErrorListener(self.me))
                    queue2.add(stringRequest2)
                } else {
                    //((self.me.rootView as! View).findViewById(R.id.nameInput) as! EditText).setText("Error: " + statusCode+" "+response.data)
                }
            }
        }

        // Request a string response from the provided URL.
        var stringRequest = StringRequest(Request.Method.GET, url,
                ResponseListener(self), ErrorListener(self))

        // Add the request to the RequestQueue.
        queue.add(stringRequest)
    }
    '''.replace('{URL}', _URLER_HAVER[ 0 ].instructions[0].get_tree()).replace(
                    '{FUNC_NAME}', func_name).replace(
                    '{CLASS_NAME}', _URLER_HAVER[ 0 ].instructions[0].get_parent_class().instructions[0].line)
                _URLER_HAVER[0].instructions[0].get_parent_class().get_parent_block().blocks.insert(0,
                     _GoodLine('''
import com.android.volley
import com.android.volley.toolbox

public class Status
{
 	var value: Int16
 	ver before: Boolean

 	init(_ value: Integer!, _ before: Boolean!) {
 		self.value = value
 		self.before = before
 	}
}
                     ''')
                                                                                                    )
                _URLER_HAVER[ 0 ] = None

        def _on_def_get_tree(self, text):
            if hasattr(self, '_URLER_OK'):
                return self._URLER_OK + text
            return text

        Def = _smart(
            IN_FORMAT='def <EXP:NAME>(self,<EXP:NAMES_LIST>):',
            OUT_FORMAT='public func <EXP:NAME>(<EXP:NAMES_LIST>)',
            locals={'self': Class},
            on_init_end=_on_def_init_end,
            on_get_tree=_on_def_get_tree
        )

        def _on_urler_init(self):
            _URLER_HAVER[ 0 ] = self

        URLER_OK = _smart(
            '@URLER_OK(<EXP:TEXT>)',
            '//URLER_OK: <EXP:TEXT>',
            on_init=_on_urler_init,
        )

        DefStart = _smart(
            IN_FORMAT='self.<EXP:self.Def>(<EXP:LIST>)',
            OUT_FORMAT='self.<EXP>(<EXP:LIST>)',
        )

        #get_local

        SelfRavno = _smart(
            IN_FORMAT='self.<EXP:NAME,^arg_to_instance> = <EXP:^type>',
            OUT_FORMAT='self.<EXP:NAME> = <EXP>',
        )

        Self = _smart(
            IN_FORMAT='self.<EXP:^get_local>',
            OUT_FORMAT='self.<EXP>',
        )

        # SelfRavno = _smart(
        #     IN_FORMAT='self.<EXP:NAME,^arg_to_instance> = <EXP:^type>',
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

        Range2 = _smart(
            IN_FORMAT='range(<EXP>, <EXP>)',
            OUT_FORMAT='<EXP>...<EXP>'
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
        Eval = _smart(
            IN_FORMAT='eval(<EXP>)',
            OUT_FORMAT='Expression(<EXP>).eval()',
        )

        # FIXME !!!
        Format = _smart(
            IN_FORMAT="'{:.2f}'.format(<EXP>)",
            OUT_FORMAT='java.lang.String.format("%.2f", <EXP>)',
        )

        Bad = _smart(
            IN_FORMAT='self.R.<EXP:TEXT>.text',
            OUT_FORMAT='R.<EXP:TEXT>.getText().toString()',
        )

        StatusBefore = _smart(
            IN_FORMAT='status.before',
            OUT_FORMAT='status.before',
        )

        If = _smart(
            IN_FORMAT='if <EXP>:',
            OUT_FORMAT='if <EXP>',
        )

        Else = _smart(
            IN_FORMAT='else:',
            OUT_FORMAT='else',
        )

        Return = _smart(
            IN_FORMAT='return <EXP>',
            OUT_FORMAT='return <EXP>',
        )

        # GridControl = _smart(
        #     IN_FORMAT='class GridControl:',
        #     OUT_FORMAT='',
        # )
        #
        # GridControlChild = _smart(
        #     IN_FORMAT='class <EXP:NAME>(GridControl):',
        #     OUT_FORMAT='public class <EXP:NAME>: GridControl',
        # )

        def _on_GridControlCreate_init_end(self):
            self.get_parent_class().get_parent_block().blocks.insert(0,
                _GoodLine('''
public class {NAME}GridControl {
    var listView:ListView
    var adapter:ArrayAdapter

    init(_ layout: Integer!, _ listView: ListView!, _ context: Context!) {
        // получаем экземпляр элемента ListView
        self.listView = listView

        // используем адаптер данных
        self.adapter = ArrayAdapter<{NAME}GridControlItem>(context, layout)

        self.listView.setAdapter(self.adapter)
    }
}
                '''.replace('{NAME}', self.instructions[0].line)
                          ))


        GridControlCreate = _smart(
            IN_FORMAT='self.grid_control = <EXP:TEXT>GridControl(grid=self.ids.<EXP:TEXT>)',
            OUT_FORMAT='self.grid_control = <EXP:TEXT>GridControl(R.layout.<EXP:TEXT>, self.findViewById(R.id.<EXP[1]:TEXT>) as! ListView)',
            on_init_end=_on_GridControlCreate_init_end
        )

        GridControlItem = _smart(
            IN_FORMAT='class <EXP:TEXT>GridControlItem(GridControlItem):',
            OUT_FORMAT = 'public class <EXP:TEXT>GridControlItem'
        )

        GridControlString = _smart(
            IN_FORMAT='<EXP:TEXT> = GridControlString()',
            OUT_FORMAT='var <EXP:TEXT>: String = ""'
        )
        GridControlInt = _smart(
            IN_FORMAT='<EXP:TEXT> = GridControlInt()',
            OUT_FORMAT='var <EXP:TEXT>: Integer = 0'
        )



        Init = _smart(
            IN_FORMAT='def __init__(self, parent):',
            OUT_FORMAT='func init()'
        )

        Super = _smart(
            IN_FORMAT='super(<EXP:TEXT>, self).__init__(parent)',
            OUT_FORMAT='// super(<EXP:TEXT>, self).__init__(parent)',
        )

        t = TextTryer(
            Super=Super,
            Init=Init,
            GridControlItem=GridControlItem,
            GridControlCreate=GridControlCreate,
            GridControlString=GridControlString,
            GridControlInt=GridControlInt,
            #GridControlChild=GridControlChild,
            #GridControl=GridControl,
            Return=Return,
            If=If,
            Else=Else,
            StatusBefore=StatusBefore,
            Bad=Bad,
            Format=Format,
            Eval=Eval,
            Self=Self,
            Element=Element,
            Range=Range,
            Range2=Range2,
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
            URLER_OK=URLER_OK,
        ).parse('''
# coding: utf-8
from kivy.uix.boxlayout import BoxLayout


# class GridControl:
#
#     def __init__(self, grid):
#         self.grid = grid
#         self.widgets = {}
#
#     def clear_grid(self):
#         self.grid.clear_widgets()
#         self.widgets = {}
#
#     def add_widget(self, index, widget):
#         if index not in self.widgets:
#             self.widgets[ index ] = widget
#             self.grid.add_widget(widget, index)
#         else:
#             raise Exception('wrong work!!! index = {}'.format(index))

class TasksGridControlItem(GridControlItem):
    title = GridControlString()
    task_id = GridControlInt()
    task_state = GridControlString()
    executor = GridControlString()
    #date = GridControlDatetime()
    full_info = GridControlString()


# class TasksGridControl(GridControl):
#
#     # item_class = TaskBoxItem
#
#     def create_widget(self, index, item):
#         # task_box = TaskBox(**item.params)
#         # task_box.complete_task_box()
#         # self.add_widget(index, task_box)
#         pass



class CalcWidget(BoxLayout):

    # def __init__(self, parent):
    #     super(CalcWidget, self).__init__(parent)

    def init_grid_control(self):
        self.grid_control = TasksGridControl(grid=self.ids.tasks_box_grid)

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

    def click_count(self):
        self.R.mainLabel.text = '{:.2f}'.format( eval(self.R.mainInput.text) )

        s = eval(self.R.mainInput.text)
        self.R.mainLabel.text = '{:.2f}'.format( s )

    def click_0(self):
        self.R.mainLabel.text = "000"
        self.R.mainInput.text += "0"

    @URLER_OK('/data/')
    def get_data(self, status=None, data=None):
        if status.before:
            print('login start...')
            #return {'name':self.ids.nameInput.text, 'pass':self.ids.passwordInput.text}
        else:
            text = 'login... {}'.format(status)
            print(text)
            # FIXME: print('login... {}'.format(status))
''')

        print( '\n---] '.join(t.b.get_tree().split('\n')) )

    def test_7(self):
        from coup.objecter_core._Smart import _line_to_slashs

        def tst(line, deleters_in, IN_FORMAT=None):
            out = _line_to_slashs(
                line=line,
                deleters_in=deleters_in,
                #IN_FORMAT=IN_FORMAT
            )
            print('>>> {}'.format(line))
            print('    {}'.format(out))

        tst(
            line='for a in [1, 2, 3]:',
            deleters_in=['for ', ' in '],
            #IN_FORMAT='for <EXP> in <EXP>:'
        )

        tst(
            line="self.do_something('{:.2f}'.format())",
            deleters_in=['self.', '(', ')'],
            #IN_FORMAT='self.<EXP>(<EXP>)'
        )

    def test_8(self):
        from coup.objecter_core._Base import _Block


        def new_smart(*args, **kwargs):
            return _smart(*args, BLOCK_START='begin', BLOCK_END='end', **kwargs)


        def is_line_starts_block(self, line):
            return line.strip().endswith('{')

        def is_line_continue_block(self, line):
            return not line.endswith('}') and not is_line_starts_block(self, line)

        # @staticmethod
        def is_start(line):
            return line.strip().endswith('{')

        def is_end(self, line):
            return line.endswith('}')


        _Block.is_start = is_start
        _Block.is_end = is_end
        #_Block.is_line_starts_block = is_line_starts_block
        #_Block.is_line_continue_block = is_line_continue_block


        Comment = new_smart(
            IN_FORMAT='<EXP>#<EXP:TEXT>',
            OUT_FORMAT='<EXP> // <EXP:TEXT>',
        )

        CommentFull = new_smart(
            IN_FORMAT='#<EXP:TEXT>',
            OUT_FORMAT='// <EXP:TEXT>',
        )

        If = new_smart(
            IN_FORMAT='if (<EXP>) {',
            OUT_FORMAT='if <EXP> then',
        )

        More = new_smart(
            IN_FORMAT='<EXP:NAME> > <EXP>',
            OUT_FORMAT='<EXP:NAME> > <EXP>',
        )

        Str = new_smart(
            IN_FORMAT='"<EXP:TEXT>"',
            OUT_FORMAT='"<EXP:TEXT>"',
            TYPE_OUT='str',
        )
        Print = new_smart(
            IN_FORMAT='print(<EXP>);',
            OUT_FORMAT='print(<EXP>)',
        )
        BlockEnd = new_smart(
            IN_FORMAT='}',
            OUT_FORMAT='',
        )

        t = TextTryer(
            NumberInt=NumberInt,
            Comment=Comment,
            CommentFull=CommentFull,
            If=If,
            More=More,
            Str=Str,
            Print=Print,
            BlockEnd=BlockEnd,
        ).parse('''# coding: utf-8
if (x > 17) {
    print("hello");
}
        ''')

        #self.assertEqual(type(t.b.blocks[0]), CommentFull)
        print( t.get_tree_text() )

    def test_9(self):

        # *** Now you import is simple.
        #
        # *** Subclass from Translater,
        #     and that's all you need.

        from coup import Translater, accord, Accord

        class ToGOBase(Translater):

            OUT_START = ['package main',
                         'import "fmt"']

            Main = accord(
                IN = "if __name__ == '__main__':",
                OUT = 'func main()'
            )

            Print = accord(
                IN =  'print(<EXP>)',
                OUT = 'fmt.Println(<EXP>)',
            )

        class ToGO(ToGOBase):

            class Str(Accord):
                IN = "'<EXP:TEXT>'"
                OUT = '"<EXP:TEXT>"'

                def _hello(self):
                    print('Hello!')

                def on_init(self, *args, **kwargs):
                    print('on_init:', args, kwargs)
                    self._hello()

        last_text = '''
if __name__ == '__main__':
    print('Hello!')
'''
        new_text = ToGO.translate(last_text)

        print('last_text lines: {}'.format(len(last_text.split('\n'))))
        print(new_text)
        print('new_text lines: {}'.format(len(new_text.split('\n'))))




if __name__=='__main__':

    main()

