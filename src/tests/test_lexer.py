import logging
import sys
from flecha.lexer import Lexer
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

testData = {
    "\'\\n\'": [('CHAR', '\n')],
    "\"\\n\\n\\t\\r\"": [('STRING', "\n\n\t\r")],
    "def a = 1": [('DEF', 'def'), ('LOWERID', 'a'), ('DEFEQ', '='), ('NUMBER', 1)],
    "a==b":[('LOWERID', 'a'), ('EQ', '=='),('LOWERID', 'b')],
    "==" : [('EQ',"==")],
    "!=" : [('NE',"!=")],
    ">=" : [('GE',">=")],
    "<=" : [('LE',"<=")],
    "=" : [('DEFEQ',"=")],
    ";" : [('SEMICOLON',";")],
    "(" : [('LPAREN',"(")],
    ")" : [('RPAREN',")")],
    "\\" : [('LAMBDA',"\\")],
    "|" : [('PIPE',"|")],
    "->" : [('ARROW',"->")],
    "&&" : [('AND',"&&")],
    "||" : [('OR',"||")],
    "!" : [('NOT',"!")],
    ">" : [('GT',">")],
    "<" : [('LT',"<")],
    "+" : [('PLUS',"+")],
    "-" : [('MINUS',"-")],
    "*" : [('TIMES',"*")],
    "/" : [('DIV',"/")],
    "%" : [('MOD',"%")],
    "-- \"\\def a= 1+2\" \n" : [],
    "True" : [("UPPERID",'True')],
    'def a = Cons "" (Cons "" Nil)':[('DEF','def'),('LOWERID','a'),('DEFEQ','='),('UPPERID','Cons'),('STRING',''),('LPAREN','('),('UPPERID','Cons'),('STRING',''),('UPPERID','Nil'),('RPAREN',')')]
}


def testLexer():
    l = Lexer().build()
    data: tuple[str, list[tuple[str, any]]] = testData.items()
    for input, expected in data:
        l.input(input)
        while True:
            tok = l.token()
            logging.debug(tok)
            if not tok:
                break
            assert (tok.type, tok.value) == expected.pop(0)
        assert len(expected) == 0
