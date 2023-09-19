from lexerFile import Lexer


class Parser:
    def __init__(self,inputCode):
        self.lexer = Lexer(inputCode)
        self.lineNumber = 1
        self.root = None
        

    def printTokens(self):
        while self.lexer.hasTokens():
            print(self.lexer.getToken(),end="  ")
            token = self.lexer.getToken()
            self.lexer.advance()


    def eatToken(self):
        while self.lexer.getToken().getValue() == '\n':
            self.lexer.advance()
            self.lineNumber += 1
        return self.lexer.getToken() 


    def match(self, string):
        if string != self.lexer.getToken():
            return False
        else:
            self.lexer.advance()
            return True


    def parseStart(self):
        pass
