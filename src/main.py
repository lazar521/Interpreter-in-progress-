from parserFile import Parser
from lexerFile import Lexer

with open("/home/lazar521/desktop/projects/python/Compiler/inputFile", 'r') as file:
    text = file.read()

tokens = Lexer().makeTokens(text)
parser = Parser()
ast = parser.parseTokens(tokens)

