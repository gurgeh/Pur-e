class Context:
    def __init__(self, parent=None):
        self.local = {}
        self.parent = parent

    def __getitem__(self, key):
        if key in self.local: return self.local[key]
        else: return self.parent[key]

    def __setitem__(self, key, val):
        self.local[key] = val

    def contains(self, context):
        for key, val in context.local.items():
            if key not in self.local:
                return False
            if not self.local[key].contains(val):
                return False
        return True

    def nest(self):
        return Context(self)

    def flatcopy(self):
        retc = Context()
        self.flatcopyto(retc)
        return retc

    def flatcopyto(self, retc):
        for key, val in self.local.items():
            if key not in retc.local:
                retc.local[key] = val

        if self.parent is not None:
            self.parent.flatcopyto(retc)
