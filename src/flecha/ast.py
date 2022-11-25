from enum import Enum
import json
from typing import Sequence

NodeOutput = int | str | Sequence['NodeOutput']

jsonConfig = dict(separators=(',', ':'),default=lambda x:x.value)

# region Clases base AST

class Tags(Enum):
    Program="Program"
    Definition="Def"
    ExprVar="ExprVar"
    ExprNumber="ExprNumber"
    ExprChar="ExprChar"
    ExprLambda="ExprLambda"
    ExprApply="ExprApply"
    ExprLet="ExprLet"
    ExprCase="ExprCase"
    CaseBranch="CaseBranch"
    ExprConstructor = "ExprConstructor"


class BinaryOperators(Enum):
    OR="OR"
    AND="AND"
    EQ="EQ"
    NE="NE"
    GE="GE"
    LE="LE"
    GT="GT"
    LT="LT"
    ADD="ADD"
    SUB="SUB"
    MUL="MUL"
    DIV="DIV"
    MOD="MOD"

class UnaryOperators(Enum):
    NOT = "NOT"
    UMINUS ="UMINUS"

binary_operators = {
    "||": BinaryOperators.OR.value,
    "&&": BinaryOperators.AND.value,
    "==": BinaryOperators.EQ.value,
    "!=": BinaryOperators.NE.value,
    ">=": BinaryOperators.GE.value,
    "<=": BinaryOperators.LE.value,
    ">": BinaryOperators.GT.value,
    "<": BinaryOperators.LT.value,
    "+": BinaryOperators.ADD.value,
    "-": BinaryOperators.SUB.value,
    "*": BinaryOperators.MUL.value,
    "/": BinaryOperators.DIV.value,
    "%": BinaryOperators.MOD.value,
}
unary_operators = {
    "!": UnaryOperators.NOT.value,
    "-": UnaryOperators.UMINUS.value,
}


class AstNode():
    ''' Representa un nodo del AST'''

    def __init__(self, tag:Tags, children):
        self.tag: Tags = tag
        self.children: list['AstNode'] = children

    def appendChild(self, child: 'AstNode') -> 'AstNode':
        self.children.append(child)
        return self

    def _childrenOutput(self) -> list[NodeOutput]:
        return [x._output() for x in self.children]

    def _output(self) -> NodeOutput:
        return [self.tag] + self._childrenOutput()

    def __repr__(self) -> str:
        return json.dumps(self._output(), **jsonConfig)

    def __eq__(self, __o: object) -> bool:
        return __o.__repr__() == self.__repr__()


class AstNodeCollection(AstNode):
    ''' Representa un nodo del AST que contiene una cantidad >=0 de nodos hijos y cuya representación no contiene un tag'''

    def __init__(self, name: str, nodes: Sequence[AstNode]):
        AstNode.__init__(self, name, nodes)

    def _output(self) -> NodeOutput:
        return self._childrenOutput() if self.children else []


class AstLeaf(AstNode):
    '''Representa una hoja del AST'''

    def __init__(self, name: str, value):
        AstNode.__init__(self, name, None)
        self.value = value

    def _output(self) -> NodeOutput:
        return self.value

# endregion


class Id(AstLeaf):
    def __init__(self, value: str):
        AstLeaf.__init__(self, 'Id', value)

# region Literales

class ExprLiteral(AstLeaf):
    def __init__(self, name, value):
        AstLeaf.__init__(self, name, value)

    def _output(self):
        return [self.tag, self.value]

class ExprNumber(ExprLiteral):
    def __init__(self, value: int):
        ExprLiteral.__init__(self, Tags.ExprNumber, value)


class ExprChar(ExprLiteral):
    def __init__(self, char: str):
        ExprLiteral.__init__(self, Tags.ExprChar, ord(char))


# endregion


class ExprVar(AstNode):
    def __init__(self, id: str):
        AstNode.__init__(self, Tags.ExprVar, [Id(id)])

    def id(self):
        return self.children[0].value


