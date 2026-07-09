import json

from ocr import recognize_code
from heal import heal_code
from parser import parse_code


def looks_like_code(text):

    keywords = [

        "int",
        "float",
        "double",
        "char",
        "void",
        "if",
        "else",
        "for",
        "while",
        "return",
        "#include",
        "cout",
        "cin",
        "printf",
        "scanf",
        "class",
        "public"

    ]

    return any(word in text for word in keywords)


image = "CODE_CANVAS/sample.png"

print("=" * 40)
print("Running OCR")
print("=" * 40)

text = recognize_code(image)

print("\nOCR Output:\n")
print(text)

print("\n" + "=" * 40)

if looks_like_code(text):

    print("Mode : CODE")

    healed = heal_code(text)

    print("\nHealed Code:\n")

    print(healed)

    ast = parse_code(healed)

    with open("output/ast.json", "w") as f:
        json.dump(ast, f, indent=4)

    print("\nAST saved in output/ast.json")

else:

    print("Mode : TEXT")

    print("\nNo AST generated because the image contains handwritten text, not source code.")