from scanner import Tokenize
from afterscan import Afterscan
from dsl_token import *
from syntax import *
import dsl_info
import attributor
import attribute_evaluator

import graphviz
from argparse import ArgumentParser
import json
import pathlib
import os

#  python .\build_ast.py -c C:\Users\Le\Desktop\expr.txt -j C:\Users\Le\Desktop\AppMath\DiaDeL\CODE\dsl_generator\_examples\expression\diadel.json

os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'


def __RenderTokenStream(diagramName, tokenList, debugInfoDir):
    if debugInfoDir is None:
        return
    h = graphviz.Digraph(diagramName, format='svg')
    h.node('0', '', shape='point')
    i = 1
    for token in tokenList:
        if Token.Type.TERMINAL == token.type:
            h.node(str(i),
                   f"TERMINAL\ntype: {token.terminalType.name}\nstring: {token.str}" + (
                       f"\nattribute: {token.attribute}" if token.attribute else ""),
                   shape='diamond')
        elif Token.Type.KEY == token.type:
            h.node(str(i), f"KEY\nstring: {token.str}" + (f"\nattribute: {token.attribute}" if token.attribute else ""),
                   shape='oval')
        h.edge(str(i - 1), str(i))
        i += 1
    h.node(str(i), '', shape='point')
    h.edge(str(i - 1), str(i))
    h.render(directory=debugInfoDir, view=True)


def __RenderAst(diagramName, ast, debugInfoDir):
    if debugInfoDir is None:
        return
    h = graphviz.Digraph(diagramName, format='svg')
    i = 1
    nodes = [(ast, 0)]
    while len(nodes):
        node = nodes[0]
        if TreeNode.Type.NONTERMINAL == node[0].type:
            h.node(str(i),
                   f"NONTERMINAL\ntype: {node[0].nonterminalType}" + (
                       f"\nattribute: {node[0].attribute}" if node[0].attribute else ""),
                   shape='box')
            if node[1] != 0:
                h.edge(str(node[1]), str(i))
            nodes += [(child, i) for child in node[0].childs]
        else:
            token = node[0].token
            if Token.Type.TERMINAL == token.type:
                h.node(str(i),
                       f"TERMINAL\ntype: {token.terminalType.name}\nstring: {token.str}" + (
                           f"\nattribute: {token.attribute}" if token.attribute else ""),
                       shape='diamond')
            elif Token.Type.KEY == token.type:
                h.node(str(i),
                       f"KEY\nstring: {token.str}" + (f"\nattribute: {token.attribute}" if token.attribute else ""),
                       shape='oval')
            h.edge(str(node[1]), str(i))
        nodes = nodes[1:]
        i += 1
    h.render(directory=debugInfoDir, view=True)


def __GetRCode(node):
    key = "$ATTRIBUTE$"
    if TreeNode.Type.NONTERMINAL != node.type:
        return ""
    res = node.commands[0]
    if -1 != res.find(key):
        raise RuntimeError("Attribute must not be used in first edge")
    for i in range(len(node.childs)):
        childCode = __GetRCode(node.childs[i])
        if len(childCode) != 0:
            res = res + ("\n" if len(res) != 0 else "") + childCode
        if len(node.commands[i + 1]) != 0:
            res = res + ("\n" if len(res) != 0 else "") + node.commands[i + 1].replace(key,
                                                                                       repr(node.childs[i].attribute))
    return res


def tree_processing(ast):
    """
    здесь стоит заглушка. По ключу должна быть не строка, а объект - графический примитив
    """
    d = {}
    for item in ast.childs:
        try:
            line = item.nonterminalType.name
            d[item.childs[0].attribute] = item.childs[2].attribute
        except Exception:
            pass
    return d


"""
{
    1: {'text': 'start', 'shape': rect, 'color': black, 'include': [3,4]},
    2: {'text': 'end', 'shape': rect, 'color': black, 'include': []},
}

[
    (1,2),
]
"""

types_dict = {
    'state': 'RECT',
    'arrow': 'ARROW',
    'include': 'INCLUDE',
    'automata': 'RECT',
    'start': 'CIRCLE',
    'action': 'RECT',
    'end': 'CIRCLE',
    '=>': 'ARROW',
    'variables': 'CIRCLE'
}

objects = {
    'RECT': {'shape': 'rect', 'color': 'black'},
    'CIRCLE': {'shape': 'circle', 'color': 'blue'}
}


def tree_traverse(ast):
    vars_dict = {}
    connections_list = []
    for connection in ast.childs:
        if hasattr(connection, 'nonterminalType') and connection.nonterminalType.name == 'CONNECTION':
            ids = []
            for user_class in [connection.childs[0], connection.childs[4]]:
                if user_class.childs[3].attribute in vars_dict.keys():
                    pass
                else:
                    vars_dict[user_class.childs[3].attribute] = {
                        'text': user_class.childs[6].attribute if len(user_class.childs) > 5 else '""',
                        'shape': objects[types_dict[user_class.childs[0].attribute]]['shape'],
                        'color': objects[types_dict[user_class.childs[0].attribute]]['color'],
                        'include': []
                    }
                ids.append(user_class.childs[3].attribute)
            if types_dict[connection.childs[2].childs[0].attribute] == 'ARROW':
                connections_list += [ids]
            if types_dict[connection.childs[2].childs[0].attribute] == 'INCLUDE':
                vars_dict[ids[0]]['include'].append(ids[1])

    return vars_dict, connections_list

def get_dot_str(dict_, arr_):
    object_dict = {}
    include_dict = {}
    init_str = f""""""
    for key, value in dict_.items():

        object_dict[key] = f'A{key}[label={dict_[key]["text"]}, shape={dict_[key]["shape"]}, color={dict_[key]["color"]}]'

        if not dict_[key]['include']:
            init_str += object_dict[key] + '\n'+' '
        else:
            include_dict[key] = f""" subgraph A{key} {{ label={dict_[key]['text']} color={dict_[key]['color']}
            """
    for key, value in include_dict.items():
        for include_item in dict_[key]['include']:
            include_dict[key]+=object_dict[include_item] + ' '
        include_dict[key]+="}"
    include_str = """"""
    for include_item in include_dict.values():
        include_str+=include_item
    arrow_str = """"""
    for tup in arr_:
        arrow_str+=f'A{tup[0]}->A{tup[1]}\n'
#         print(arrow_str)
    result_str = 'digraph G{ \n'+init_str + '\n' + include_str + '\n' + arrow_str + '}'
    print(result_str)


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

tokenList = Tokenize(code)
__RenderTokenStream('token_stream_after_scanner', tokenList, debugInfoDir)
tokenList = Afterscan(tokenList)
__RenderTokenStream('token_stream_after_afterscan', tokenList, debugInfoDir)

ast = BuildAst(syntaxInfo, dsl_info.axiom, tokenList)
__RenderAst('ast', ast, debugInfoDir)
attributor.SetAttributes(ast, attribute_evaluator.attributesMap)
__RenderAst('ast_attributed', ast, debugInfoDir)

# processed_tree = tree_processing(ast)
# print(processed_tree)
vars, conns = tree_traverse(ast)
print('\nDOT CODE:\n')
get_dot_str(vars, conns)

if debugInfoDir is not None and "semantics" in jsonData and "virt" == jsonData["semantics"]["type"]:
    rCode = __GetRCode(ast)
    with open(f"{debugInfoDir}/r_code.py", 'w') as codeFile:
        codeFile.write(rCode)
