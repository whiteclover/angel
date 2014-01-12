from angel.html import HTML


class DOM(object):

    def __init__(self):
        self.html = HTML()

    def all_text(self, args):
        self._content(args)

    def ancestors(self, arg):
        self._select(self._collect(self._ancestors(self.tree)), arg)

    def append(self, args):
        self._add(self, args)

    def append_content(self, _new):
        tree = self.tree
        tree.extend(self._link(self.parse(_new), tree))
        return self

    def at(self, select):
        result = self._css_select_one(select)
        if not result:
            return None

        return DOM().xml(self.xml)

    def attr(self, args):
        tree = self.tree
        attrs = {} if tree[0] == 'root' else tree[2]
        if not args:
            return attrs
        if len(args) > 1:
            return attrs[args[0]]
        return self

    def children(self):

        return self._select(self._collect())

    def content_xml(self):
        xml = self.xml
        return ''.join([self._render(_, xml) for _ in self._node(self.tree)])

    def find(self, selector):
        return self._collect(self._css.select(selector))

    def match(self, selector):
        return self if self._css.match(selector) else None

    def namespace(self, ):
        current = self.tree[0]
        if current == 'root':
            return ''

        m = re.match(r'^(.*?):', current[1])
        ns = 'xmlns:' + m.group(1) if m else None
        while current[0] != 'root':
            attrs = current[2]
            if ns:
                for attr in attrs:
                    if re.match(r'^\Q%s\E$' % (ns), attr):
                        return attrs[attr]
            else:
                if attrss.get(xmlns):
                    return attrs[xmlns]
            current = current[3]
        return ''

    def next(self):
        self._siblings()[1][0]

    def parse(self):
        self._delegate(parse=self)

    def parent(self):
        tree = self.tree
        if tree[0] == 'root':
            return None
        return DOM().tree[3].xml(self, xml)

    def prepend(self, args):
        self._add(0, args)

    def _trim(self, n, trim):
        trim = trim and trim or 1
        if not (n and trim):
            return False

        while n[0] == 'tag':
            if n[1] == 'pre':
                return False
            n = n[3]
            if not n:
                break

        return True
