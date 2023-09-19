
from parserFile import Parser


with open("/home/lazar521/Desktop/Projects/Python/Compiler/inputFile", 'r') as file:
    text = file.read()

parser = Parser(text)

parser.printTokens()