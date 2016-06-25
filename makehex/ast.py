import logging

from makehex.tools import debug_point


class Expression:
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        return None

    def write(self, out, locals_: dict, globals_: dict) -> None:
        out.write(self.eval(out, locals_, globals_))


class HexExp(Expression):
    def __init__(self, i: str):
        self.i = i

    def __repr__(self):
        return '%s' % self.i

    @debug_point('HexExp')
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        return bytes.fromhex(self.i)


class StringExp(Expression):
    def __init__(self, s: str):
        self.s = s

    def __repr__(self):
        return '"%s"' % self.s

    @debug_point('StringExp')
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        return self.s.encode(locals_["ENCODING"]) + b'\x00'


class CharsExp(Expression):
    def __init__(self, s: str):
        self.s = s

    def __repr__(self):
        return '\'%s\'' % self.s

    @debug_point('CharsExp')
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        return self.s.encode(locals_["ENCODING"])


class VarExp(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '.%s' % self.name

    @debug_point('VarExp')
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        return locals_[self.name].eval(out, locals_, globals_)

    @debug_point('VarExp')
    def write(self, out, locals_: dict, globals_: dict) -> None:
        locals_[self.name].write(out, locals_, globals_)


class CompoundStatement(Expression):
    def __init__(self, expressions: list):
        self.expressions = expressions
        self.results = None

    @debug_point('CompoundStatement')
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        results = []
        for exp in self.expressions:
            result = exp.eval(out, locals_, globals_)
            if isinstance(result, bytes):
                results.append(result)
            else:
                logging.warning("Result of %s: %s is not bytes!", exp, result)
        return b''.join(results)

    @debug_point('CompoundStatement')
    def write(self, out, locals_: dict, globals_: dict) -> None:
        for exp in self.expressions:
            exp.write(out, locals_, globals_)


class CallExp(Expression):
    def __init__(self, name: str, args: dict, body: Expression=None):
        self.name = name
        self.args = args
        self.body = body

    @debug_point('CallExp')
    def eval(self, out, locals_: dict, globals_: dict) -> bytes:
        return globals_[self.name].eval(self.args, out, locals_, globals_, self.body)

    @debug_point('CallExp')
    def write(self, out, locals_: dict, globals_: dict) -> None:
        globals_[self.name].write(self.args, out, locals_, globals_, self.body)
