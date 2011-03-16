"""
Context
.
Interpret
  Core
  Build context
  Add + * >
.
Add tail recursion
.
Static interpret (just type check, incl. arity)
.
Lists (or some container anyway)
.

"""

class Call:
    def __init__(self, fun, arguments):
        self.fun = fun
        self.arguments = arguments

    def resolve(self, context):
        for expr in arguments:
            expr.resolve(context.nest())

class Symbol:
    def __init__(self, name):
        self.name = name

    def resolve(self, context):
        self.ref = context[self.name]

class Literal:
    def __init__(self, s):
        self.s = eval(s)

    def resolve(self, context):
        pass

class Let:
    def __init__(self, bindings, inexpr):
        self.bindings = bindings
        self.inexpr = inexpr

    def resolve(self, context):
        for name, expr in self.bindings:
            if expr.__class__ in RECURSIVES:
                context[name] = expr

        for _, expr in self.bindings:
            expr.resolve(context.nest())

        return self.inexpr.resolve(context.nest())

class FunArg:
    pass #enough for now

class Function:
    def __init__(self, names, expression):
        self.names = names
        self.expression = expression

    def resolve(self, context):
        for name in self.names:
            arg = FunArg()
            self.values[name] = arg
            context[name] = arg
        
        self.expression.resolve(context)

class Lookup:
    def __init__(self, instance, key):
        self.instance = instance
        self.key = key

    def resolve(self, context):
        self.instance.resolve(context)

class Instance:
    def __init__(self, cls, arguments):
        self.cls = cls
        self.arguments = arguments

    def resolve(self, context):
        self.cls.resolve()

        for expr in arguments:
            expr.resolve(context.nest())

class Class:
    def __init__(self, constructor, bindings):
        self.constructor = constructor
        self.bindings = bindings

    def resolve(self, context):
        for name, expr in self.bindings:
            if expr.__class__ in RECURSIVES:
                context[name] = expr

        for _, expr in self.bindings:
            expr.resolve(context.nest())

class If:
    def __init__(self, ifexpr, thenexpr, elseexpr):
        self.ifexpr = ifexpr
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def resolve(self, context):
        self.ifexpr.resolve()
        self.thenexpr.resolve()
        self.elseexpr.resolve()

RECURSIVES = {Class, Function}
