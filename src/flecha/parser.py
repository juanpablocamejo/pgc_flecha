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
        '''definition : DEF LOWERID DEFEQ expression'''
        p[0] = Definition(p[2], p[4])

    def p_expression_number(self, p):
        '''expression : NUMBER'''
        p[0] = ExprNumber(p[1])

    # def p_definition(self, p):
    #     """definition : DEF LOWERID DEFEQ NUMBER"""
    #     p[0] = Definition(p[2],p[3])

    # def p_definition_with_params(self, p):
    #     '''definition : DEF LOWERID parameters DEFEQ expressio'''
    #     p[0] = Definition(p[2], curry(p[3], p[4]))

    # def p_parameters_empty(self, p):
    #     '''parameters :'''
    #     p[0] = []

    # def p_parameters(self, p):
    #     '''parameters : LOWERID parameters'''
    #     p[0] = p[2].append(p[1])

    # def p_empty(self, p):
    #     """empty :"""
    #     pass





    # def p_expression_externalExpression(self, p):
    #     """ expression : externalExpression"""
    #     p[0] = p[1]

    # def p_sequence_expression(self, p):
    #     '''expression: expression SEMICOLON externalExpression'''
    #     p[0] = ExprLet('_', p[1], p[3])

    # def p_externalExpression(self, p):
    #     '''externalExpression: ifExpression
    #                         | caseExpression
    #                         | letExpression
    #                         | lambdaExpression
    #                         | internalExpression'''
    #     p[0] = p[1]

    # def p_ifExpression(self, p):
    #     '''ifExpression : IF internalExpression THEN internalExpression elseBranches'''
    #     p[0] = ExprCase(p[2], [CaseBranch('True', [], p[4])].extend(p[5]))

    # def p_elseBranches_elif(self, p):
    #     '''elseBranches : ELIF internalExpression THEN internalExpression elseBranches'''
    #     p[0] = [CaseBranch('False', [], ExprCase(
    #         p[2], [CaseBranch('True', [], p[4])].extend(p[5])))]

    # def p_elseBranches_else(self, p):
    #     '''elseBranches : ELSE internalExpression'''
    #     p[0] = [CaseBranch('False', [], p[2])]

    # def p_caseExpression(self, p):
    #     '''caseExpression : CASE internalExpression caseBranches'''
    #     p[0] = ExprCase(p[0], p[3])

    # def p_caseBranches_empty(self, p):
    #     '''caseBranches: empty'''
    #     p[0] = []

    # def p_caseBranches_caseBranch(self, p):
    #     '''caseBranches : caseBranches caseBranch'''
    #     p[0] = p[1].append(p[2])

    # def p_caseBranch_case(self, p):
    #     '''caseBranch : PIPE UPPERID parameters ARROW internalExpression'''
    #     p[0] = CaseBranch(p[2], p[3], p[5])

    # def P_letExpression(self, p):
    #     '''letExpression : LET ID parameters DEFEQ internalExpression IN externalExpression'''
    #     p[0] = ExprLet(p[2], curry(p[3], p[5]), p[6])

    # def p_lambdaExpression(self, p):
    #     '''lambdaExpression : LAMBDA ID ARROW externalExpression'''
    #     p[0] = ExprLambda(p[2], p[4])

    # def p_internalExpression(self, p):
    #     '''internalExpression : applyExpression'''
    #     p[0] = p[1]

    # def p_internalExpression_binaryOperation(self, p):
    #     '''internalExpression : internalExpression binaryOperator internalExpression'''
    #     p[0] = ExprApply(ExprApply(ExprVar(p[2]), p[1]), p[3])

    # def p_internalExpression_unaryOperation(self, p):
    #     '''internalExpression : unaryOperator internalExpression'''
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
    #     p[0] = p[1].type

    # def p_unaryOperator(self, p):
    #     '''unaryOperator : NOT
    #                      | UMINUS'''
    #     p[0] = p[1].type

    # def p_applyExpression_atomic(self, p):
    #     '''applyExpression : atomicExpression'''
    #     p[0] = p[1]

    # def p_applyExpression(self, p):
    #     '''applyExpression : applyExpression atomicExpression'''
    #     p[0] = ExprApply(p[1],p[2])

    # def p_atomicExpression_id(self,p):
    #     '''atomicExpression : LOWERID'''
    #     p[0] = ExprVar(p[1])

    # def p_atomicExpression_id(self,p):
    #     '''atomicExpression : UPPERID'''
    #     p[0] = ExprConstructor(p[1])

    # def p_atomicExpression_number(self,p):
    #     '''atomicExpression : NUMBER'''
    #     p[0]=ExprNumber(p[1])

    # def p_atomicExpression_char(self,p):
    #     '''atomicExpression : CHAR'''
    #     p[0]=ExprChar(p[1])

    # def p_atomicExpression_char(self,p):
    #     '''atomicExpression : STRING'''
    #     p[0]=buildString(p[1])

    # def p_atomicExpression_brackets(self,p):
    #     '''atomicExpression : LPAREN expression RPAREN'''
    #     p[0]=p[2]

    def p_error(self, p):
        print(f'Syntax error at {p.value!r}')

    def parse(self, input):
        return f'{self.__yacc.parse(input, lexer=self.__lex)}'