class ExprConstructor(AstNode):
    def __init__(self, id: str):
        AstNode.__init__(self, Tags.ExprConstructor, [Id(id)])
    
    def id(self):
        return self.children[0].value


class ExprCase(AstNode):
    def __init__(self, expr: 'Expression', branches: 'CaseBranches'):
        AstNode.__init__(self, Tags.ExprCase, [expr] + branches.children)
        
    def expr(self):
        return self.children[0]

    def _output(self):
        return [self.tag, self.expr()._output(),[c._output() for c in self.children[1:]]]
       
    def branches(self):
        return self.children[1:]

class CaseBranch(AstNode):
    def __init__(self, id: str, params: Sequence[str], expr: 'Expression'):
        _params = [Id(p) for p in params]
        AstNode.__init__(self, Tags.CaseBranch, [
                         Id(id), CaseBranchParams(_params), expr])

    def id(self):
        return self.children[0].value
    
    def params(self) -> list[str]:
        return [ p.value for p in self.children[1].children ]

    def expr(self):
        return self.children[2]


class CaseBranches(AstNodeCollection):
    def __init__(self, branches: Sequence[CaseBranch]):
        AstNodeCollection.__init__(self, None, branches)

    def append(self, branch: CaseBranch):
        return self.appendChild(branch)


class CaseBranchParams(AstNodeCollection):
    def __init__(self, params: Sequence[Id]):
        AstNodeCollection.__init__(self, None, params)


n: Sequence[AstNode] = [AstLeaf('', 1)]


class ExprLet(AstNode):
    def __init__(self, id: str, letExpr: 'Expression', inExpr: 'Expression'):
        AstNode.__init__(self, Tags.ExprLet, [Id(id), letExpr, inExpr])

    def param(self):
        return self.children[0].value

    def argExpr(self):
        return self.children[1]
    
    def inExpr(self):
        return self.children[2]


class ExprLambda(AstNode):
    def __init__(self, id: str, expr: 'Expression'):
        AstNode.__init__(self, Tags.ExprLambda, [Id(id), expr])
    
    def param(self):
        return self.children[0].value

    def body(self):
        return self.children[1]


class ExprApply(AstNode):
    def __init__(self, fn: 'Expression', arg: 'Expression'):
        AstNode.__init__(self, Tags.ExprApply, [fn, arg])

    def fn(self):
        return self.children[0]

    def arg(self):
        return self.children[1]


Expression = ExprNumber | ExprApply | ExprCase | ExprChar | ExprConstructor | ExprLambda | ExprLet | ExprVar

def build_binary_expression(expr1: Expression, op:str, expr2: Expression):
    return ExprApply(ExprApply(ExprVar(binary_operators[op]),expr1), expr2)

def build_unary_expression(op:str, expr: Expression):
    return ExprApply(ExprVar(unary_operators[op]),expr)

def build_lambda(params: list[str], exp: Expression) -> Expression:
    return ExprLambda(params[0], build_lambda(params[1:], exp)) if params else exp


def build_if(exp: any, t_exp: any, f_exp: any):
    return ExprCase(exp, CaseBranches([CaseBranch('True', [], t_exp), f_exp]))


def build_string(txt) -> Expression:
    return ExprApply(ExprApply(ExprConstructor('Cons'), ExprChar(txt[0])), build_string(txt[1:])) if txt else ExprConstructor('Nil')


class Definition(AstNode):
    def __init__(self, id: str, expr: Expression):
        AstNode.__init__(self, Tags.Definition, [Id(id), expr])

    def id(self):
        return self.children[0].value
    
    def expr(self):
        return self.children[1]


class Program(AstNodeCollection):
    def __init__(self, *args: Definition):
        AstNode.__init__(self, Tags.Program, [args[0]] if args else [])

    def append(self, definition: Definition):
        AstNode.appendChild(self, definition)
        return self

    def definitions(self):
        return self.children
