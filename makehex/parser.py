from makehex import ast, combinators


def parser() -> combinators.Parser:
    return combinators.Phrase(stmt_list())


def p() -> combinators.Parser:
    return (combinators.Tag('STRING') ^ (lambda x: ast.StringExp(x))) | (combinators.Tag('CHARS') ^ (lambda x: ast.CharsExp(x))) |\
           (combinators.Tag('HEX') ^ (lambda x: ast.HexExp(x))) | (combinators.Tag('NAME') ^ (lambda x: ast.VarExp(x)))


def stmt_list() -> combinators.Parser:
    return -(stmt()) ^ (lambda a: ast.CompoundStatement(a))


def stmt() -> combinators.Parser:
    return p() | expr() | block()


def expr() -> combinators.Parser:
    def process(parsed):
        (exp, args) = parsed
        return ast.CallExp(exp, dict(args))

    return combinators.Tag('CALL') + -call_stmt() ^ process


def block() -> combinators.Parser:
    def process(parsed):
        (((exp, args), body), _) = parsed
        return ast.CallExp(exp, dict(args), body)

    return combinators.Tag('BLOCK') + -call_stmt() + combinators.Lazy(stmt_list) + combinators.Reserved('end', 'END') ^ process


def call_stmt() -> combinators.Parser:
    def process(parsed):
        (((func_name, _), args), _) = parsed
        return func_name, args
    return combinators.Tag('VA_NAME') + combinators.Reserved('(', 'RESERVED') + +(-p()) + combinators.Reserved(')', 'RESERVED') ^ process
