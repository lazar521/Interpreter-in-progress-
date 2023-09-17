from lexerFile import Lexer



with open("inputFile", 'r') as file:
    text = file.read()

lexer = Lexer(text)


while lexer.hasTokens():
    print(lexer.getToken(),end="  ")
    lexer.advance()
