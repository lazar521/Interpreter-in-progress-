from constants import *

class Lexer:
#------------- PUBLIC SECTION -------------------------------
    def makeTokens(self, text):
        self.text = text
        self.charPos = 0
        self.lineNumber = 1
        self.tokens = []

        while not self._isFinished():
            char = self._getChar()

            if char in r"[](){};:,":
                self._tokenizeSpecialSymbol()

            elif char in r"-+/*=<>!&|":
                self._tokenizeOperator()

            elif char.isalpha() or char == r"_":
                self._tokenizeIdentifier()

            elif char in "0123456789":
                self._tokenizeLiteral()

            elif char in " \n":
                self._handleBlankSpaces()

            elif char == "#":
                self._handleComments()

            else:
                self.handleUnexpectedSymbol()

        self.tokens.append(EOF)
        return self.tokens


#--------------- PRIVATE SECTION ----------------------------
    def _advanceChar(self):
        self.charPos += 1


    def _isFinished(self):
        return self.charPos >= len(self.text)


    def _addToken(self, newToken):
        self.tokens.append(newToken)
        


    def _getChar(self):
        return self.text[self.charPos]


    def _getNextChar(self):
        if self.charPos + 1 < len(self.text):
            return self.text[self.charPos + 1]
        else: 
            return None


    

    
    def _tokenizeSpecialSymbol(self):
        char = self._getChar()
        tokenStr = char

        if char == ":":
            nextChar = self._getNextChar()
            if nextChar == ":":
                tokenStr = "::"
                self._advanceChar()
            else:
                self.handleUnexpectedSymbol()

        self._addToken(tokenStr)
        self._advanceChar()


    def _tokenizeOperator(self):
        char = self._getChar()
        tokenStr = char

        if char in "!-&|=+":
            nextChar = self._getNextChar()
            complexOperator = char + nextChar

            if complexOperator in ["!=", "&&", "||", "->", "==","++","--"]:
                tokenStr += nextChar
                self._advanceChar()

        self._addToken(tokenStr)
        self._advanceChar()


    def _tokenizeIdentifier(self):
        char = self._getChar()
        tokenStr = ""

        while char.isalnum() or char == "_":
            tokenStr += char
            self._advanceChar()
            char = self._getChar()

        self._addToken(tokenStr)


    def _tokenizeLiteral(self):
        char = self._getChar()
        tokenStr = ""

        while char in "0123456789":
            tokenStr += char
            self._advanceChar()
            char = self._getChar()

        self._addToken(tokenStr)


    def _handleBlankSpaces(self):
        char = self._getChar()

        if char == '\n':
            self._addToken("\n")
            self.lineNumber += 1

        self._advanceChar()


    def _handleComments(self):
        while not self._isFinished() and self._getChar() != "\n":
            self._advanceChar()


    def handleUnexpectedSymbol(self):
        char = self._getChar()
        print("Line " + str(self.lineNumber) + ": Invalid character: \'" + char + "\'")
        exit()





