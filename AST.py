from context import Context

"""
Interpret
  Core
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
        for expr in self.arguments:
            expr.resolve(context.nest())

    def interpret(self):
        pass

class Symbol:
    def __init__(self, name):
        self.name = name

    def resolve(self, context):
        self.ref = context[self.name]

    def interpret(self):
        self.value = maybeResolve(self.ref).value
        return self.value

class Literal:
    def __init__(self, s):
        self.value = eval(s)

    def resolve(self, context):
        pass

    def interpret(self):
        return self.s

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
    pass #enough for now

class Function:
    def __init__(self, names, expression):
        self.names = names
        self.expression = expression
        self.values = {}

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
        self.cls.resolve(context)

        for expr in self.arguments:
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
        self.ifexpr.resolve(context)
        self.thenexpr.resolve(context)
        self.elseexpr.resolve(context)

RECURSIVES = {Class, Function}