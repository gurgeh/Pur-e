from context import Context
from possibilities import Poss

"""

-- later
priv/pub/prot objects
concurrency (multi core)
GC
a backtracking version of if that can yield multiple values if there is a backtracking if "above"
 maybe like the (amb) operator in LISP
compilation (LLVM, I think)
advanced analytics
FFI
good error messages
standard library
inter-process communication analysis
GPGPU
cluster over machines
debugging
profiling
standard (enforced?) syntax conventions, capital letters, function names, etc

"""

class SExpression:
    def __init__(self, obj, member, *args):
        self.obj = obj
        self.member = member
        self.args = args

        assert type(self.member) == str

    def analyze(self, context):
        p = Poss()
        for obj in self.obj.analyze(context.nest()):
            for fun in obj[self.member].analyze(context.nest()):
                if fun.strict:
                    aargs = [arg.analyze(context.nest()) for arg in self.args]
                else:
                    aargs = self.args
                p.extend(fun.callalyze(context.nest(), aargs))
        return p

class SLet:
    def __init__(self, bindings, inexpr):
        self.bindings = bindings
        self.inexpr = inexpr

    def analyze(self, context):
        for name, expr in self.bindings:
            context[name] = expr

        for name, expr in self.bindings:
            context[name] = expr.analyze(context.nest())

        return self.inexpr.analyze(context.nest())

class SFunction(Context):
    def __init__(self, argnames, expr=None):
        self.argnames = argnames
        self.expr = expr
        self.funcontext = None
        self.strict = True
        Context.__init__(self)
        self['$'] = self

    def contains(self, fun):
        return self == fun

    def analyze(self, context):
        self.funcontext = context
        return Poss(self)

    def callalyze(self, context, args):
        assert len(args) == len(self.argnames)
        
        for name, expr in zip(self.argnames, args):
            context[name] = expr

        if self.expr:
            return self.expr.analyze(context.nest())

"""        
class SCall:
    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def analyze(self, context):
        p = Poss()
        for fun in self.fun.analyze(context.nest()):
            retvals = fun.callalyze(fun.funcontext.nest(), [x.analyze(context.nest()) for x in self.args])
            p.extend(retvals)
        return p
"""

class SSymbol:
    def __init__(self, sym):
        self.sym = sym

    def analyze(self, context):
        return context[self.sym]

class SGetContext:
    def analyze(self, context):
        return Poss(context.flatcopy()) #a copy should not be needed..







