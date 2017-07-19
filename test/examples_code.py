# coding: utf-8

code = '''# coding: utf-8

class MainWidget:

    def click_ac(self):
        for a in [1, 2, 3]:
            print( a )
        self.ids.mainInput.text = ""

    def click_break(self):
        for a in range(0, 10):
            pass
        self.ids.mainInput.text = self.ids.mainInput.text[:-1]

    def click_delit(self):
        z = [" / ", " / ", " / "]
        self.ids.mainInput.text += z[1] # " / "

    def click_multiply(self):
        self.ttt = 'hello'
        self.ids.mainInput.text += " * "
        print(self.ttt)

    def click_plus(self):
        self.ids.mainInput.text += " + "

    def click_skobki(self):
        self.ids.mainInput.text = "(" + self.ids.mainInput.text + ")"

    def click_count(self):
        text = self.ids.mainInput.text
        text2 = eval(text)
        text3 = '{:.2f}'.format( text2 )
        self.ids.mainInput.text = text3.replace(',', '.')

    def click_1(self):
        self.ids.mainInput.text += "1"

mw = MainWidget()
mw.click_ac()
mw.click_1()
mw.click_plus()
mw.click_1()
print(mw.ids.mainInput.text)
'''

need_result_js = '''// coding: utf-8
class MainWidget
{
    click_ac()
    {
        for (var i=0,lst=[1,  2,  3],a=lst[i];i<lst.length;i++,a=lst[i])
        {
            console.log(a)
        }
        this.ids.mainInput.text = ""
    }
    click_break()
    {
        for (var i=0,lst=[...Array(10).keys()].slice(0),a=lst[i];i<lst.length;i++,a=lst[i])
        {
        }
        this.ids.mainInput.text = this.ids.mainInput.text.slice(-1)
    }
    click_delit()
    {
        var z = [" / ", " / ", " / "]
        this.ids.mainInput.text += z[1] // " / "
    }
    click_multiply()
    {
        this.ttt = 'hello'
        this.ids.mainInput.text += " * "
        console.log(this.ttt)
    }
    click_plus()
    {
        this.ids.mainInput.text += " + "
    }
    click_skobki()
    {
        this.ids.mainInput.text = "(" + this.ids.mainInput.text + ")"
    }
    click_count()
    {
        var text = this.ids.mainInput.text
        var text2 = eval(text)
        var text3 = '{:.2f}' + text2
        this.ids.mainInput.text = text3.replace(',', '.')
    }
    click_1()
    {
        this.ids.mainInput.text += "1"
    }
}
var mw = new MainWidget()
mw.click_ac()
mw.click_1()
mw.click_plus()
mw.click_1()
console.log(mw.ids.mainInput.text)'''

need_result_php = '''// coding: utf-8
class MainWidget
{
    function click_ac()
    {
        foreach ([1, 2, 3] as $a)
        {
            print(a);
        }
        $this->ids.mainInput.text = "";
    }
    function click_break()
    {
        foreach (range(0, 10-1) as $a)
        {
        }
        $this->ids.mainInput.text = array_slice($this->ids.mainInput.text, 0, -1);
    }
    function click_delit()
    {
        $z = [" / ",  " / ",  " / "];
        $this->ids.mainInput.text += $z[1]; // " / "
    }
    function click_multiply()
    {
        $this->ttt = "hello";
        $this->ids.mainInput.text += " * ";
        print($this->ttt);
    }
    function click_plus()
    {
        $this->ids.mainInput.text += " + ";
    }
    function click_skobki()
    {
        $this->ids.mainInput.text = "(" + $this->ids.mainInput.text + ")";
    }
    function click_count()
    {
        $text = $this->ids.mainInput.text;
        $text2 = eval(text);
        sprintf($text3 = "{:.2f}", text2);
        str_replace(",", ".", $this->ids.mainInput.text = text3);
    }
    function click_1()
    {
        $this->ids.mainInput.text += "1";
    }
}
$mw = new MainWidget();
mw.click_ac();
mw.click_1();
mw.click_plus();
mw.click_1();
print(mw.ids.mainInput.text);'''
