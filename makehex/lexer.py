import re
import logging
import sys

from makehex.tools import debug_point


class Token:
    def __init__(self, regexp: str, tag=None):
        self.regexp = re.compile(regexp)
        self.tag = tag

    def match(self, string: str, pos: int, line: int):
        value = self.regexp.match(string, pos)
        if value:
            return Tok(self, value, line)
        return None

    def __repr__(self):
        return "<Token %s regexp='%s'>" % (self.tag, self.regexp)


class Tok:
    @debug_point("Tok")
    def __init__(self, parent, value, line: int):
        self.text = value.group(1)
        self.tag = parent.tag
        self.regexp = parent.regexp
        self.skip = not parent.tag
        self.pos = value.end(0)
        self.line = line + self.text.count('\n')

    def __repr__(self):
        return "<Tok %s text='%s'>" % (self.tag, self.text)


_expressions = (
    Token(r'([ \n\t;]+)'),
    Token(r'^#!([^\n]*)'),
    Token(r'//([^\n]*)'),
    Token(r'/\*((?:.|\n)*?)\*/'),

    Token(r'#@(end)',                               'END'),
    Token(r'#@([A-Za-z_][A-Za-z0-9_]*)',            'BLOCK'),
    Token(r'#([A-Za-z_][A-Za-z0-9_]*)',             'CALL'),

    Token(r'(\()',                                  'RESERVED'),
    Token(r'(\))',                                  'RESERVED'),

    Token(r'"([^"]*)"',                             'STRING'),
    Token(r"'([^']*)'",                             'CHARS'),
    Token(r'([0-9A-Fa-f]{2})',                      'HEX'),
    Token(r'\.([A-Za-z0-9_]+)',                     'NAME'),
    Token(r'([A-Za-z0-9_]+)',                       'VA_NAME'),
)


def lex(characters: str) -> list:
    pos = 0
    line = 1
    tokens = []
    characters = characters.replace("\\\n", " ").replace("\\\\", "\\")
    logging.debug("Tokenizing chars '%s'", characters.replace('\n', '\\n'))
    while pos < len(characters):
        found = None
        for token_expr in _expressions:
            found = token_expr.match(characters, pos, line)
            if found:
                if not found.skip:
                    tokens.append(found)
                break
        if not found:
            logging.critical('Illegal character "%s" at %s (line %s)', characters[pos], pos, line)
            sys.exit(10)
        else:
            pos, line = found.pos, found.line
    return tokens
