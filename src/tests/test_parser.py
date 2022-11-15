from flecha.ast import *
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


def testExample_01_vacio():
    __testExampleFile(1)


def testExample_02_numeros():
    __testExampleFile(2)


def testExample_03_variables():
    __testExampleFile(3)

def testExample_04_constructores():
    __testExampleFile(4)

def testExample_05_caracteres():
    __testExampleFile(5)

def testExample_06_strings():
    __testExampleFile(6)

def testExample_07_if():
    __testExampleFile(7)

def testExample_08_case():
    __testExampleFile(8)

def testExample_09_applicacion():
    __testExampleFile(9)

def testExample_10_let():
    __testExampleFile(10)

def testExample_11_lambdas():
    __testExampleFile(11)

def testExample_12_secuenciacion():
    __testExampleFile(12)

def testExample_13_anidamiento_est_ctrl():
    __testExampleFile(13)

def testExample_14_operadores():
    __testExampleFile(14)

def testExample_15_asociatividad():
    __testExampleFile(15)

def testExample_16_anidamiento_oper_ap():
    __testExampleFile(16)

def testExample_17_precedencia():
    __testExampleFile(17)

def testExample_18_otros():
    __testExampleFile(18)


def __testExampleFile(file_number):
    p = Parser()
    f_num = str.rjust(str(file_number), 2, '0')
    filename = glob.glob(
        os.getcwd() + f'/**/test{f_num}.input', recursive=True)[0]
    input, expected = getInput(filename), getExpected(filename)
    assert p.parse(input) == expected
