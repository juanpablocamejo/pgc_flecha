import ply.lex as lex
from ply.lex import LexToken
import re
LexInstance = lex.Lexer

def replace(m): 
    return Lexer.escaped_chars[m.group('esc')]

class Lexer():
    reserved = {
        'def': 'DEF',
        'if': 'IF',
        'then': 'THEN',
        'elif': 'ELIF',
        'else': 'ELSE',
        'case': 'CASE',
        'let': 'LET',
        'in': 'IN',
        'def': 'DEF'
    }

    tokens = [
        # Identificadores y constantes
        'LOWERID', 'UPPERID', 'NUMBER', 'CHAR', 'STRING',

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

    t_EQ = r'=='
    t_NE = r'!='
    t_GE = r'>='
    t_LE = r'<='
    t_DEFEQ = r'='
    t_SEMICOLON = r';'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_PIPE = r'\|'
    t_ARROW = r'->'
    t_LAMBDA = r'(\\)'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_GT = r'>'
    t_LT = r'<'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIV = r'/'
    t_MOD = r'%'

    escaped_chars = {
        "\\n": '\n',
        "\\r": '\r',
        "\\t": '\t',
        "\\\\": '\\',
        '\\"': '"',
        "\\'": "'"
    }

    __esc_chars_pattern = re.compile(r"(?P<esc>\\(n|t|r|\\|\'|\"))")

    def t_CHAR(self, t):
        r"\'(?P<value>(\\(n|t|r|\\|\'|\"))|[^\\])\'"
        val = t.lexer.lexmatch.group('value')
        t.value = Lexer.escaped_chars[val] if val in Lexer.escaped_chars else val
        return t

    def t_STRING(self, t):
        r'\"(?P<value>((\\(n|t|r|\\|\'|\"))|[^\\])*)\"'
        t.value = self.unescapeString(t.lexer.lexmatch.group('value'))
        return t

    def unescapeString(self, txt):
        return re.sub(Lexer.__esc_chars_pattern, lambda m: Lexer.escaped_chars[m.group('esc')], txt)

    def t_LOWERID(self, t):
        r'[a-z][_a-zA-Z0-9]*'
        t.type = Lexer.reserved.get(t.value, 'LOWERID')
        return t

    def t_UPPERID(self, t):
        r'[A-Z][_a-zA-Z0-9]*'
        t.type = Lexer.reserved.get(t.value, 'UPPERID')
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_Comment(self, t):
        r'\--.*\n?'
        t.lexer.lineno += 1

    def t_ignore_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    def t_error(self, t):
        print(f'Illegal character {t.value[0]!r}')
        t.lexer.skip(1)

    def build(self) -> LexInstance:
        return lex.lex(module=self)
