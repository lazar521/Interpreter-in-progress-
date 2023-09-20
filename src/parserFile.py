from nodeFile import *
from enum import Enum


IDENTIFIER = 1
LITERAL = 2
NUM_LITERAL = 3


class Parser:
    keywords = ["let","def"]
 

    def parseTokens(self, tokens):
        self.tokenIndex = 0
        self.lineNumber = 1
        self.tokens = tokens
        self.skipNewline()
        self.root = self.parseProgram()
        
        return self.root


    def skipNewline(self):
        while self.hasTokens() and self.getToken() == "\n":
            self.lineNumber += 1
            self.advance()


    def hasTokens(self):
        return self.tokenIndex < len(self.tokens) - 1


    def advance(self):     ## advance doesnt skip newline characters 
        if self.hasTokens():
            self.tokenIndex += 1
        else:
            signalError("No more tokens")    


    def getToken(self):
        return self.tokens[self.tokenIndex]


    def tryMatch(self, matchType, string=None)->bool:
        if matchType == IDENTIFIER:
            return self.matchIdentifier()
        
        elif matchType == LITERAL:
            return self.matchLiteral(string)
        
        elif matchType == NUM_LITERAL:
            return self.matchNumericLiteral()

        else:
            print("unknown matching")
            return False


    def forceMatch(self, matchType, string = None)->None:
        if not self.tryMatch(matchType, string):
            self.signalError("Cannot match token: " + self.getToken())



    def matchLiteral(self,string):
        if self.getToken() == string:
            return True
        
        return False


    def matchIdentifier(self):
        token = self.getToken()
        
        for letter in token:
            if not letter.isalnum() and letter != "_":
                return False
        
        if token in Parser.keywords:
            return False

        return True


    def matchNumericLiteral(self):
        print("MATCHING NUMERIC LITERAL")


    def signalError(self,string):
        print("Line " + str(self.lineNumber) + " error: " + string)
        exit(-1)


##################  PARSING  ##################


    def parseProgram(self):
        while self.hasTokens():
            
            if self.tryMatch(LITERAL,"def" ):
                self.advance()
                self.parseFunction()

            elif self.forceMatch(LITERAL,"let"):
                self.advance()
                self.parseExpression()

        

    def parseFunction(self):
        typeSpec = self.parseFunctionTypeSpecifier()
        
        self.forceMatch(IDENTIFIER)
        identifier = self.getToken()
        self.advance()
        
        self.forceMatch(LITERAL,"(")
        self.advance()

        arguments = self.parseArguments()
        
        self.forceMatch(LITERAL,")")
        self.advance()



    def parseFunctionTypeSpecifier(self):
        if not self.tryMatch(LITERAL,"int"):
            self.forceMatch(LITERAL,"void")

        typeSpecifier = self.getToken() 
        self.advance()

        if self.tryMatch(LITERAL,'*'):
            typeSpecifier += '*'
            self.advance()

        return typeSpecifier


    def parseExpression(self):
        self.signalError("Parsing an expression")


    
    def parseArguments(self):
        arguments = []

        if self.tryMatch(IDENTIFIER):
            arguments.append(self.getToken())
            self.advance()

            while self.tryMatch(LITERAL, ","):
                self.advance()

                self.forceMatch(IDENTIFIER)
                arguments.append(self.getToken())
                self.advance()

        return arguments