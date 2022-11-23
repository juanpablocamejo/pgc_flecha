from enum import Enum
from typing import TextIO
from flecha.ast import *

# region Values
class Value:
    pass

class VoidValue(Value):
    pass

class IntValue(Value):
    def __init__(self, n) -> None:
        self.value = n


class CharValue(Value):
    def __init__(self, n: int):
        self.value = chr(n)

class ClosureValue(Value):
    def __init__(self, param, body, env) -> None:
        self.param: str = param
        self.body: Expression = body
        self.env: LocalEnv = env

class StructValue(Value):
    def __init__(self, ctor, params):
        self.ctor = ctor
        self.params = params
# endregion

# region enviroments
class GlobalEnv:
    def __init__(self):
        self._map: dict[str, Value] = {}

    def assign(self, id: str, val: 'Value'):
        self._map[id] = val

    def lookup(self, id: str) -> 'Value':
        try:
            return self._map[id]
        except:
            raise RuntimeError(f"Identificador no definido: '{id}'")

class LocalEnv:
    def __init__(self, init=[]):
        self._stack = init

    def __len__(self):
        return len(self._stack)

    def extend(self, id: str, val: 'Value'):
        return LocalEnv([(id, val)] + self._stack)

    def lookup(self, id: str):
        for x in self._stack:
            if x[0] == id:
                return x[1]
        return None

    def __repr__(self):
        return str(self._stack)
# endregion

class FakeOutput():
    def __init__(self):
        self._buffer = ''

    def write(self, str:str):
        self._buffer += str

    def read(self) -> str:
        return self._buffer

class Primitives(Enum):
    UNSAFE_PRINT_INT = 'unsafePrintInt'
    UNSAFE_PRINT_CHAR = 'unsafePrintChar'

class Interpreter:
    def __init__(self, output:TextIO ) -> None:
        self._global_env = GlobalEnv()
        self._output = output


    def lookup(self, id: str, env: LocalEnv):
        val = env.lookup(id)
        return self._global_env.lookup(id) if (val is None) else val

    def eval(self, ast: AstNode, env: LocalEnv) -> Value:
        if isinstance(ast, Program): return self.eval_program(ast, env)
        elif isinstance(ast, Definition): return self.eval_definition(ast, env)
        elif isinstance(ast, ExprVar): return self.eval_var(ast, env)
        elif isinstance(ast, ExprNumber): return self.eval_number(ast)
        elif isinstance(ast, ExprChar): return self.eval_char(ast)
        elif isinstance(ast, ExprLambda): return self.eval_lambda(ast, env)
        elif isinstance(ast, ExprApply): return self.eval_apply(ast, env)
        elif isinstance(ast, ExprLet): return self.eval_let(ast, env)
        # elif isinstance(ast, ExprCase): self.eval_case(ast, env)
        raise RuntimeError(f"No se pudo evaluar la expresión {ast}")

    def eval_program(self, ast: Program, env: LocalEnv = LocalEnv()):
        for d in ast.definitions():
            self.eval_definition(d, env)
        return self._global_env.lookup('main')

    def eval_definition(self, ast: Definition, env: LocalEnv) -> VoidValue:
        self._global_env.assign(ast.id(), self.eval(ast.expr(), env))
        return VoidValue()

    def eval_var(self, ast: ExprVar, env: LocalEnv) -> Value:
        return self.lookup(ast.id(), env)

    def eval_let(self, ast:ExprLet, env:LocalEnv) -> Value:
        arg_val = self.eval(ast.argExpr(),env)
        return self.eval(ast.inExpr(), env.extend(ast.param(),arg_val))        

    def eval_number(self, ast: ExprNumber) -> IntValue:
        return IntValue(ast.value)

    def eval_char(self, ast: ExprNumber) -> CharValue:
        return CharValue(ast.value)
    
    def eval_lambda(self, ast: ExprLambda, env:LocalEnv) -> ClosureValue:
        return ClosureValue(ast.param(), ast.body(), env)

    def eval_apply(self, ast: ExprApply, env:LocalEnv) -> Value:
        if self.is_unary_operation(ast): return self.eval_unary_op(ast.fn(), ast.arg(), env)
        elif self.is_binary_operation(ast): return self.eval_binary_op(ast, env)
        _arg = self.eval(ast.arg(), env)
        _cl: ClosureValue = self.eval(ast.fn(), env)
        assert isinstance(_cl, ClosureValue)
        return self.eval(_cl.body, _cl.env.extend(_cl.param, _arg))
    
    def is_unary_operation(self, ast:ExprApply):
        fn = ast.fn()
        return is_var(fn) and (fn.id() in [p.value for p in Primitives] or fn.id() in unary_operators.values())

    def is_binary_operation(self, ast:ExprApply):
        fn = ast.fn()
        return is_apply(fn) and is_var(fn.arg()) and fn.arg().id() in binary_operators.values()

    def eval_unary_op(self, op: ExprVar, arg:Expression, env:LocalEnv):
        _arg = self.eval(arg,env)
        match op.id():
            case Primitives.UNSAFE_PRINT_INT.value: return self.eval_print_int(_arg)
            case Primitives.UNSAFE_PRINT_CHAR.value: return self.eval_print_char(_arg)
            case UnaryOperators.NOT.value: return self.eval_not(_arg)

    def eval_binary_op(self,ast:ExprApply):
        return VoidValue()

    def eval_print_int(self, arg:IntValue):
        assert isinstance(arg, IntValue)
        self._output.write(f'{arg.value}')
        return VoidValue()

    def eval_print_char(self, arg:CharValue):
        assert isinstance(arg, CharValue)
        self._output.write(f'{arg.value}')
        return VoidValue()
    
    def eval_add(self, expr1, expr2, l_env, g_env):
        val1 = expr1.eval(l_env, g_env)
        val2 = expr2.eval(l_env, g_env)
        assert isinstance(val1, IntValue) and isinstance(val2, IntValue)
        return IntValue(val1.value + val2.value)

def is_apply(ast:AstNode):
    return isinstance(ast, ExprApply)
        
def is_var(ast:AstNode):
    return isinstance(ast, ExprVar)