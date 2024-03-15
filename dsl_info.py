from enum import Enum


class Terminal(Enum):
    user_class = "user_class"
    diadel_class = "diadel_class"
    terminator = "terminator"


tokenRegularExpressions = [
    (Terminal.user_class, r"[a-zA_Z0-9]+"),
    (Terminal.diadel_class, r"&[a-zA_Z0-9]+"),
    (Terminal.terminator, r"[\;\:]")
]


keys = [
    (":", Terminal.terminator),
    (";", Terminal.terminator),
]


class Nonterminal(Enum):
    DIADEL_PROG = 'DIADEL_PROG'
    LINE = 'LINE'


axiom = Nonterminal.DIADEL_PROG