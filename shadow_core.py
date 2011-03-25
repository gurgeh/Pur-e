"""
I need a Possibilities-object which has one or more values, with conditions attached. It is iterable, so it can be used to generate more possibilites.

It may be a tree structure, to represent a host of subvalues with the some preconditions in common. I need to think more of execution, but maybe this way I mitigate exponential path explosion somewhat?

---

Implement Poss
N
.
recursion (maybe a max_recursive_analysis param, so we can go further than 1)
T
generalizer
L
!
design class system
implement in shadow
convert DataBool, etc, if necessary
.
better mul
use conditions and constraints in reasoning
.
uniqueness typing
.
world object
.
currying? (probably just syntactic sugar for wrapper function)
generators?
optional lazy arguments (like if and or)?

module system and parser and we are ready for others to test

"""

class SLet:
    def __init__(self, bindings, inexpr):
        self.bindings = bindings
        self.inexpr = inexpr

    def analyze(self, context):
        for name, expr in self.bindings:
            context[name] = expr

        for name, expr in self.bindings:
            context[name] = expr.analyze(context.nest())

        return self.inexpr.analyze(context.nest()):

class SFunction:
    def __init__(self, argnames, expr=None):
        self.argnames = argnames
        self.expr = expr

    def analyze(self, context):
        return Poss(self)

    def callalyze(self, context, args):
        assert len(args) == len(self.argnames)
        
        for name, expr in zip(self.argnames, args):
            context[name] = expr

        if self.expr:
            return self.expr.analyze(context.nest())
        
class SCall:
    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def analyze(self, context):
        return Poss(*[fun.callalyze(context, [x.analyze(context.nest()) for x in self.args]) for fun in self.fun])

class SSymbol:
    def __init__(self, sym):
        self.sym = sym

    def analyze(self, context):
        return context[self.sym]


class SIf:
    def __init__(self, condexpr, thenexpr, elseexpr):
        self.condexpr = condexpr
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def analyze(self, context):
        p = Poss()
        for poss in self.condexpr.analyze(context.nest()):
            assert isBool(poss)

            p.extend((thenexpr if poss.exact else elseexpr).
                     analyze(context.nest()))
        return p

#-----

def exact(xs):
    return all(x.exact is not None for x in xs)

def isBool(x):
    return x.__class__ == DataBool

def isNumber(x):
    return x.__class__ == DataInt

def alwaysNumber(poss):
    return all(isNumber(p) for p in poss)

def real(*args):
    return all(x.exact is not None for x in args)

class OpEq(SFunction): #Numeric Eq for now
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all(alwaysNumber(x) for x in args)

        p = Poss()
        for x in args[0]:
            for y in args[1]:
                if real(x.min, x.max, y.min, y.max) and \
                        x.min == x.max == y.min == y.max:
                    p.add(DataBool(True))
                elif (real(x.min, y.max) and x.min > y.max) or \
                        (real(x.max, y.min) and x.max < y.min):
                    p.add(DataBool(False))
                else:
                    p.add(DataBool(True, conds=[('==', x, y)]))
                    p.add(DataBool(False, conds=[('!=', x, y)]))

class OpGreater(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all(alwaysNumber(x) for x in args)

        p = Poss()
        for x in args[0]:
            for y in args[1]:
                if real(x.min, y.max) and x.min > y.max:
                    p.add(DataBool(True))
                elif real(x.max, y.min) and x.max <= y.min:
                    p.add(DataBool(False))
                else:
                    p.add(DataBool(True, conds=[('>', x, y)]))
                    p.add(DataBool(False, conds=[('<=', x, y)]))
        return p

class OpPlus(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all(alwaysNumber(x) for x in args)

        p = Poss()
        for x in args[0]:
            for y in args[1]:
                d = DataInt()
                if real(x.min, y.min):
                    d.min = x.min + y.min
                if real(x.max, y.max):
                    d.max = x.max + y.max
                if real(d.min, d.max):
                    if d.min == d.max:
                        d.exact = d.min
                else:
                    d.constraints = set([('+', x, y)])
                p.add(d)
        return p

class OpMinus(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all(alwaysNumber(x) for x in args)

        p = Poss()
        for x in args[0]:
            for y in args[1]:
                d = DataInt()
                if real(x.max, y.min):
                    d.max = x.max - y.min
                if real(x.min, y.max):
                    d.min = x.min - y.max
                if real(d.min, d.max):
                    if d.min == d.max:
                        d.exact = d.min
                else:
                    d.constraints = set([('-', x, y)])
                p.add(d)
        return p

class OpMul(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all(alwaysNumber(x) for x in args)

        p = Poss()
        for x in args[0]:
            for y in args[1]:
                d = DataInt()
                vals = []
                for x1 in (x.min, x.max):
                    if not real(x1): continue
                    for y1 in (y.min, y.max):
                        if real(y1):
                            vals.append(x1 * y1)

                if len(vals) == 4:
                    d.min = min(vals)
                    d.max = max(vals)

                if real(d.min, d.max):
                    if d.min == d.max:
                        d.exact = d.min
                else:
                    d.constraints = set([('*', x, y)])
                p.add(d)
        return p


#---

class DataBool:
    def __init__(self, exact=None, conds=None):
        self.exact = exact
        self.conds = conds

    def analyze(self, context):
        return Poss(self)

class DataInt:
    def __init__(self, exact=None, min=None, max=None, constraints=None):
        self.exact = exact
        self.constraints = constraints
        if exact is not None:
            self.min = self.max = exact
        else:
            self.min = min
            self.max = max

    def analyze(self, context):
        return Poss(self)
