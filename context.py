from possibilities import Poss

class Context:
    def __init__(self, parent=None, params=None):
        if params is not None:
            self.local = params
        else:
            self.local = {}
        self.parent = parent

    def __getitem__(self, key):
        if key == 'in':
            return ExecInContext(self)
        if key in self.local: return self.local[key]
        else:
            if self.parent is None:
                raise KeyError, key
            return self.parent[key]

    def __setitem__(self, key, val):
        self.local[key] = val

    def analyze(self, context):
        #for key, val in self.local.items():
        #    self.local[key] = p.analyze(context.nest() for p in val)
        return Poss(self)

    def contains(self, context):
        for key, val in context.local.items():
            if key not in self.local:
                return False
            if not self.local[key].contains(val):
                return False
        return True

    def nest(self):
        return Context(self)

    def generalize(self, context2):
        for key, val in context2:
            if key in self.local:
                #Todo: if different basic datatypes generalize to Unknown type
                self.local[key].generalize(val)
            else:
                self.local[key] = val

    def flatcopy(self):
        retc = Context()
        self.flatcopyto(retc)
        return retc

    def flatcopyto(self, retc):
        for key, val in self.local.items():
            if key not in retc.local:
                retc.local[key] = val

        if self.parent is not None:
            self.parent.flatcopyto(retc)

class ExecInContext(Context):
    def __init__(self, mycontext):
        self.mycontext = mycontext
        self.strict = False
        Context(self)

    def analyze(self, _):
        return Poss(self)

    def callalyze(self, _, args):
        assert len(args) == 1

        p = Poss()
        for fun in args[0].analyze(self.mycontext.nest()):
            p.extend(fun.analyze(self.mycontext.nest()))
        return p

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
