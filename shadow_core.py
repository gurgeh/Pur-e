from context import Context
from possibilities import Poss
from generalizer import Generalizer


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

class Recursion(Exception):
    pass

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

class SFunction:
    def __init__(self, argnames, expr=None):
        self.argnames = argnames
        self.expr = expr
        self.inprogress = Generalizer()
        self.funcontext = None

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
        self.tryreturn = {True:None, False:None}
        self.triedreturn = {True:False, False:False}
        self.lock = {True:[], False:[]}

    def islocked(self, context, cond):
        for source in self.lock[cond]:
            if source.contains(context):
                return True
        return False

    def analyze(self, context):
        p = Poss()
        thiscontext = context.flatcopy()
        for poss in self.condexpr.analyze(context.nest()):
            assert isBool(poss)
            if self.islocked(thiscontext, poss.exact): #bug what if several true returns from condexpr?
                print 'locked context', thiscontext.local, poss.exact, self.tryreturn[poss.exact]
                self.triedreturn[poss.exact] = True
                if self.tryreturn[poss.exact] is not None:
                    p.extend(self.tryreturn[poss.exact])
            else:
                self.lock[poss.exact].append(thiscontext)
                while True:
                    ret = (self.thenexpr if poss.exact else self.elseexpr).analyze(context.nest())
                    if self.triedreturn[poss.exact]:
                        tryret = self.tryreturn[poss.exact]
                        if tryret is None or not tryret.contains(ret):
                            self.tryreturn[poss.exact] = ret
                            continue
                    
                    p.extend(ret)
                    self.triedreturn[poss.exact] = False
                    self.tryreturn[poss.exact] = None
                    break
                self.lock[poss.exact].pop()
        return p

class SGetContext:
    def analyze(self, context):
        return Poss(context.flatcopy()) #a copy should not be needed..


class SInheritContext: #design and implement later
    def __init__(self, context, bindings):
        self.sourceContext = context
        self.bindings = bindings

    def analyze(self, context):
        self.sourceContext.analyze(context.nest()) #TODO: context.analyze
        
        for name, expr in self.bindings:
            context[name] = expr

        for name, expr in self.bindings:
            context[name] = expr.analyze(context.nest())

class SLookup:
    def __init__(self, context, name):
        self.mycontext = context
        self.name = name

    def analyze(self, context):
        p = Poss()
        for mycon in self.mycontext.analyze(context.nest()):
            assert mycon.__class__ == Context, 'class was %s' % mycon.__class__.__name__

            mycon.parent = context
            p.extend(mycon[self.name])
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
    return all(x is not None for x in args)

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

def checkC(cs):
    return '' if cs is None else ', when %s' % cs 

class DataBool:
    def __init__(self, exact=None, conds=None):
        self.exact = exact
        self.conds = conds

    def generalize(self, d):
        if real(self.exact) and self.exact == d.exact:
            return
        self.exact = None

    def analyze(self, _):
        return Poss(self)

    def contains(self, d):
        if self.exact is not None:
            return self.exact == d.exact
        return True

    def __repr__(self):
        return 'Bool(%s), %s' % (self.exact, self.conds)

class DataInt:
    def __init__(self, exact=None, min=None, max=None, constraints=None):
        self.exact = exact
        self.constraints = constraints
        if exact is not None:
            self.min = self.max = exact
        else:
            self.min = min
            self.max = max

    def generalize(self, d):
        if real(self.exact) and self.exact == d.exact:
            return
        if real(d.min, self.min):
            self.min = min(self.min, d.min)
        else:
            self.min = None

        if real(d.max, self.max):
            self.max = min(self.max, d.max)
        else:
            self.max = None

            

    def analyze(self, _):
        return Poss(self)

    def contains(self, d):
        if self.exact is not None:
            return self.exact == d.exact
        if real(self.min) and (self.min > d.min or d.min is None): return False
        if real(self.max) and (self.max < d.max or d.max is None): return False
        return True

    def __repr__(self):
        if self.exact is not None:
            return 'Int(%s)%s' % (self.exact, checkC(self.constraints))
        return '%s <= Int <= %s' % (self.min, self.max)
        #return '%s <= Int <= %s%s' % (self.min, self.max, checkC(self.constraints))
