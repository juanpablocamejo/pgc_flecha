from flecha.lexer import Lexer

testData = {
    # "\'\\n\'": [('CHAR', '\n')],
    # "\"\\n\\n\\t\\r\"": [('STRING', "\n\n\t\r")],
    "def a = 1": [('DEF', 'def'), ('LOWERID', 'a'), ('DEFEQ', '='), ('NUMBER', 1)],
    # "a==b":[('LOWERID', 'a'), ('EQ', '=='),('LOWERID', 'b')],
    # "==" : [('EQ',"==")],
    # "!=" : [('NE',"!=")],
    # ">=" : [('GE',">=")],
    # "<=" : [('LE',"<=")],
    # "=" : [('DEFEQ',"=")],
    # ";" : [('SEMICOLON',";")],
    # "(" : [('LPAREN',"(")],
    # ")" : [('RPAREN',")")],
    # "\\" : [('LAMBDA',"\\")],
    # "|" : [('PIPE',"|")],
    # "->" : [('ARROW',"->")],
    # "&&" : [('AND',"&&")],
    # "||" : [('OR',"||")],
    # "!" : [('NOT',"!")],
    # ">" : [('GT',">")],
    # "<" : [('LT',"<")],
    # "+" : [('PLUS',"+")],
    # "-" : [('MINUS',"-")],
    # "*" : [('TIMES',"*")],
    # "/" : [('DIV',"/")],
    # "%" : [('MOD',"%")],
    # "-- \"\\def a= 1+2\" \n" : [],
    # "True" : [("UPPERID",'True')]
}


def testLexer():
    l = Lexer().build()
    data: tuple[str, list[tuple[str, any]]] = testData.items()
    for input, expected in data:
        l.input(input)
        while True:
            tok = l.token()
            if not tok:
                break
            assert (tok.type, tok.value) == expected.pop(0)
        assert len(expected) == 0
