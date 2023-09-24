from parserFile import Parser
from lexerFile import Lexer

with open("/home/lazar521/Desktop/Projects/Python/Compiler/inputFile", 'r') as file:
    text = file.read()

tokens = Lexer().makeTokens(text)
parser = Parser()
ast = parser.parseTokens(tokens)

