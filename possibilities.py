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

    def contains(self, p2):
        if not p2: return True
        for poss2 in p2:
            found = False
            for poss1 in self:
                if poss1.contains(poss2):
                    found = True
                    break
            if not found:
                return False
        return True

    def simplify(self):
        types = {}
        for val in self.values:
            key = val.__class__
            if key not in types: types[key] = []
            types[key].append(val)
        
        self.values = []
        for t, vals in types.items():
            first = True
            theval = None
            for val in vals:
                if first:
                    theval = val
                    first = False
                else:
                    theval.generalize(val)
            self.values.append(theval)
            
