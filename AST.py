from context import Context

"""
Construct unit tests
. (if bugs get complicated, maybe remove resolve step)
Static interpret (just type check, incl. arity)
.
Add tail recursion
.
Lists (or some container anyway)
.

"""

LIVE = False

class Call:
    def __init__(self, fun, arguments):
        self.fun = fun
        self.arguments = arguments

    def resolve(self, context):
        for expr in self.arguments:
            expr.resolve(context.nest())

    def interpret(self):
        self.value = self.fun.interpret().run([arg.interpret() for arg in self.arguments])
        return self.value

class Symbol:
    def __init__(self, name):
        self.name = name

    def resolve(self, context):
        self.ref = context[self.name]

    def interpret(self):
        self.value = self.ref.value
        return self.value

class Literal:
    def __init__(self, s):
        self.value = eval(s)

    def resolve(self, context):
        pass

    def interpret(self):
        return self.value

class Let:
    def __init__(self, bindings, inexpr):
        self.bindings = bindings
        self.inexpr = inexpr
        self.value = None

    def resolve(self, context):
        for name, expr in self.bindings:
            if expr.__class__ in RECURSIVES:
                context[name] = expr

        for _, expr in self.bindings:
            expr.resolve(context.nest())

        return self.inexpr.resolve(context.nest())

    def interpret(self):
        for _, expr in self.bindings:
            expr.interpret()

        self.value = self.inexpr.interpret()
        return self.value

class FunArg:
    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)
        self.value = val

    def pop(self):
        x = self.stack.pop()
        if self.stack:
            self.value = self.stack[-1]
        return x

class Function:
    def __init__(self, names, expression):
        self.names = names
        self.expression = expression
        self.values = {}
        self.value = self

    def resolve(self, context):
        for name in self.names:
            arg = FunArg()
            self.values[name] = arg
            context[name] = arg
        
        self.expression.resolve(context)

    def run(self, args):
        for i, name in enumerate(self.names):
            self.values[name].push(args[i])

        x = self.expression.interpret()

        for name in self.names:
            self.values[name].pop()

        return x

    def interpret(self):
        return self

class Op:
    def __init__(self):
        self.value = self

    def resolve(self, context):
        pass

    def interpret(self):
        return self

class OpPlus(Op):
    def run(self, args):
        return args[0].value + args[1].value
class OpMinus(Op):
    def run(self, args):
        return args[0].value - args[1].value
class OpMul(Op):
    def run(self, args):
        return args[0].value * args[1].value
class OpGreater(Op):
    def run(self, args):
        return args[0].value > args[1].value



class Lookup:
    def __init__(self, instance, key):
        self.instance = instance
        self.key = key

    def resolve(self, context):
        self.instance.resolve(context)

    def interpret(self):
        return self.instance.keys[self.key.interpret()]
            
class Object:
    def __init__(self, parent, bindings):
        self.parent = parent
        self.bindings = bindings
        self.keys = {}

    def resolve(self, context):
        if self.parent.__class__ != Literal: #FIXME: literals should be objects too
            self.parent.resolve(context)

        if LIVE:
            mycontext = context.nest()
            for name, expr in self.bindings:
                if expr.__class__ in RECURSIVES:
                    mycontext[name] = expr

            for _, expr in self.bindings:
                expr.resolve(mycontext.nest()) #FIXME: need to handle recursion?

    def interpret(self):
        self.resolve(Context())
        
        for name, expr in self.bindings:
            self.keys[name] = expr.interpret()

        self.value = self
        return self


class If:
    def __init__(self, ifexpr, thenexpr, elseexpr):
        self.ifexpr = ifexpr
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def resolve(self, context):
        self.ifexpr.resolve(context)
        self.thenexpr.resolve(context)
        self.elseexpr.resolve(context)

    def interpret(self):
        self.value = self.thenexpr.interpret() if self.ifexpr.interpret() else self.elseexpr.interpret()
        return self.value

RECURSIVES = {Object, Function}
