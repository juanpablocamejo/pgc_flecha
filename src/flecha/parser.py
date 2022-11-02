from ply.yacc import yacc
from flecha.lexer import Lexer
from flecha.ast import *

# parser


class Parser():
    tokens = Lexer.tokens

    def __init__(self):
        self.__lex = Lexer().build()
        self.__yacc = yacc(module=self)

    def p_program_empty(self, p):
        '''program :'''
        p[0] = Program()

    def p_program(self, p):
        '''program : program definition'''
        prog : Program = p[1]
        p[0] = prog.append((p[2]))

    def p_def(self, p):
        '''definition : DEF LOWERID parameters DEFEQ expression'''
        p[0] = Definition(p[2], curry(p[3],p[5]))

    def p_parameters_empty(self, p):
        '''parameters :'''
        p[0] = []

    def p_parameters(self, p):
        '''parameters :  parameters LOWERID'''
        p[0] = p[1] + [p[2]]

    def p_expression_outerExpression(self, p):
        """ expression : outerExpression"""
        p[0] = p[1]

    # def p_sequence_expression(self, p):
    #     '''expression : expression SEMICOLON outerExpression'''
    #     p[0] = ExprLet('_', p[1], p[3])

    def p_outerExpression(self, p):
        '''outerExpression :  innerExpression '''
        p[0] = p[1]

                            #         |ifExpression
                            # | caseExpression
                            # | letExpression
                            # | lambdaExpression
                            # | 

    # def p_ifExpression(self, p):
    #     '''ifExpression : IF innerExpression THEN innerExpression elseBranches'''
    #     p[0] = ExprCase(p[2], [CaseBranch('True', [], p[4])].extend(p[5]))

    # def p_elseBranches_elif(self, p):
    #     '''elseBranches : ELIF innerExpression THEN innerExpression elseBranches'''
    #     p[0] = [CaseBranch('False', [], ExprCase(
    #         p[2], [CaseBranch('True', [], p[4])].extend(p[5])))]

    # def p_elseBranches_else(self, p):
    #     '''elseBranches : ELSE innerExpression'''
    #     p[0] = [CaseBranch('False', [], p[2])]

    # def p_caseExpression(self, p):
    #     '''caseExpression : CASE innerExpression caseBranches'''
    #     p[0] = ExprCase(p[0], p[3])

    # def p_caseBranches_empty(self, p):
    #     '''caseBranches :'''
    #     p[0] = []

    # def p_caseBranches_caseBranch(self, p):
    #     '''caseBranches : caseBranches caseBranch'''
    #     p[0] = p[1].append(p[2])

    # def p_caseBranch(self, p):
    #     '''caseBranch : PIPE UPPERID parameters ARROW innerExpression'''
    #     p[0] = CaseBranch(p[2], p[3], p[5])

    # def p_letExpression(self, p):
    #     '''letExpression : LET LOWERID parameters DEFEQ innerExpression IN outerExpression'''
    #     p[0] = ExprLet(p[2], curry(p[3], p[5]), p[6])

    # def p_lambdaExpression(self, p):
    #     '''lambdaExpression : LAMBDA LOWERID ARROW outerExpression'''
    #     p[0] = ExprLambda(p[2], p[4])

    def p_innerExpression(self, p):
        '''innerExpression : applyExpression'''
        p[0] = p[1]

    # def p_innerExpression_binaryOperation(self, p):
    #     '''innerExpression : innerExpression binaryOperator innerExpression'''
    #     p[0] = ExprApply(ExprApply(ExprVar(p[2]), p[1]), p[3])

    # def p_innerExpression_unaryOperation(self, p):
    #     '''innerExpression : unaryOperator innerExpression'''
    #     p[0] = ExprApply(ExprVar(p[1]), p[2])

    # def p_binaryOperator(self, p):
    #     '''binaryOperator : AND
    #              | OR
    #              | EQ
    #              | NE
    #              | GE
    #              | LE
    #              | GT
    #              | LT
    #              | PLUS
    #              | MINUS
    #              | TIMES
    #              | DIV
    #              | MOD'''
    #     p[0] = binary_operators[p[1]]

    # def p_unaryOperator(self, p):
    #     '''unaryOperator : NOT
    #                      | MINUS'''
    #     p[0] = unary_operators[p[1]]

    def p_applyExpression_atomic(self, p):
        '''applyExpression : atomicExpression'''
        p[0] = p[1]

    def p_applyExpression(self, p):
        '''applyExpression : applyExpression atomicExpression'''
        p[0] = ExprApply(p[1],p[2])

    def p_atomicExpression_lowerid(self,p):
        '''atomicExpression : LOWERID'''
        p[0] = ExprVar(p[1])

    def p_atomicExpression_upperid(self,p):
        '''atomicExpression : UPPERID'''
        p[0] = ExprConstructor(p[1])

    def p_atomicExpression_number(self,p):
        '''atomicExpression : NUMBER'''
        p[0]=ExprNumber(p[1])

    def p_atomicExpression_char(self,p):
        '''atomicExpression : CHAR'''
        p[0]=ExprChar(p[1])

    def p_atomicExpression_string(self,p):
        '''atomicExpression : STRING'''
        p[0]=buildString(p[1])

    def p_atomicExpression_parenthesis(self,p):
        '''atomicExpression : LPAREN expression RPAREN'''
        p[0]=p[2]

    def p_error(self, p):
        print(f'Syntax error at {p.value!r} | line: {p.lineno}')
        
    def parse(self, input):
        return f'{self.__yacc.parse(input, lexer=self.__lex)}'
