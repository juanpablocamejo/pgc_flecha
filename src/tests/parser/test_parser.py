import pytest
from flecha.ast import *
import os
import glob
import json

from flecha.parser import Parser

def test_parser():
    p = Parser()
    testData = [
        ('',Program()),
        ('def a = 1', Program(Definition('a',ExprNumber(1)))),
        ('def a b = 1', Program(Definition('a',ExprLambda('b',ExprNumber(1)))))
    ]
    for t in testData:
        actual, expected = f'{p.parse(t[0])}',f'{t[1]}'
        assert actual == expected


test_examples = [
('vacio'),
('numeros'),
('variables'),
('constructores'),
('caracteres'),
('caracteres'),
('strings'),
('if'),
('case'),
('applicacion'),
('let'),
('lambdas'),
('secuenciacion'),
('anidamiento_est_ctrl'),
('operadores'),
('asociatividad'),
('anidamiento_oper_ap'),
('precedencia'),
('otros')
]

@pytest.mark.parametrize('n, desc', [(str.rjust(str(i), 2, '0'),e) for i,e in enumerate(test_examples)])
def test_parse_example_(n,desc):
    __testExampleFile(n)

def getInput(filename) -> str:
    with open(os.path.join(os.getcwd(), filename), 'r') as fi:
        return fi.read()

def getExpected(filename) -> str:
    with open(os.path.join(os.getcwd(), filename[0:-5]+'expected'), 'r') as fe:
        return json.dumps(json.loads(fe.read()), **jsonConfig)

def __testExampleFile(file_number):
    p = Parser()
    filename = glob.glob(
        os.getcwd() + f'/**/test{file_number}.input', recursive=True)[0]
    input, expected = getInput(filename), getExpected(filename)
    assert f'{p.parse(input)}' == expected
