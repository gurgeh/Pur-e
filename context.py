class Context:
    def __init__(self, parent=None):
        self.local = {}
        self.parent = parent

    def __getitem__(self, key):
        if key in self.local: return self.local[key]
        else: return self.parent[key]

    def __setitem__(self, key, val):
        self.local[key] = val

    def nest(self):
        return Context(self)
