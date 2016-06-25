import logging


class Result:
    def __init__(self, value, pos: int):
        self.value = value
        self.pos = pos


class Parser:
    def __call__(self, tokens: list, pos: int) -> Result:
        return None

    def __add__(self, other):
        return Concat(self, other)

    def __or__(self, other):
        return Alternate(self, other)

    def __xor__(self, function):
        return Process(self, function)

    def __pos__(self):
        return Opt(self)

    def __neg__(self):
        return Rep(self)


class Reserved(Parser):
    def __init__(self, value: str, tag: str):
        self.value = value
        self.tag = tag

    def __call__(self, tokens: list, pos: int) -> Result:
        if pos < len(tokens) and tokens[pos].text == self.value and tokens[pos].tag is self.tag:
            return Result(tokens[pos].text, pos + 1)
        else:
            return None


class Tag(Parser):
    def __init__(self, tag: str):
        self.tag = tag

    def __call__(self, tokens: list, pos: int) -> Result:
        if pos < len(tokens) and tokens[pos].tag is self.tag:
            return Result(tokens[pos].text, pos + 1)
        else:
            return None


class Concat(Parser):
    def __init__(self, left: Parser, right: Parser):
        self.left = left
        self.right = right

    def __call__(self, tokens: list, pos: int) -> Result:
        left_result = self.left(tokens, pos)
        if left_result:
            right_result = self.right(tokens, left_result.pos)
            if right_result:
                combined_value = (left_result.value, right_result.value)
                return Result(combined_value, right_result.pos)
        return None


class Alternate(Parser):
    def __init__(self, left: Parser, right: Parser):
        self.left = left
        self.right = right

    def __call__(self, tokens: list, pos: int) -> Result:
        left_result = self.left(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.right(tokens, pos)
            return right_result


class Process(Parser):
    def __init__(self, parser: Parser, function):
        self.parser = parser
        self.function = function

    def __call__(self, tokens: list, pos: int) -> Result:
        result = self.parser(tokens, pos)
        if result:
            result.value = self.function(result.value)
            return result


class Opt(Parser):
    def __init__(self, parser: Parser):
        self.parser = parser

    def __call__(self, tokens: list, pos: int) -> Result:
        result = self.parser(tokens, pos)
        if result:
            return result
        else:
            return Result(None, pos)


class Rep(Parser):
    def __init__(self, parser: Parser):
        self.parser = parser

    def __call__(self, tokens: list, pos: int) -> Result:
        results = []
        result = self.parser(tokens, pos)
        while result:
            results.append(result.value)
            pos = result.pos
            result = self.parser(tokens, pos)
        return Result(results, pos)


class Lazy(Parser):
    def __init__(self, parser_func):
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens: list, pos: int) -> Result:
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)


class Phrase(Parser):
    def __init__(self, parser: Parser):
        self.parser = parser

    def __call__(self, tokens: list, pos: int) -> Result:
        result = self.parser(tokens, pos)
        if result and result.pos < len(tokens):
            logging.error("Not all tokens parses: %s (%s)", result.value, result.pos)
            return Result(None, 0)
        return result
