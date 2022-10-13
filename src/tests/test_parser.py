from flecha.ast import Definition, ExprLambda, ExprNumber, Expression, Program, curry, jsonConfig
import os
import glob
import json

from flecha.parser import Parser

def testParser():
    p = Parser()
    testData = [
        ('',Program()),
        ('def a = 1', Program(Definition('a',ExprNumber(1)))),
        ('def a b = 1', Program(Definition('a',ExprLambda('b',ExprNumber(1)))))
    ]
    for t in testData:
        actual, expected = p.parse(t[0]),f'{t[1]}'
        assert actual == expected


def getExpected(filename) -> str:
    with open(os.path.join(os.getcwd(), filename[0:-5]+'expected'), 'r') as fe:
        return json.dumps(json.loads(fe.read()), **jsonConfig)


def getInput(filename) -> str:
    with open(os.path.join(os.getcwd(), filename), 'r') as fi:
        return fi.read()


def testExample_01():
    __testExampleFile(1)


def testExample_02():
    __testExampleFile(2)


def testExample_03():
    __testExampleFile(3)


def testExample_04():
    __testExampleFile(4)

# def testExample_05():
#     __testExampleFile(5)


# def testExample_06():
#     __testExampleFile(6)


# def testExample_07():
#     __testExampleFile(7)


# def testExample_08():
#     __testExampleFile(8)


def __testExampleFile(file_number):
    p = Parser()
    f_num = str.rjust(str(file_number), 2, '0')
    filename = glob.glob(
        os.getcwd() + f'/**/test{f_num}.input', recursive=True)[0]
    input, expected = getInput(filename), getExpected(filename)
    assert p.parse(input) == expected
