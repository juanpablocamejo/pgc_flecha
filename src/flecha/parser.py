from ply.yacc import yacc
from flecha.lexer import Lexer
from flecha.ast import *


class Parser():
    tokens = Lexer.tokens

    def __init__(self):
        self.__lex = Lexer().build()
        self.__yacc = yacc(module=self)

    precedence = (
        ('left', 'SEMICOLON'),
        ('left', 'IF', 'CASE', 'LET', 'LAMBDA'),
        ('left', 'THEN', 'ELSE', 'ELIF'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('nonassoc', 'EQ', 'NE', 'GE', 'LE', 'GT', 'LT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES'),
        ('left', 'DIV', 'MOD'),
        ('right', 'UMINUS'),
    )

    def p_program_empty(self, p):
        '''program :'''
        p[0] = Program()

    def p_program(self, p):
        '''program : program definition'''
        prog: Program = p[1]
        p[0] = prog.append((p[2]))

    def p_def(self, p):
        '''definition : DEF LOWERID parameters DEFEQ expression'''
        p[0] = Definition(p[2], build_lambda(p[3], p[5]))

    def p_parameters_empty(self, p):
        '''parameters :'''
        p[0] = []

    def p_parameters(self, p):
        '''parameters :  parameters LOWERID'''
        p[0] = p[1] + [p[2]]

    def p_expression_outerExpression(self, p):
        """ expression : outerExpression
                       | secuenceExpression """
        p[0] = p[1]

    def p_sequence_expression(self, p):
        '''secuenceExpression : outerExpression SEMICOLON expression'''
        p[0] = ExprLet('_', p[1], p[3])

    def p_outerExpression(self, p):
        '''outerExpression :  ifExpression
                            | letExpression
                            | lambdaExpression
                            | caseExpression
                            | innerExpression
        '''
        p[0] = p[1]

    def p_ifExpression(self, p):
        '''ifExpression : IF innerExpression THEN innerExpression elseBranches'''
        p[0] = build_if(p[2], p[4], p[5])

    def p_elseBranches_elif(self, p):
        '''elseBranches : ELIF innerExpression THEN innerExpression elseBranches'''
        p[0] = CaseBranch('False', [], build_if(p[2], p[4], p[5]))

    def p_elseBranches_else(self, p):
        '''elseBranches : ELSE innerExpression'''
        p[0] = CaseBranch('False', [], p[2])

    def p_caseExpression(self, p):
        '''caseExpression : CASE innerExpression caseBranches'''
        p[0] = ExprCase(p[2], p[3])

    def p_caseBranches_empty(self, p):
        '''caseBranches :'''
        p[0] = CaseBranches([])

    def p_caseBranches_caseBranch(self, p):
        '''caseBranches : caseBranches caseBranch'''
        p[0] = p[1].append(p[2])

    def p_caseBranch(self, p):
        '''caseBranch : PIPE UPPERID parameters ARROW innerExpression'''
        p[0] = CaseBranch(p[2], p[3], p[5])

    def p_letExpression(self, p):
        '''letExpression : LET LOWERID parameters DEFEQ innerExpression IN outerExpression'''
        p[0] = ExprLet(p[2], build_lambda(p[3], p[5]), p[7])

    def p_lambdaExpression(self, p):
        '''lambdaExpression : LAMBDA parameters ARROW outerExpression'''
        p[0] = build_lambda(p[2], p[4])

    def p_innerExpression(self, p):
        '''innerExpression : applyExpression
                           | binaryExpression
                           | unaryExpression'''
        p[0] = p[1]

    def p_unaryOperation(self, p):
        '''unaryExpression : NOT innerExpression
                           | MINUS innerExpression %prec UMINUS'''
        for key in unary_operators.keys():
            if p[1] == key:
                p[0] = build_unary_expression(p[1], p[2])
                break

    def p_binaryExpression(self, p):
        ''' binaryExpression : innerExpression AND innerExpression
                             | innerExpression OR innerExpression
                             | innerExpression EQ innerExpression
                             | innerExpression NE innerExpression
                             | innerExpression GE innerExpression
                             | innerExpression LE innerExpression
                             | innerExpression GT innerExpression
                             | innerExpression LT innerExpression
                             | innerExpression PLUS innerExpression
                             | innerExpression MINUS innerExpression
                             | innerExpression TIMES innerExpression
                             | innerExpression DIV innerExpression
                             | innerExpression MOD innerExpression'''
        for key in binary_operators.keys():
            if p[2] == key:
                p[0] = build_binary_expression(p[1], p[2], p[3])
                break

    def p_applyExpression_atomic(self, p):
        '''applyExpression : atomicExpression'''
        p[0] = p[1]

    def p_applyExpression(self, p):
        '''applyExpression : applyExpression atomicExpression'''
        p[0] = ExprApply(p[1], p[2])

    def p_atomicExpression_lowerid(self, p):
        '''atomicExpression : LOWERID'''
        p[0] = ExprVar(p[1])

    def p_atomicExpression_upperid(self, p):
        '''atomicExpression : UPPERID'''
        p[0] = ExprConstructor(p[1])

    def p_atomicExpression_number(self, p):
        '''atomicExpression : NUMBER'''
        p[0] = ExprNumber(p[1])

    def p_atomicExpression_char(self, p):
        '''atomicExpression : CHAR'''
        p[0] = ExprChar(p[1])

    def p_atomicExpression_string(self, p):
        '''atomicExpression : STRING'''
        p[0] = build_string(p[1])

    def p_atomicExpression_parenthesis(self, p):
        '''atomicExpression : LPAREN expression RPAREN'''
        p[0] = p[2]

    def p_error(self, p):
        print(f'Syntax error at {p.value!r} | line: {p.lineno}')

    def parse(self, input):
        ast = self.__yacc.parse(input, lexer=self.__lex)
        return f'{ast}'
