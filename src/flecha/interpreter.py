from enum import Enum
from typing import Callable, TextIO
from flecha.ast import *

class ValueTypes(Enum):
    Int = "Int"
    Char = "Char"
    Closure = "Closure"
    Struct = "Struct"
    Null = "Null"

class Booleans(Enum):
    TRUE = "True"
    FALSE = "False"

# region Values
class Value:
    def __init__(self):
        self.type = ValueTypes.Null.value
class VoidValue(Value):
    pass

class LiteralValue(Value):
    def __init__(self, type, v):
        self.value = v
        self.type = type.value

    def __repr__(self) -> str:
        return self.value

class IntValue(LiteralValue):
    def __init__(self,v):
        super().__init__(ValueTypes.Int, v)

class CharValue(LiteralValue):
    def __init__(self, v:int):
        super().__init__(ValueTypes.Char, chr(v)) 

class ClosureValue(Value):
    def __init__(self, param, body, env) -> None:
        self.param: str = param
        self.body: Expression = body
        self.env: LocalEnv = env
        self.type = ValueTypes.Closure.value
        
    def __repr__(self):
        return json.dumps([self.type, self.param]+self.body, default=str)

class StructValue(Value):
    def __init__(self, ctor:str, args: list[Value]):
        self.ctor: str = ctor
        self.args: list[Value] = args
        self.type = ValueTypes.Struct.value

    def __repr__(self):
        return json.dumps([self.type,self.ctor]+self.args,default=str)
class BooleanValue(StructValue):
    def __init__(self,b):
        super().__init__(Booleans.TRUE.value if b else Booleans.FALSE.value,[])


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



class Primitives(Enum):
    UNSAFE_PRINT_INT = 'unsafePrintInt'
    UNSAFE_PRINT_CHAR = 'unsafePrintChar'

class Interpreter:
    def __init__(self, output:TextIO ) -> None:
        self._global_env = GlobalEnv()
        self._output = output
        self._eval_map:dict[Tags,Callable[[AstNode],Value]] = {
            Tags.Program : self.eval_program,
            Tags.Definition: self.eval_definition,
            Tags.ExprVar: self.eval_var,
            Tags.ExprNumber: self.eval_number,
            Tags.ExprChar: self.eval_char,
            Tags.ExprLambda: self.eval_lambda,
            Tags.ExprApply: self.eval_apply,
            Tags.ExprConstructor: self.eval_constructor,
            Tags.ExprLet: self.eval_let,
            Tags.ExprCase: self.eval_case
        }
        self._relational_ops = {
            BinaryOperators.EQ.value : lambda x, y: x == y,
            BinaryOperators.NE.value : lambda x, y: x != y,
            BinaryOperators.LE.value : lambda x, y: x <= y,
            BinaryOperators.GE.value : lambda x, y: x >= y,
            BinaryOperators.LT.value : lambda x, y: x < y,
            BinaryOperators.GT.value : lambda x, y: x > y,
        }
        self._arithmetic_ops = {
            BinaryOperators.DIV.value : lambda x, y: x // y,
            BinaryOperators.MOD.value : lambda x, y: x % y,
            BinaryOperators.SUB.value : lambda x, y: x - y,
            BinaryOperators.ADD.value : lambda x, y: x + y,
            BinaryOperators.MUL.value : lambda x, y: x * y,

        }
        self._logical_ops = {
            BinaryOperators.AND.value : self.eval_and,
            BinaryOperators.OR.value : self.eval_or
        }


    def eval(self, ast: AstNode, env: LocalEnv) -> Value:
        if ast.tag in self._eval_map: 
            return self._eval_map[ast.tag](ast,env)
        raise RuntimeError(f"No se pudo evaluar la expresión {ast}")

    def eval_program(self, ast: Program, env: LocalEnv):
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

    def eval_number(self, ast: ExprNumber, env) -> IntValue:
        return IntValue(ast.value)

    def eval_char(self, ast: ExprNumber, env) -> CharValue:
        return CharValue(ast.value)
   
    def eval_lambda(self, ast: ExprLambda, env:LocalEnv) -> ClosureValue:
        return ClosureValue(ast.param(), ast.body(), env)

    def eval_apply(self, ast: ExprApply, env:LocalEnv) -> Value:
        if self.is_unary_operation(ast): return self.eval_unary_op(ast.fn(), ast.arg(), env)
        elif self.is_binary_operation(ast): return self.eval_binary_op(ast, env)
        elif self.is_struct_expr(ast): return self.eval_struct(ast,env)
        _arg = self.eval(ast.arg(), env)
        _cl: ClosureValue = self.eval_as_closure(ast.fn(),env)
        return self.eval(_cl.body, _cl.env.extend(_cl.param, _arg))

    def eval_constructor(self, ast:ExprConstructor, env):
        return StructValue(ast.id(),[])

    def eval_struct(self, ast: AstNode, env:LocalEnv) -> Value:
        _curr = ast
        _args = []
        while(_curr.tag == Tags.ExprApply):
            _args.insert(0,_curr.arg())
            _curr = _curr.fn()
        _ctor:ExprConstructor = _curr
        return StructValue(_ctor.id(),[self.eval(a,env) for a in _args])
    
    def eval_case(self, ast: ExprCase, env:LocalEnv) -> Value:
        val:Value = self.eval(ast.expr(),env)
        for b in ast.branches():
            is_match, new_env = self.match(val,b,env)
            if is_match : return self.eval(b.expr(), new_env)
        raise RuntimeError(f"Error al intentar matchear la expresión: {val}")

