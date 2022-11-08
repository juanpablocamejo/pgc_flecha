import json
from typing import Sequence

NodeOutput = int | str | Sequence['NodeOutput']

jsonConfig = dict(separators=(',', ':'))

# region Clases base AST

binary_operators = {
    "||": "OR",
    "&&": "AND",
    "==": "EQ",
    "!=": "NE",
    ">=": "GE",
    "<=": "LE",
    ">": "GT",
    "<": "LT",
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
    "%": "MOD",
}
unary_operators = {
    "!": "NOT",
    "-": "UMINUS",
}


class AstNode():
    ''' Representa un nodo del AST'''

    def __init__(self, name, children):
        self.name: str = name
        self.children: list['AstNode'] = children

    def appendChild(self, child: 'AstNode') -> 'AstNode':
        self.children.append(child)
        return self

    def _childrenOutput(self) -> list[NodeOutput]:
        return [x._output() for x in self.children]

    def _output(self) -> NodeOutput:
        return [self.name] + self._childrenOutput()

    def __repr__(self) -> str:
        return json.dumps(self._output(), **jsonConfig)

    def __eq__(self, __o: object) -> bool:
        return __o.__repr__() == self.__repr__()


class AstNodeCollection(AstNode):
    ''' Representa un nodo del AST que contiene una cantidad >=0 de nodos hijos y cuya representación no contiene un label'''

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
        return [self.name, self.value]


class ExprNumber(ExprLiteral):
    def __init__(self, value: int):
        ExprLiteral.__init__(self, 'ExprNumber', value)


class ExprChar(ExprLiteral):
    def __init__(self, char: str):
        ExprLiteral.__init__(self, 'ExprChar', ord(char))


# endregion


class ExprVar(AstNode):
    def __init__(self, id: str):
        AstNode.__init__(self, 'ExprVar', [Id(id)])


class ExprConstructor(AstNode):
    def __init__(self, id: str):
        AstNode.__init__(self, 'ExprConstructor', [Id(id)])


class ExprCase(AstNode):
    def __init__(self, expr: 'Expression', branches: 'CaseBranches'):
        AstNode.__init__(self, 'ExprCase', [expr] + branches.children)
        self.expr = expr
    
    def _output(self):
        return [self.name, self.expr._output(),[c._output() for c in self.children[1:]]]

class CaseBranch(AstNode):
    def __init__(self, id: str, params: Sequence[str], expr: 'Expression'):
        _params = [Id(p) for p in params]
        AstNode.__init__(self, 'CaseBranch', [
                         Id(id), CaseBranchParams(_params), expr])


class CaseBranches(AstNodeCollection):
    def __init__(self, branches: Sequence[CaseBranch]):
        AstNodeCollection.__init__(self, 'CaseBranches', branches)

    def append(self, branch: CaseBranch):
        return self.appendChild(branch)


class CaseBranchParams(AstNodeCollection):
    def __init__(self, params: Sequence[Id]):
        AstNodeCollection.__init__(self, 'CaseBranchParams', params)


n: Sequence[AstNode] = [AstLeaf('', 1)]


class ExprLet(AstNode):
    def __init__(self, id: str, letExpr: 'Expression', inExpr: 'Expression'):
        AstNode.__init__(self, 'ExprLet', [Id(id), letExpr, inExpr])


class ExprLambda(AstNode):
    def __init__(self, id: str, expr: 'Expression'):
        AstNode.__init__(self, 'ExprLambda', [Id(id), expr])


class ExprApply(AstNode):
    def __init__(self, fn: 'Expression', arg: 'Expression'):
        AstNode.__init__(self, 'ExprApply', [fn, arg])


Expression = ExprNumber | ExprApply | ExprCase | ExprChar | ExprConstructor | ExprLambda | ExprLet | ExprVar


def build_lambda(params: list[str], exp: Expression) -> Expression:
    return ExprLambda(params[0], build_lambda(params[1:], exp)) if params else exp


def build_if(exp: any, t_exp: any, f_exp: any):
    return ExprCase(exp, CaseBranches([CaseBranch('True', [], t_exp), f_exp]))


def build_string(txt) -> Expression:
    return ExprApply(ExprApply(ExprConstructor('Cons'), ExprChar(txt[0])), build_string(txt[1:])) if txt else ExprConstructor('Nil')


class Definition(AstNode):
    def __init__(self, id: str, expr: Expression):
        AstNode.__init__(self, 'Def', [Id(id), expr])


class Program(AstNodeCollection):
    def __init__(self, *args: Definition):
        AstNode.__init__(self, 'Program', [args[0]] if args else [])

    def append(self, definition: Definition):
        AstNode.appendChild(self, definition)
        return self
