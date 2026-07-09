import re

def heal_code(code):

    while code.count("(") > code.count(")"):
        code += ")"

    while code.count("{") > code.count("}"):
        code += "\n}"

    while code.count("[") > code.count("]"):
        code += "]"

    code = re.sub(r"\s+", " ", code)

    return code