# unary operations
    def eval_unary_op(self, op: ExprVar, exp:Expression, env:LocalEnv):
        match op.id():
            case Primitives.UNSAFE_PRINT_INT.value: return self.eval_print_int(exp, env)
            case Primitives.UNSAFE_PRINT_CHAR.value: return self.eval_print_char(exp, env)
            case UnaryOperators.NOT.value: return self.eval_not(exp, env)
            case UnaryOperators.UMINUS.value: return self.eval_uminus(exp, env)

    def eval_not(self, exp:AstNode, env:LocalEnv):
        return BooleanValue(not self.eval_as_boolean(exp,env))

    def eval_uminus(self,exp:AstNode,env):
        return IntValue(-self.eval_as_number(exp,env))

    def eval_print_int(self, exp:AstNode, env):
        self._output.write(f'{self.eval_as_number(exp,env)}')
        return VoidValue()

    def eval_print_char(self, exp:AstNode, env):
        self._output.write(f'{self.eval_as_char(exp,env)}')
        return VoidValue()

#binary operations
    def eval_binary_op(self, ast:ExprApply, env:LocalEnv):
        left = ast.fn().arg()
        right = ast.arg()
        binOp : ExprVar = ast.fn().fn().id()
        if binOp in self._relational_ops: eval_fn = self.eval_relational_op
        elif binOp in self._arithmetic_ops: eval_fn = self.eval_arithmetic_op
        elif binOp in self._logical_ops: eval_fn = self.eval_logical_op
        else: raise RuntimeError(f"Operación no reconocida: {binOp}")
        return eval_fn(left, binOp, right, env)

    def eval_relational_op(self,left: AstNode, op:str, right: AstNode, env:LocalEnv):
        vL,vR = self.assert_numeric_operation(left, op, right, env)
        return BooleanValue(self._relational_ops[op](vL,vR))

    def eval_arithmetic_op(self,left: AstNode, op:str, right: AstNode, env:LocalEnv):
        vL,vR = self.assert_numeric_operation(left, op, right, env)
        return IntValue(self._arithmetic_ops[op](vL,vR))

    def eval_logical_op(self,left: AstNode, op:str, right: AstNode,env:LocalEnv):
        return self._logical_ops[op](left,right,env)

    def eval_or(self,left: AstNode, right: AstNode,env:LocalEnv):
        return BooleanValue(self.eval_as_boolean(left, env) or self.eval_as_boolean(right, env))

    def eval_and(self,left: AstNode, right: AstNode,env:LocalEnv):
        return BooleanValue(self.eval_as_boolean(left, env) and self.eval_as_boolean(right, env))

#aux
    def lookup(self, id: str, env: LocalEnv):
        val = env.lookup(id)
        return self._global_env.lookup(id) if (val is None) else val

    def match(self, val:Value, b:CaseBranch, env:LocalEnv):
        return self.match_struct(val,b,env) if (val.type == ValueTypes.Struct.value) else (val.type==b.id(), env)

    def match_struct(self, val:StructValue, b:CaseBranch, env:LocalEnv):
        _new_env = env
        _is_match:bool = val.ctor==b.id() and len(val.args) == len(b.params())
        if _is_match:
            for i,p in enumerate(b.params()):
                _new_env = _new_env.extend(p,val.args[i])
        return (_is_match, _new_env)
           
    def is_unary_operation(self, ast:ExprApply):
        fn = ast.fn()
        return self.is_var_expr(fn) and (fn.id() in [p.value for p in Primitives] or fn.id() in unary_operators.values())

    def is_binary_operation(self, ast:ExprApply):
        fn = ast.fn()
        return self.is_app_expr(fn) and self.is_var_expr(fn.fn()) and fn.fn().id() in binary_operators.values()

    def is_struct_expr(self, ast: AstNode) -> bool:
        _curr = ast
        while(_curr.tag == Tags.ExprApply):
            _curr = _curr.fn()
        return _curr.tag == Tags.ExprConstructor

    def is_app_expr(self,ast:AstNode):
        return ast.tag == Tags.ExprApply
            
    def is_var_expr(self,ast:AstNode):
        return ast.tag == Tags.ExprVar

    def assert_numeric_operation(self, left, op, right, env):
        try:
            vL = self.eval_as_number(left, env)
            vR = self.eval_as_number(right, env)
        except:
            raise RuntimeError(f"El operador {op} solo se puede usar con números")
        return(vL,vR)    

    def eval_as_number(self, exp:AstNode, env) -> int:
        val = self.eval(exp,env)
        self.assert_number_val(val)
        return val.value

    def eval_as_closure(self, exp:AstNode, env) -> int:
        val = self.eval(exp, env)
        self.assert_closure_val(val)
        return val

    def eval_as_boolean(self, exp:AstNode, env):
        val = self.eval(exp, env)
        self.assert_bool_val(val)
        return val.ctor == Booleans.TRUE.value
    
    def assert_number_val(self, val:IntValue):
        if val.type != ValueTypes.Int.value: 
            raise RuntimeError(f"El valor {val} no se puede evaluar como número")

    def assert_closure_val(self, val:ClosureValue):
        if val.type != ValueTypes.Closure.value: 
            raise RuntimeError(f"El valor {val} no se puede evaluar como closure")

    def assert_bool_val(self, val:StructValue):
        if not (val.type == ValueTypes.Struct.value and val.ctor in [Booleans.TRUE.value,Booleans.FALSE.value]): 
            raise RuntimeError(f"El valor {val} no se puede evaluar como booleano")

    def eval_as_char(self,exp,env):
        v = self.eval(exp,env)
        if v.type != ValueTypes.Char.value:
            raise RuntimeError(f"El valor {v} no se puede evaluar como char")
        return v.value
