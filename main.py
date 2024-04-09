from build_ast import *
from build_ast import __RenderAst
from scanner import Tokenize
from afterscan import Afterscan
from syntax import *
import dsl_info
import attributor
import attribute_evaluator
from argparse import ArgumentParser
import json
import pathlib
import os
from diadel_objects import objects

######################################################
# Ваша Diadel - программа (изменить)
######################################################

types_dict = {
    'state': 'RECT_DASHED',
    'arrow': 'ARROW',
    'include': 'INCLUDE',
    'automata': 'RECT',
    'start': 'CIRCLE_FILLED',
    'action': 'ELLIPSE',
    'end': 'CIRCLE_DOUBLE',
    '=>': 'ARROW',
    'variables': 'CIRCLE',
    'decision': 'DIAMOND_BLUE',
    'merge': 'RECT_DASHED'
}

######################################################
# Чтение экземпляра семантический модели
######################################################

parser = ArgumentParser(prog="create_ast", description="Create AST")
parser.add_argument("-c", "--code", dest="codeFile", help="File with code", metavar="FILE", required=True)
parser.add_argument("-j", "--json", dest="jsonFile", help="Json file with settings", metavar="FILE", required=True)
args = parser.parse_args()

with open(args.jsonFile, 'r') as jsonFile:
    jsonData = json.loads(jsonFile.read())

syntaxInfo = GetSyntaxDesription(jsonData["syntax"])

if "debugInfoDir" in jsonData:
    debugInfoDir = pathlib.Path(jsonData["debugInfoDir"])
    if not debugInfoDir.exists():
        os.mkdir(debugInfoDir)
else:
    debugInfoDir = None

with open(args.codeFile, 'r') as codeFile:
    code = codeFile.read()

######################################################
# Построение AST
######################################################

tokenList = Tokenize(code)
tokenList = Afterscan(tokenList)
ast = BuildAst(syntaxInfo, dsl_info.axiom, tokenList)
attributor.SetAttributes(ast, attribute_evaluator.attributesMap)
__RenderAst('ast_attributed', ast, debugInfoDir)

######################################################
# Результат
######################################################

tmp1, tmp2 = tree_traverse(types_dict, objects, ast)
get_dot_str(*tree_traverse(types_dict, objects, ast))

