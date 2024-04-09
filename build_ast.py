from syntax import *
import graphviz
import os
import requests
import webbrowser

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


def tree_traverse(types_dict, objects, ast):
    vars_dict = {}
    connections_list = []
    connections_dict = {}
    for connection in ast.childs:
        if hasattr(connection, 'nonterminalType') and connection.nonterminalType.name == 'CONNECTION':
            ids = []
            for user_class in [connection.childs[0], connection.childs[4]]:
                if user_class.childs[3].attribute in vars_dict.keys():
                    pass
                else:
                    vars_dict[user_class.childs[3].attribute] = {
                        'text': user_class.childs[6].attribute if len(user_class.childs) > 5 else "",
                        'shape': objects[types_dict[user_class.childs[0].attribute]]['shape'],
                        'color': objects[types_dict[user_class.childs[0].attribute]]['color'],
                        'include': [],
                        'style': objects[types_dict[user_class.childs[0].attribute]]['style']
                    }
                ids.append(user_class.childs[3].attribute)
            if types_dict[connection.childs[2].childs[0].attribute] == 'ARROW':
                connections_list += [ids]
                connections_dict[tuple(ids)] = connection.childs[2].childs[3].attribute if len(connection.childs[2].childs) > 4 else ""
            if types_dict[connection.childs[2].childs[0].attribute] == 'INCLUDE':
                vars_dict[ids[0]]['include'].append(ids[1])

    return vars_dict, connections_dict


def get_dot_str(dict_, arrow_dict):
    object_dict = {}
    include_dict = {}
    init_str = f""""""
    for key, value in dict_.items():

        object_dict[key] = f'A{key}[label="{dict_[key]["text"]}", shape={dict_[key]["shape"]}, style={dict_[key]["style"] if dict_[key]["style"] else 0}, color={dict_[key]["color"]}]'

        if not dict_[key]['include']:
            init_str += object_dict[key] + '\n'+' '
        else:
            include_dict[key] = f""" subgraph cluster_A{key} {{ label="{dict_[key]['text']}" color={dict_[key]['color']}
            """
    for key, value in include_dict.items():
        for include_item in dict_[key]['include']:
            include_dict[key]+=object_dict[include_item] + ' '
        include_dict[key]+="}"
    include_str = """"""
    for include_item in include_dict.values():
        include_str+=include_item
    arrow_str = """"""
    for key,value in arrow_dict.items():
        arrow_str+=f'A{key[0]}->A{key[1]} [label="{value}"] \n'
    result_str = 'digraph G{ \n'+init_str + '\n' + include_str + '\n' + arrow_str + '}'
    print(result_str)
    response = requests.get('https://quickchart.io/graphviz?graph='+result_str)
    webbrowser.open(response.url)





