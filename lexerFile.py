from tokenFile import Token

class Lexer:
#------------- PUBLIC SECTION -------------------------------
    def __init__(self, text):
        self.text = text
        self.charPos = 0
        self.tokens = []
        self._makeTokens()
        self.tokenPos = 0
        self.lineNumber = 0


    def getToken(self):
        if self.tokenPos >= len(self.tokens):
            print("No more tokens error")
            return None

        return self.tokens[self.tokenPos]


    def advance(self):        # advance() should keep track of lineNumber
        self.tokenPos += 1



    def hasTokens(self):
        return self.tokenPos < len(self.tokens)


#--------------- PRIVATE SECTION ----------------------------
    def _advanceChar(self):
        self.charPos += 1


    def _isFinished(self):
        return self.charPos >= len(self.text)


    def _addToken(self, tokenStr):
        newToken = Token(tokenStr)
        self.tokens.append(newToken)


    def _getChar(self):
        return self.text[self.charPos]


    def _getNextChar(self):
        if self.charPos + 1 < len(self.text):
            return self.text[self.charPos + 1]
        else: 
            return None


    def _makeTokens(self):

        while not self._isFinished():
            char = self._getChar()

            if char in r"[](){};:":
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

    
    def _tokenizeSpecialSymbol(self):
        char = self._getChar()
        tokenStr = char


        if char == ":":
            nextChar = self._getNextChar()
            if nextChar == ":":
                tokenStr += nextChar
                self._advanceChar()
            else:
                self.handleUnexpectedSymbol()

        self._addToken(tokenStr)
        self._advanceChar()


    def _tokenizeOperator(self):
        char = self._getChar()
        tokenStr = char

        if char in "!-&|=":
            nextChar = self._getNextChar()
            complexOperator = char + nextChar
            if complexOperator in ["!=", "&&", "||", "->", "=="]:
                tokenStr += nextChar
                self._advanceChar()

        self._addToken(tokenStr)
        self._advanceChar()


    def _tokenizeIdentifier(self):
        char = self._getChar()
        tokenStr = ""

        while char.isalnum() or char in "_":
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
        self._advanceChar()


    def _handleComments(self):
        while not self._isFinished() and self._getChar() != "\n":
            self._advanceChar()


    def handleUnexpectedSymbol(self):
        char = self._getChar()
        print("Invalid character: \'" + char + "\'")
        exit()





