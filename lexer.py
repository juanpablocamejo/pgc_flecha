from ply.lex import lex

reserved = {
    'def': 'DEF',
    'if': 'IF',
    'then': 'THEN',
    'elif': 'ELIF',
    'else': 'ELSE',
    'case': 'CASE',
    'let': 'LET',
    'in': 'IN',
    'def': 'DEF',
}

tokens = [
    # Identificadores y constantes
    'LOWERID', 'UPPERID', 'NUMBER', 'CHAR', 'STRING',

    # palabras reservadas
    'DEF', 'IF', 'THEN', 'ELIF', 'ELSE', 'CASE', 'LET', 'IN',

    # símbolos reservados
    # delimitadores (=,;,(,),\,|,->)
    'DEFEQ', 'SEMICOLON', 'LPAREN', 'RPAREN', 'LAMBDA', 'PIPE', 'ARROW',

    # operadores lógicos
    'AND', 'OR', 'NOT',
    # operadores relacionales
    'EQ', 'NE', 'GE', 'LE', 'GT', 'LT',
    # operadores aritmeticos
    'PLUS', 'MINUS', 'TIMES', 'DIV', 'MOD'
] + list(reserved.values())

t_ignore = ' \t'

t_UPPERID = r'[A-Z][_a-zA-Z0-9]*'
t_CHAR = r'\'.\''
t_STRING = r'\".*\"'
t_DEFEQ = r'\='
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LAMBDA = r'\\'
t_PIPE = r'\|'
t_ARROW = r'\-\>'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_NOT = r'\!'
t_EQ = r'\=='
t_NE = r'\!='
t_GE = r'\>='
t_LE = r'\<='
t_GT = r'\>'
t_LT = r'\<'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIV = r'\/'
t_MOD = r'\%'


def t_LOWERID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'LOWERID')    # Check for reserved words
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_Comment(t):
    r'\--.*\n?'
    t.lexer.lineno += t.value.count('\n')


def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)


lexer = lex()
