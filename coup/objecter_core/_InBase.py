from ._Base import _Base, _Line


class _InSimpleBase(_Base):
    IN_LEFT = None
    IN_RIGHT = None
    IN_LEFT_TO = None
    IN_RIGHT_TO = None

    def __init__(self, string, parent=None, line_number=0):
        #print(line_number, self)
        super(_InSimpleBase, self).__init__(string, parent, line_number)

        self.init_in(string, parent)

    def init_in(self, string, parent=None):
        in_string = string.split(self.IN_LEFT)[1].split(self.IN_RIGHT)[0]
        self.init_in_instructions(in_string)

    def init_in_instructions(self, string):
        raise NotImplementedError

    def get_tree_main(self):
        return (self.get_in_left_to() +
                self.get_tree_in() +
                self.get_in_right_to())

    def get_tree_in(self):
        raise NotImplementedError

    @classmethod
    def is_instruction(cls, line, parent=None, line_number=None):
        st = line.strip()
        if st.startswith(cls.IN_LEFT) and st.endswith(cls.IN_RIGHT):
            return True

    @classmethod
    def get_in_left_to(cls):
        return cls.IN_LEFT if cls.IN_LEFT_TO == None else cls.IN_LEFT_TO

    @classmethod
    def get_in_right_to(cls):
        return cls.IN_RIGHT if cls.IN_RIGHT_TO == None else cls.IN_RIGHT_TO

class _InReplacersAbility:

    IN_REPLACERS = []

    @classmethod
    def try_instruction(cls, line, line_number=0, parent=None):
        # if len(cls.IN_REPLACERS) > 0:
        #     print(cls.IN_REPLACERS)
        instructers = cls.IN_REPLACERS + _Line._INSTRUCTS
        return _Line.try_instruction_base(line, instructers, parent=parent, line_number=line_number)

class _InBase(_InSimpleBase, _InReplacersAbility):

    def init_in_instructions(self, string):
        strings = string.split(',') #string.split(self.IN_LEFT)[1].split(self.IN_RIGHT)[0].split(',')
        self.init_in_instructions_by_strings(strings)

    def init_in_instructions_by_strings(self, strings):
        self.in_instructions = [ self.on_new_instruction(self.try_instruction(s, parent=self, line_number=self.line_number)) for s in strings ]

    def on_new_instruction(self, ins):
        return ins

    def get_tree_in(self):
        return ','.join(s.get_tree() for s in self.in_instructions)