import sys
from flecha.lexer import Lexer
from flecha.parser import Parser

# region COMMANDS

def parse_input(input):
    print("input:",input)
    print("ast:",Parser().parse(input))

def parse_file(input_file):
    with open(file=input_file, mode='r', encoding='utf-8',) as file:
        print(Parser().parse(file.read()))

def tokenize_input(input):
    _lex = Lexer().build()
    _lex.input(input)
    result = []
    while True:
        tok = _lex.token()
        if not tok:
            break
        result.append((tok.type,tok.value))
    print(result)

def tokenize_file(input_file):
    with open(file=input_file, mode='r', encoding='utf-8',) as file:
        _lex = Lexer().build()
        _lex.input(file.read())
        result = []
        while True:
            tok = _lex.token()
            if not tok:
                break
            result.append((tok.type,tok.value))
        print(result)

def print_help():
    print("Usage:")
    for k, val in __commands.items():
        print(f' py src/main.py {k} {" ".join([f"<{v}>" for v in val[1]])}')


__commands = {
    '--tokenize': (tokenize_input, ['input_file']),
    '--tokenize-file': (tokenize_file, ['input_file']),
    '--parse': (parse_input, ['"input"']),
    '--parse-file': (parse_file, ['input_file']),
}

# endregion
def process_command(key, params):
    __commands[key][0](*params)


def valid_args(args):
    return args and (args[0] in __commands) and (len(args) == (len(__commands[args[0]][1])+1))


def main():
    if (valid_args(sys.argv[1:])):
        process_command(sys.argv[1], sys.argv[2:])
    else:
        print_help()


if __name__ == "__main__":
    main()
