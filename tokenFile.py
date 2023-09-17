from tokenTypesFile import *


class Token:
    def __init__(self, tokenStr):
        self.tokenType = self.deduceType(tokenStr)
        self.value = tokenStr

    def __repr__(self):
        return str(self.value)


    def deduceType(self, tokenStr):    # razmisli kako ces ovo uraditi treba da se radi dedukcija tipa, ali da se ne pretrazuje 50 puta po nekim listama
        if tokenStr in ["::", "[", "]", "(", ")", "{", "}", ";"]:
            return self.deduceSpecialSymbol(tokenStr)

        elif tokenStr in r"-+/*=<>!&|":
        #elif tokenStr in ["->", "
            return self.deduceOperator(tokenStr)

        else:
            return self.deduceWord(tokenStr)


    def deduceSpecialSymbol(self, tokenStr):
        if tokenStr == "::":
            return NAMESPACE_OPERATOR
        elif tokenStr == "[":
            return LEFT_BRACKET
        elif tokenStr == "]":
            return RIGHT_BRACKET
        elif tokenStr == "(":
            return LEFT_PAREN
        elif tokenStr == ")":
            return RIGHT_PAREN
        elif tokenStr == "{":
            return LEFT_BRACES
        elif tokenStr == "}":
            return RIGHT_BRACES
        elif tokenStr == ";":
            return SEMICOLON


    def deduceOperator(self, tokenStr):
        if tokenStr == "->":
            return ARROW_OPERATOR
        elif tokenStr in ["!=", "==", ">", "=>", "<", "=<"]:
            return COMPARISON_OPERATOR
        elif tokenStr in


    def deduceWord(self, tokenStr):
        pass