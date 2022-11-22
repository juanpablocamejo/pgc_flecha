import sys
from typing import TextIO
from flecha.ast import *
from copy import deepcopy

primitive_operations = ['unsafePrintInt', 'unsafePrintChar']


class Value:
    pass

class GlobalEnv:
    def __init__(self):
        self._map: dict[str, Value] = {}

    def assign(self, id: str, val: Value):
        self._map[id] = val

    def lookup(self, id: str) -> Value:
        try:
            return self._map[id]
        except:
            raise RuntimeError(f"Identificador no definido: '{id}'")


class LocalEnv:
    def __init__(self, init=[]):
        self._stack = init

    def __len__(self):
        return len(self._stack)

    def cleanup(self, env):
        return LocalEnv(self._stack[:-len(env)]) if len(env) > 0 else self

    def extend(self, id: str, val: Value):
        return LocalEnv([(id, val)]+[self._stack])

    def lookup(self, id: str):
        for x in self._stack:
            if x[0] == id:
                return x[1]
        return None


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


class FakeOutput():
    def __init__(self):
        self._buffer = ''

    def write(self, str:str):
        self._buffer += str

    def __repr__(self) -> str:
        return self._buffer

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
        elif isinstance(ast, Value): return ast
        # elif isinstance(ast, ExprCase): self.eval_case(ast, env)
        # elif isinstance(ast, ExprLet): self.eval_let(ast, env)
        raise RuntimeError(f"No se pudo evaluar la expresión {ast}")

    def eval_program(self, ast: Program, env: LocalEnv = LocalEnv()):
        for d in ast.definitions():
            self.eval_definition(d, env)
        self.eval(self._global_env.lookup('main'), env)
        return VoidValue()

    def eval_definition(self, ast: Definition, env: LocalEnv) -> VoidValue:
        self._global_env.assign(ast.id(), self.eval(ast.expr(), env))
        return VoidValue()

    def eval_var(self, ast: ExprVar, env: LocalEnv) -> Value:
        return self.lookup(ast.id(), env)        

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
        return self.eval(_cl.body, env.extend(_cl.param, _arg))
    
    def is_unary_operation(self, ast:ExprApply):
        fn = ast.fn()
        return isinstance(fn, ExprVar) and (fn.id() in primitive_operations or fn.id() in unary_operators.values())

    def is_binary_operation(self, ast:ExprApply):
        arg = ast.arg()
        return isinstance(ast.fn(), ExprApply) and isinstance(arg, ExprApply) and arg.id in binary_operators.values()

    def eval_unary_op(self, op: ExprVar, arg:Expression, env:LocalEnv):
        _arg = self.eval(arg,env)
        match op.id():
            case "unsafePrintInt": return self.eval_print_int(_arg)
            case "unsafePrintChar": return self.eval_print_char(_arg)

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
