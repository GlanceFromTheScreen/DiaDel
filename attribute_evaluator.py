from dsl_info import *


def __RemoveNones(attributes):
    return [attribute for attribute in attributes if attribute]


def __Multiple(attributes):
    attributes = __RemoveNones(attributes)
    res = 1
    for num in attributes:
        res *= num
    return res


def __Add(attributes):
    attributes = __RemoveNones(attributes)
    res = 0
    for num in attributes:
        res += num
    return res

def __Substr(attributes):
    attributes = __RemoveNones(attributes)
    res = 0
    for num in attributes:
        res -= num
    return res

def __Kostil(attributes):
    return "kostil"


attributesMap = {
    Nonterminal.DIADEL_PROG: __Kostil,
    Nonterminal.LINE: __Kostil
}