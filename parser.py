from ply.yacc import yacc
from lexer import tokens
from models.program import Program

# parser


# def p_program(p):
#     '''
#     program :  program definition
#     '''
#     p[0] = p[1].append(p[2])


# def p_program_definition(p):
#     '''
#     program : definition
#     '''
#     p[0] = Program(p[1])


# def p_definition_constante(p):
#     '''
#     definition : DEF LOWERID DEFEQ expression
#     '''
#     p[0] = ('Defi', p[2], p[4])


# def p_expression_number(p):
#     ''' expression : NUMBER'''
#     p[0] = p[1]

# def p_parametros(p):
#     '''parametros :  parametros LOWERID'''
#     p[0] = p[1], p[2]

# def p_empty(p):
#     'empty :'
#     pass


def p_error(p):
    print(f'Syntax error at {p.value!r}')


# Build the parser
parser = yacc()

ast = parser.parse('def a = 5')
print(ast)
