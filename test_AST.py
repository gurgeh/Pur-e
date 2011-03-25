#nosetests --with-coverage --cover-erase --cover-package=AST,context,test_AST --cover-tests test_AST.py

from nose.tools import assert_equal, assert_raises, assert_true, eq_

from AST import *
import AST

def run(code, expect):
    AST.LIVE = False
    code.resolve(Context())
    AST.LIVE = True
    eq_(code.interpret().value, expect)

class TestAST:
    def setup(self):
        pass

    def testLiteral(self):
        code = Literal('5')
        run(code, 5)

    def testSimpleLet(self):
        code = Let([('seven', Literal('7'))], Symbol('seven'))
        run(code, 7)

    def testIf(self):
        code = If(Literal('True'), Literal('1'), Literal('2'))
        run(code, 1)

        code = If(Literal('False'), Literal('1'), Literal('2'))
        run(code, 2)

    def testOps(self):
        code = Call(OpPlus(), [Literal('1'), Literal('2')])
        run(code, 3)

        code = Call(OpPlus(), [Call(OpMul(), [Literal('10'), Literal('5')]), Call(OpMinus(), [Literal('6'), Literal('2')])])
        run(code, 54)

        code = If(Call(OpGreater(), [Literal('10'), Literal('5')]), Literal('1'), Literal('2'))
        run(code, 1)

        code = If(Call(OpGreater(), [Literal('10'), Literal('50')]), Literal('1'), Literal('2'))
        run(code, 2)

    def testFunction(self):
        code = Let([('fun', Function(['a', 'b'], Call(OpMinus(), [Symbol('a'), Symbol('b')])))], Call(Symbol('fun'), [Literal('11'), Literal('7')]))
        run(code, 4)

    def testRecursiveFunction(self):
        code = Let([('fun', Function(['n'], 
                                     If(Call(OpGreater(), [Symbol('n'), Literal('1')]), 
                                        Call(OpMul(), [Symbol('n'), Call(Symbol('fun'), [Call(OpMinus(), [Symbol('n'), Literal('1')])])]),
                                        Literal('1'))))], Call(Symbol('fun'), [Literal('10')]))
        run(code, 10*9*8*7*6*5*4*3*2)

    def testMutualRecursion(self):
        code = Let([('even', Function(['n'], 
                                     If(Call(OpEq(), [Symbol('n'), Literal('0')]),
                                        Literal('True'),
                                        Call(Symbol('odd'), [Call(OpMinus(), [Symbol('n'), Literal('1')])])))),
                    ('odd', Function(['n'], 
                                     If(Call(OpEq(), [Symbol('n'), Literal('1')]),
                                        Literal('True'),
                                        Call(Symbol('even'), [Call(OpMinus(), [Symbol('n'), Literal('1')])]))))], Call(Symbol('odd'), [Literal('13')]))
        run(code, True)

    def testObject(self):
        code = Lookup(Object(Literal('0'), [('a', Literal('7'))]), 'a')
        run(code, 7)

    def testInheritance(self):
        pass

    def testMutuallyRecursiveObject(self):
        pass
