"""


N
switch to generators
.
recursion
T
generalizer
.
class system
.
world object
.

"""


class SLet:
    def __init__(self, bindings, inexpr):
        self.bindings = bindings
        self.inexpr = inexpr

    def analyze(self, context):
        for name, expr in self.bindings:
            context[name] = expr

        for name, expr in self.bindings:
            expr.analyze(context.nest())

        for poss in self.inexpr.analyze(context.nest()):
            yield poss

class SFunction:
    def __init__(self, argnames, expr=None):
        self.argnames = argnames
        self.expr = expr

    def analyze(self, context):
        return [self]

    def callalyze(self, context, args):
        assert len(args) == len(self.argnames)
        
        for name, expr in zip(self.argnames, args):
            context[name] = expr

        if self.expr:
            yield self.expr.analyze(context.nest())
        

class SCall:
    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def analyze(self, context):
        for poss in self.fun.callalyze(context, [x.analyze(context.nest()) for x in self.args]):
            yield poss

class SSymbol:
    def __init__(self, sym):
        self.sym = sym

    def analyze(self, context):
        return [context[self.sym]]


class SIf:
    def __init__(self, condexpr, thenexpr, elseexpr):
        self.condexpr = condexpr
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def analyze(self, context):
        for poss in self.condexpr.analyze(context.nest()):
            assert isBool(poss)
            if poss.exact:
                for poss2 in thenexpr.analyze(context.nest()):
                    yield poss2
            else:
                for poss2 in elseexpr.analyze(context.nest()):
                    yield poss2
        

#-----

def exact(xs):
    return all(x.exact is not None for x in xs)

def isBool(x):
    return x.__class__ == DataBool

class OpEq(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all([isBool(x) for x in args])

        if exact(args):
            yield DataBool(args[0].exact == args[1].exact)
        else:
            #add knowledge here
            yield DataBool(False)
            yield DataBool(True)

class OpGreater(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all([isBool(x) for x in args])

        if exact(args):
            yield DataBool(args[0].exact > args[1].exact)
        else:
            #add knowledge here
            yield DataBool(False)
            yield DataBool(True)

def isNumber(x):
    return x.__class__ == DataInt

class OpPlus(SFunction): #switch these to ranges
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all([isNumber(x) for x in args])

        if exact(args):
            return DataInt(args[0].exact + args[1].exact)
        
        return DataInt()

class OpMinus(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all([isNumber(x) for x in args])

        if exact(args):
            return DataInt(args[0].exact - args[1].exact)
        
        return DataInt()

class OpMul(SFunction):
    def __init__(self):
        SFunction.__init__(self, ('x', 'y'))

    def callalyze(self, context, args):
        SFunction.callalyze(self, context, args)

        assert all([isNumber(x) for x in args])

        if exact(args):
            return DataInt(args[0].exact * args[1].exact)
        
        return DataInt()

#---

class DataBool:
    def __init__(self, exact=None):
        self.exact = exact

    def analyze(self, context):
        yield self

class DataInt:
    def __init__(self, exact=None, min=None, max=None):
        self.exact = exact
        self.min = min
        self.max = max

    def analyze(self, context):
        yield self
