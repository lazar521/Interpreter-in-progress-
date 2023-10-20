from parserFile import Parser
from lexerFile import Lexer
from nodeFile import Node
from syntaxTreeFile import SyntaxTree


with open("/home/lazar521/desktop/projects/python/Compiler/inputFile", 'r') as file:
    text = file.read()

tokens = Lexer().makeTokens(text)
parser = Parser()
ast = SyntaxTree( parser.parseTokens(tokens) )

Node.printAttributes(nodeType=".node")

ast.traverseTree()
