from scanner import *
from afterscan.afterscan import Afterscan

from scanner import Tokenize
from afterscan.afterscan import Afterscan
from dsl_token import *
from syntax import *
import dsl_info
import attributor
import attribute_evaluator

from argparse import ArgumentParser
import json
import pathlib
import os
import shutil
import re

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need only one argument: program text path")
        sys.exit()

    with open(sys.argv[1], 'r') as file:
        tokenList = Tokenize(file.read())
        print("tokens:")
        for i, token in enumerate(tokenList):
            print(f"{i} TYPE: '{token.terminalType.name}', STRING: '{token.str}'.")
        print()

        tmp = Afterscan(tokenList)
        for i, token in enumerate(tmp):
            print(f"{i} TYPE: '{token.terminalType.name}', STRING: '{token.str}'.")
        print()

    with open("C:\\Users\\Le\\Desktop\\AppMath\\DiaDeL\\CODE\\dsl_generator\\_examples\\expression\\expression.json", 'r') as jsonFile:
        jsonData = json.loads(jsonFile.read())

    syntaxInfo = GetSyntaxDesription(jsonData["syntax"])

    tokenList = Afterscan(tokenList)
    ast = BuildAst(syntaxInfo, dsl_info.axiom, tokenList)
    attributor.SetAttributes(ast, attribute_evaluator.attributesMap)
    print()


