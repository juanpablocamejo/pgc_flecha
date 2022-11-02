import json
from typing import Any
from flecha.ast import *


def test_ast_base_classes():
    testData: list[tuple[AstNode, Any]] = [
        (AstNode("Label", []), ["Label"]),
        (AstLeaf("Leaf", 1), 1),
        (AstNodeCollection("Label", []), []),
        (AstNodeCollection("Label", [AstLeaf("num", 1)]), [1]),
        (ExprLiteral("ExprChar", 1), ["ExprChar", 1])]
    for data in testData:
        assert f'{data[0]}' == json.dumps(data[1], **jsonConfig)


def testAstSpecificClasses():
    testData: list[tuple[AstNode, Any]] = [
        (Program(),        []),
        (Definition('a', ExprNumber(1)), ["Def", "a", ["ExprNumber", 1]]),
        (ExprVar('v'), ["ExprVar", "v"]),
        (ExprConstructor('Mk'), ["ExprConstructor", "Mk"]),
        (ExprNumber(1), ["ExprNumber", 1]),
        (ExprChar(chr(22)), ["ExprChar", 22]),
        (ExprCase(ExprVar('ls'), [CaseBranch('Nil', [], ExprNumber(1))]),
         ["ExprCase", ["ExprVar", "ls"], [["CaseBranch", "Nil", [], ["ExprNumber", 1]]]]),
        (ExprLet('x', ExprVar('y'), ExprVar('z')),
         ["ExprLet", "x", ["ExprVar", "y"], ["ExprVar", "z"]]),
        (ExprLambda('f', ExprNumber(1)),
         ["ExprLambda", "f", ["ExprNumber", 1]]),
        (ExprApply(ExprVar("fn"), ExprNumber(1)),
         ["ExprApply", ["ExprVar", "fn"], ["ExprNumber", 1]])
    ]
    for data in testData:
        assert f'{data[0]}' == json.dumps(data[1], **jsonConfig)


def test_AstNode_equals():
    assert ExprNumber(1) == ExprNumber(1)
    assert ExprConstructor('Nil') != ExprConstructor('Cons')


def test_ExprStringBuild():
    testData = [
        (buildString(""), ExprConstructor('Nil')),
        (buildString("a"), ExprApply(ExprApply(ExprConstructor(
            "Cons"), ExprChar('a')), ExprConstructor("Nil"))),
        (buildString("abc"), ExprApply(
            ExprApply(ExprConstructor("Cons"), ExprChar('a')), 
            ExprApply(ExprApply(ExprConstructor("Cons"), ExprChar('b')), 
            ExprApply(ExprApply(ExprConstructor("Cons"), ExprChar('c')), 
            ExprConstructor('Nil'))))),
    ]
    for data in testData:
        assert data[0] == data[1]

def test_Curry():
   assert curry(['x','y'],ExprNumber(1)) == ExprLambda('x',ExprLambda('y',ExprNumber(1)))
   assert curry([],ExprNumber(1)) == ExprNumber(1)
