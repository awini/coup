

class _ExpLine(object):

    def __init__(self, fline):
        fline = fline.strip()
        last_pos = 0
        self.exp_list = []

        while True:
            start, end = _Exp.find_me(fline)

            if start < 0:
                self.add_splitter(fline[last_pos:])
                break

            splitter, fline, exp = fline[last_pos:start], fline[end:], fline[start:end]

            if start > 0:
                self.add_splitter(splitter)

            self.exp_list.append(_Exp(exp))

    def __str__(self):
        return '_ExpLine({})'.format(' '.join(str(e) for e in self.exp_list))

    def add_splitter(self, splitter):

        splitter = splitter.strip()

        if len(splitter) == 0:
            raise Exception('Space splitter')
        else:
            self.exp_list.append(_Splitter(splitter))

    def is_me(self, line):
        exps = []
        for e in self.exp_list:
            if type(e) == _Splitter:
                new_exps, line = e.extend_from_line(line)
                exps += new_exps
        if len(line) > 0:
            exps.append(line)
        for e, ne in zip(self.exp_list, exps):
            if type(e) == _Splitter:
                if type(ne) != _Splitter or e != ne:
                    return False
            else:
                if type(ne) == _Splitter:
                    return False
                if not e.is_me(ne):
                    return False
        return True

    @property
    def splitters(self):
        return [s for s in self.exp_list if type(s) == _Splitter]


class _Exp:

    def __init__(self, line):
        self.line = line

    def __str__(self):
        return '_Exp({})'.format(self.line)

    @classmethod
    def find_me(cls, line):
        start = line.find('<EXP')
        end = -1
        if start >= 0:
            end = line.find('>', start+1)
            if end < 0:
                raise Exception('Exp not ends')
            end += 1
        return start, end

    # FIXME
    def is_me(self, line):
        return len(line.strip()) > 0


class _Splitter(object):

    def __init__(self, splitter):
        self.splitter = splitter

    def __str__(self):
        return '_Spl({})'.format(self.splitter)

    def __eq__(self, other):
        return self.splitter == other.splitter

    def extend_from_line(self, line):
        lst = line.split(self.splitter)
        exp, line = lst[0].strip(), self.splitter.join(lst[1:]).strip()
        if len(exp) == 0:
            return [self], line
        else:
            return [exp, self], line



if __name__=='__main__':


    rule = _ExpLine('for <EXP:text> in <EXP:text>:')
    print(rule)
    line = 'for a in [1, 2, 3]:'
    print(rule.is_me(line))