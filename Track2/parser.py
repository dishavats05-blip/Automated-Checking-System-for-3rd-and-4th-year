from tree_sitter_languages import get_parser

parser = get_parser("cpp")


def node_to_dict(node):

    return {
        "type": node.type,
        "start": node.start_point,
        "end": node.end_point,
        "children": [
            node_to_dict(child)
            for child in node.children
        ]
    }


def parse_code(code):

    tree = parser.parse(bytes(code, "utf8"))

    return node_to_dict(tree.root_node)