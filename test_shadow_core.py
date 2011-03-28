
from nose.tools import assert_equal, assert_raises, assert_true, eq_

from shadow_core import *
from context import Context

EXP = {}
EXP['plus1'] = SCall(OpPlus(), [DataInt(5), DataInt(3)])
EXP['min1']  = SCall(OpMinus(), [SSymbol('a'), SCall(OpPlus(), [DataInt(3), SSymbol('b')])])
EXP['mul1']  = SCall(OpMul(), [DataInt(20), DataInt(10)])
EXP['cond1'] = SCall(OpGreater(), [DataInt(5), DataInt(7)])
EXP['cond2'] = SCall(OpGreater(), [EXP['plus1'], DataInt(7)])
EXP['cond3'] = SCall(OpGreater(), [DataInt(), DataInt(7)])
EXP['cond4'] = SCall(OpEq(), [DataInt(5), DataInt()])
EXP['if1']   = SIf(EXP['cond1'], EXP['plus1'], EXP['mul1'])
EXP['if2']   = SIf(EXP['cond2'], EXP['plus1'], EXP['mul1'])
EXP['if3']   = SIf(EXP['cond3'], EXP['plus1'], EXP['mul1'])
EXP['let1']  = SLet([('a', DataInt(11)), ('b', DataInt(5))], EXP['min1'])
EXP['let2']  = SLet([('a', DataInt(12)), ('b', DataInt(12))], SLet([('a', DataInt(21))], EXP['min1']))
EXP['fun1']  = SCall(SFunction(('a', 'b'), EXP['min1']), [DataInt(11), DataInt(13)])
EXP['fun2']  = SLet([('a', DataInt(30))],
                    SLet([('fun', SFunction(('b',), EXP['min1']))],
                         SLet([('a', DataInt(0)), ('b', DataInt(0))],
                              SCall(SSymbol('fun'), [DataInt(40)]))))

EXP['rfun1'] = SLet([('fac', SFunction(['n'], SIf(
        SCall(OpGreater(), [SSymbol('n'), DataInt(1)]),
        SCall(OpMul(), [SSymbol('n'), SCall(SSymbol('fac'),
                                            [SCall(OpMinus(), [SSymbol('n'), DataInt(1)])])]),
        DataInt(1))))],
                    SCall(SSymbol('fac'), [DataInt(10)]))

#two constant paramters (i.e infinite recursion)
#one constant parameter (bool) and one changing
#two changing parameters (int and bool)

#check rfun that returns something new in recur

class TestShadow:
    def setup(self):
        pass


