import pytest
from flecha.ast import *
import os
import glob
from flecha.interpreter import IntValue, Interpreter, LocalEnv, StructValue, Value
from flecha.parser import Parser

class FakeOutput():
    def __init__(self):
        self._buffer = ''

    def write(self, str:str):
        self._buffer += str

    def read(self) -> str:
        return self._buffer

@pytest.mark.parametrize('n',[str.rjust(str(n), 2, '0') for n in range(1,32)])
def test_eval_example_(n):__test_example_file(n)

def read_file(filename):
    with open(os.path.join(os.getcwd(), filename), 'r') as fi:
        return fi.read()

def read_expected_file(filename) -> str:
    return read_file(filename[0:-2]+'expected')

def __test_example_file(n):
    filename = glob.glob(
        os.getcwd() + f'/**/test{n}.fl', recursive=True)[0]
    input, expected = read_file(filename), read_expected_file(filename)
    out = FakeOutput()
    Interpreter(out).eval(Parser().parse(input),LocalEnv())
    assert out.read() == expected

def test_match_extends_env_ok():
    env = LocalEnv()
    cons_id = 'Cons'
    num = 1
    cons_expr = ExprConstructor(cons_id)
    head_expr = ExprNumber(num)
    tail_expr = ExprConstructor('Nil')
    expr = ExprApply(ExprApply(cons_expr,head_expr),tail_expr)
    interpreter = Interpreter(FakeOutput())
    struct = StructValue(cons_id,[IntValue(num),StructValue('Nil',[])])
    pattern = CaseBranch(cons_id,['x','xs'],expr)
    is_match, new_env = interpreter.match(struct,pattern,env)
    assert is_match
    x:IntValue = new_env.lookup("x")
    xs:StructValue = new_env.lookup("xs")
    assert isinstance(x,IntValue) and x.value==num
    assert isinstance(xs,StructValue) and xs.ctor=="Nil"