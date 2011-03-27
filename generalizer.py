#deal with None in shadow_core
#soften arguments

class Generalizer:
    def __init__(self):
        self.argmap = {}

    def has(self, args):
        if tuple(args) in self.argmap:
            return self.argmap[tuple(args)]
        self.argmap[tuple(args)] = None

    def get(self, args):
        return self.argmap[tuple(args)]

    def set(self, args, val):
        self.argmap[tuple(args)] = val
