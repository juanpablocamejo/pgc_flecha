import pytest
from flecha.ast import *
import os
import glob
from flecha.interpreter import FakeOutput, Interpreter, LocalEnv
from flecha.parser import Parser


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
