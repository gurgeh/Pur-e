#remove duplicates

class Poss:
    def __init__(self, *args):
        self.values = list(args)

    def add(self, val):
        self.values.append(val)

    def extend(self, iterable):
        for val in iterable:
            self.add(val)

    def __iter__(self):
        return self.values.__iter__()


    def __repr__(self):
        return str(self.values)
