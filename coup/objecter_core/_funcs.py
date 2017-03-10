
def into_maybe_kavichki(func):
    def new_func(self, value, *args, **kwargs):
        pre, value = (value[0], value[1:]) if value[0] in ("'", '"') else ('', value)
        value, post = (value[:-1], value[-1]) if value[-1] in ("'", '"') else (value, '')

        if hasattr(self, 'value_prefix'):
            if self.value_prefix == '@+id/' and len(pre) == 0:
                pre = post = "'"

        #print('***', value, '|', pre, post)

        return pre + func(self, value, *args, **kwargs) + post
    return new_func

def remove_kavichki(s):
    s = s.strip()
    if len(s) > 0:
        for a in ('"', "'"):
            if s[0] == a:
                return s.replace(a, '')
        # if s[0] in ('"', "'"):
        #     return s[1:-1]
    return s

def add_kavichki(s):
    if len(s)==0 or s[0] in ('"', "'"):
        return s
    return '"' + s + '"'

def need_be_id(s):
    if s.startswith('@+id/'):
        return s
    return '@+id/' + s

def _full_find_string(line, find_str):
    stripped = line.strip()
    if stripped.startswith(find_str):
        lst = line.split(find_str)[1].split('.')
        line = find_str + '.'.join(lst[:1])
    return line

def _get_find_attr(line, find_str):
    lst = line.split(find_str)[1].split('.')
    return lst[0]

def _format_line_by_methods(line, method_formaters):
    if '=' in line:
        lst = line.split('=')
        setter = ''.join(lst[0].split('.')[-1].split(' '))
        if setter in method_formaters:
            lst[0] = lst[0].replace(setter, '').rstrip()
            lst[1] = method_formaters[setter].format(lst[1].strip())
        line = ''.join(lst)
    return line

def _get_tip_from_name(attr):
    d = {
        'Label': 'TextView',
        'Input': 'EditText',
    }
    for a in d:
        if attr.endswith(a):
            return d[a]
