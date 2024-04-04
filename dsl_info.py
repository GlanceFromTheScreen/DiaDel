from enum import Enum


class Terminal(Enum):
    user_class_name = "user_class_name"
    terminator = "terminator"
    STR = "STR"
    INT = "INT"
    # ID = "ID"
    # TEXT = "TEXT"


tokenRegularExpressions = [
    (Terminal.terminator, r"id=|text=|[\,\{\}\;\#]"),
    (Terminal.user_class_name, r"[a-z=><]+"),
    (Terminal.STR, r'"[^"]*"'),
    (Terminal.INT, r"[0-9]+"),
]


keys = [
    ("id=", Terminal.terminator),
    ("text=", Terminal.terminator),
    (",", Terminal.terminator),
    (";", Terminal.terminator),
    ("{", Terminal.terminator),
    ("}", Terminal.terminator),
    ("\"", Terminal.terminator),
    ("#", Terminal.terminator),
]


class Nonterminal(Enum):
    USER_CLASS = 'USER_CLASS'
    CONNECTION = 'CONNECTION'
    INSTANCE = 'INSTANCE'


axiom = Nonterminal.INSTANCE
