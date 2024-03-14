from enum import Enum


class Terminal(Enum):
    number = "number"
    operation = "operation"
    terminator = "terminator"


tokenRegularExpressions = [
    (Terminal.number, r"[1-9]\d*"),
    (Terminal.operation, r"[\+\*\-]"),
    (Terminal.terminator, r",")
]


keys = [
    ("+", Terminal.operation),
    ("*", Terminal.operation),
    ("-", Terminal.operation),
    (",", Terminal.terminator),
]


class Nonterminal(Enum):
    EXPRESSIONS = 'EXPRESSIONS'
    EXPRESSION = 'EXPRESSION'
    EXPRESSION1 = 'EXPRESSION1'
    TERM = 'TERM'


axiom = Nonterminal.EXPRESSIONS