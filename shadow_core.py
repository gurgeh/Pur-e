from possibilities import Poss
from generalizer import Generalizer


"""

(2)
design class system and the rest in generalizer
  solved with "generalized lets"?
  continuations?
  context + code blocks?
P

(3)
solve implementation issues in generalizer
start cleanup, refactoring, implementation

(4)
more CRI

(5)
finish CRI
 (incl. everything class based, containers, conds and constrs, etc)

--
.
uniqueness typing
.
set definite name
blog post

-- release factsite, while thinking through stuff below.

think through:
  currying? (probably just syntactic sugar for wrapper function)
  generators?
  continuations?
  exceptions?
  optional lazy arguments (like if and or)?
  macros
  module system
  polymorphism
  communication with shadow (promise, must, custom shadow, etc)
  syntax

implement the above in shadow

implement some missing core:
  List
  Array/Vector (list enough for now?)
  Map (associative list?)
  DataString
  string operations
  DataFloat
  more integer and float operations
  missing bool operations
  file I/O
  arguments in

interpreter
do simple parser and blog post and we are ready for others to test

--
priv/pub/prot objects
concurrency (multi core)
GC
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
        self.norecur = False
        self.recur_detected = False

    def analyze(self, context):
        self.funcontext = context
        return Poss(self)

    def callalyze(self, context, args):
        if self.norecur:
            self.recur_detected = True
            raise Recursion(self)
        assert len(args) == len(self.argnames)
        
        for name, expr in zip(self.argnames, args):
            context[name] = expr

        if self.expr:
            outer = False
            if not self.recur_detected:
                self.norecur = True #initial run without recursion
                try:
                    ret = self.expr.analyze(context.nest())
                    self.inprogress.poss_returns = ret
                except Recursion, fun:
                    self.norecur = False
                    if fun is self:
                        print 'Possible infinite recursion detected in', self
                    raise Recursion, fun
                self.norecur = False
                outer = True
            
            if self.recur_detected:
                if self.inprogress.has(args):
                    return self.inprogress.get(args)
                while True:
                    ret = self.expr.analyze(context.nest())
                    self.inprogress.set(args, ret)
                    if outer and not self.inprogress.poss_returns.contains(ret):
                        self.inprogress.poss_returns = ret
                    else:
                        break
            
            return ret
        
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

    def analyze(self, context):
        p = Poss()
        for poss in self.condexpr.analyze(context.nest()):
            assert isBool(poss)
            try:
                p.extend((self.thenexpr if poss.exact else self.elseexpr).
                         analyze(context.nest()))
            except Recursion, _:
                pass
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

    def analyze(self, _):
        return Poss(self)

    def contains(self, d):
        if self.exact is not None:
            return self.exact == d.exact
        if self.min > d.min: return False
        if self.max < d.max: return False
        return True

    def __repr__(self):
        if self.exact is not None:
            return 'Int(%s)%s' % (self.exact, checkC(self.constraints))
        return '%s <= Int <= %s%s' % (self.min, self.max, checkC(self.constraints))
