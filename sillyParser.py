from AST import *

class LET: pass
class IF: pass
class FUN: pass

COREOPS = {'+':OpPlus, '-':OpMinus, '*':OpMul, '>':OpGreater, '==':OpEq}

def parseList(l):
    head = l[0]
    if head in COMD:
        return COMD[head](l[1:])
    elif head in COREOPS:
        return Call(COREOPS[head](), parseAll(l[1:]))
    else:
        return Call(Symbol(head), parseAll(l[1:]))
        

def parse(x):
    if type(x) == list:
        return parseList(x)
    if x.startswith('_'):
        return Literal(x[1:])
    else:
        return Symbol(x)


def parseAll(l):
    return [parse(x) for x in l]

def let(l):
    bindings = [(sym, parse(expr)) for sym, expr in l[0]]
    expr = parse(l[1])
    return Let(bindings, expr)

def iff(l):
    return If(parse(l[0]), parse(l[1]), parse(l[2]))

def fun(l):
    names = l[0]
    expr = parse(l[1])
    return Function(names, expr)

COMD = {LET:let, IF:iff, FUN:fun}

def run(p):
    pp = parse(p)
    pp.resolve(Context())
    return pp.interpret().value
