from nodeFile import Node
from constants import *

class Parser:
    keywords = ["struct","for","while","void","int","if","else","return","func","var"]
    

    def parseTokens(self, tokens):
        self.tokens = tokens
        self.tokenPos = 0
        self.lineNumber = 1
        self.errorList = []

        while self.hasTokens() and self.getToken() == "\n":
            self.tokenPos += 1
            self.lineNumber += 1

        return self.parseProgram()


    def getLineNumber(self):
        return self.lineNumber

    def hasTokens(self):
        return self.getToken() != EOF


    def advance(self):     
        if self.hasTokens():
            self.tokenPos += 1

            while self.getToken() == "\n":
                self.tokenPos += 1
                self.lineNumber +=1

        else:
            print("No more tokens")    
            exit(-1)

    def getToken(self):
        return self.tokens[self.tokenPos]



    def match(self,string):
        if self.getToken() == string:
            self.advance()
            return True

        return False


    def parseIdentifier(self):
        token = self.getToken()
        
        if token[0].isnumeric():
            return None

        for letter in token:
            if not letter.isalnum() and letter != "_":
                return None
        
        if token in Parser.keywords:
            return None

        self.advance()
        return token

    def matchNum(self):
        if self.getToken().isnumeric():
            return True
        return False

    def parseNumericLiteral(self):             
        token = self.getToken()                     
        #print(token)
        if token.isnumeric():
            self.advance()
            return token 
        
        return None


    def error(self,message,line,printToken = True):
        if printToken:
            self.errorList.insert(0,"Line " + str(line) + " : " + message + " : Unmatched token: " + self.getToken())
        else:
            self.errorList.insert(0,"Line " + str(line) + " : " + message)

    def showErrors(self):
        print("AN ERROR HAS OCCURED")
        for error in self.errorList:
            print (error)

##################  PARSING  ##################


    # Program       -> DeclarationList
    
    def parseProgram(self):
        declarationList = self.parseDeclarationList()
        if declarationList == None:
            self.showErrors()
            return None 

        return Node("Program",\
                    ["declarations.list"],\
                    [declarationList])

        
    # DeclarationList -> Declaration
    #            | Declaration DeclarationList

    def parseDeclarationList(self):
        declarations = []

        while self.hasTokens():
            declaration = self.parseDeclaration()
            
            if declaration == None:
                return None

            declarations.append(declaration)

        return declarations



    # Declaration    -> VariableDeclarationStatement
    #            | FunctionDeclaration
    #            | StructDeclaration

    def parseDeclaration(self):
        line = self.getLineNumber()
        token = self.getToken()

        if token == "func":
            decl = self.parseFunctionDeclaration()
        elif token == "struct":
            decl = self.parseStructDeclaration()
        elif token == "var":
            decl = self.parseVariableDeclarationStatement()
        else:
            decl = None
            self.error("Cannot deduce declaration type",line)
            
        return decl



    def parseVariableDeclarationStatement(self):
        line = self.getLineNumber()

        declarataion = self.parseVariableDeclaration()
        if declarataion == None:
            return None
        
        if not self.match(";"):
            self.error("Variable declaration missing ';'" + line)
            return None
        
        return declarataion


    # VariableDeclarationStatement ->var TypeSpecifier Identifier 
    #                    | var TypeSpecifier Identifier [ ConditionalExpression ] 
    #                    | var TypeSpecifier Identifier = ConditionalExpression 

    def parseVariableDeclaration(self):
        line = self.getLineNumber()
        expr = None
        declType = "regular"

        if not self.match("var"):
            return None

        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            self.error("Invalid type specifier",line)
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Invalid identifier",line)
        
        if self.match("["):  
            expr = self.parseConditionalExpression()
            if expr == None:
                self.error("Invalid expression",line)
                return None

            if not self.match("]"):
                self.error("Missing ']'",line)
                return None
        
        elif self.match("="):
            expr = self.parseConditionalExpression()
            if expr == None:
                self.error("Invalid expression",line)
                return None

        return Node("VariableDeclaration",\
                    ["type.node","identifier.lit","expression.node","declarationType.lit"],\
                    [typeSpecifier,identifier,expr,declType])
        


    # TypeSpecifier -> int
    #           | struct Identifier
    #           | void

    def parseTypeSpecifier(self):
        line = self.getLineNumber()
        identifier = None
        dataType = None
        indirection = False

        for word in ["int","void","struct"]:
            dataType = word
            if self.match(dataType):
                break
        else:
            self.error("Unknown type ",line)
            return None

        if dataType == "struct":
            identifier = self.parseIdentifier()
            if identifier == None:    
                self.error("Invalid struct identifier",line)
                return None

        if self.match("*"):
            indirection = True

        return Node("TypeSpecifier",\
            ["type.node","identifier.lit","indirection.lit"],\
            [dataType,identifier,indirection])


    # FunctionDeclaration -> func TypeSpecifier Identifier ( ParameterList ) CompoundStatement

    # ParameterList -> Parameter
    #       | Parameter , ParameterList 

    def parseFunctionDeclaration(self):
        line = self.getLineNumber()

        if not self.match("func"):
            self.error("Function declaration missing 'func'",line)
            return None

        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            self.error("Invalid funciton type specifier",line)
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Invalid funciton identifier",line)
            return None

        if not self.match("("):
            self.error("Function declaration missing ')'",line)
            return None
        
        parameterList = []
        paramCnt = 0
        while not self.match(")"):
            if paramCnt > 0:
                    if not self.match(","):
                        self.error("Parameter list missing ','",line)
                        return None

            parameter = self.parseParameter()    # parameterList is optional so we dont need to check None case
            if parameter == None:
                self.error("Function declaration missing ')'",line)
                return None
            parameterList.append(parameter)
            paramCnt += 1

        
        statements = self.parseCompountStatement()
        if statements == None:
            self.error("Invalid function body",line,False)
            return None


        return Node("FunctionDeclaration",\
                    ["type.node","identifier.lit","parameterList.list","body.node"],\
                    [typeSpecifier,identifier,parameterList,statements])




    # Parameter     -> TypeSpecifier Identifier
    #       | TypeSpecifier Identifier [ ]
    
    def parseParameter(self):
        line = self.getLineNumber()
        isArray = False

        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            self.error("Invalid parameter type",line)
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Invalid parameter identifier",line)
            return None
        
        if self.match("["):
            if not self.match("]"):
                self.error("Parameter missing ']'")
                return None
            isArray = True
        
        
        return Node("Parameter",\
                    ["type.node","identifier.lit","isArray.lit"],\
                    [typeSpecifier,identifier,isArray])


    # StructDeclaration -> struct Identifier { MemberList } 

    def parseStructDeclaration(self):
        line = self.getLineNumber()

        if not self.match("struct"):
            self.error("Missing 'struct' keyword",line)
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Invalid identifier",line)
            return None
        
        if not self.match("{"):
            self.error("Struct declaration missing '{'",line)
            return None

        memberList = []
        while not self.match("}"):
            member = self.parseMember()
            if member == None:
                self.error("Invalid struct member or missing '}'",line)
                return None
            memberList.append(member)
        


        return Node("structDeclaration",\
                    ["identifier.lit","memberList.list"],\
                    [identifier,memberList])


    # MemberList    -> Member
    #       | Member MemberList



    # Member        -> TypeSpecifier Identifier ;
    #       | TypeSpecifier Identifier [ ConstantExpression ] ;

    def parseMember(self):
        line = self.getLineNumber()
        constantExpression = None
        isArray = False

        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            self.error("Invalid member type",line)
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Invalid member identifier",line)
            return None


        if self.match("["):
            if not self.match("]"):
                constantExpression = self.parseConditionalExpression()
                if constantExpression == None:
                    self.error("Invalid expression inside [ ]",line)

            if not self.match("]"):
                self.error("Member missing ']",line)
                return None
            isArray = True


        if not self.match(";"):
            self.error("Member missing ';'",line)
            return None

        return Node("member",\
                    ["type.node","identifier.lit","isArray.lit","expression.node"],\
                    [typeSpecifier,identifier,isArray,constantExpression])


    # CompoundStatement -> { StatementList }
        
    # StatementList -> Statement
    #       | Statement StatementList


    def parseCompountStatement(self):
        line = self.getLineNumber()

        if not self.match("{"):
            self.error("Missing '{'",line)
            return None
        
        statementList = []
        while not self.match("}"):
            statement = self.parseStatement()
            if statement == None:
                return None
            statementList.append(statement)
       
        return statementList



    # Statement     -> ExpressionStatement
    #       | IfStatement
    #       | WhileStatement
    #       | ForStatement
    #       | ReturnStatement
    #       | VariableDeclaration


    def parseStatement(self):
        line = self.getLineNumber()
        token = self.getToken()

        if token == "if":
            stmt = self.parseIfStatement()
        elif token == "while":
            stmt = self.parseWhileStatement()
        elif token == "for":
            stmt = self.parseForStatement()
        elif token == "return":
            stmt = self.parseReturnStatement()
        elif token == "var":
            stmt = self.parseVariableDeclarationStatement()
        else:
            stmt = self.parseExpressionStatement()


        return stmt

        
    # ExpressionStatement -> Expression ;

    def parseExpressionStatement(self):
        line = self.getLineNumber()

        expression = self.parseExpression()
        if expression == None:
            return None

        if not self.match(";"):
            self.error("Expression missing ';'",line)
            return None
        
        return expression
        

    # IfStatement   -> if ( Expression ) CompoundStatement
    #               | if ( Expression ) CompoundStatement else CompoundStatement

    def parseIfStatement(self):
        line = self.getLineNumber()

        if not self.match("if"):
            self.error("Missing 'if' keyword",line)
            return None
        
        if not self.match("("):
            self.error("If statement missing '('",line)
            return None

        condition = self.parseConditionalExpression()
        if condition == None:
            self.error("If statement invalid condition",line)
            return None
        
        if not self.match(")"):
            self.error("If statement missing ')'",line)
            return None
        
        body = self.parseCompountStatement()
        if body == None:
            self.error("If statement invalid body",line,False)
            return None

        
        elseBody = None
        if self.match("else"):
            elseBody = self.parseCompountStatement()
            if elseBody == None:
                self.error("If statement else branch has invalid body",line,False)
                return None
        
    
        return Node("ifStatement",\
                    ["condition.node","body.node","elseBody.node"],\
                    [condition,body,elseBody])


    # WhileStatement -> while ( Expression ) CompoundStatement

    def parseWhileStatement(self):
        line = self.getLineNumber()

        if not self.match("while"):
            self.error("Missing 'while' keyword",line)
            return None
        
        if not self.match("("):
            self.error("While statement missing '('")
            return None
        
        condition = self.parseConditionalExpression()
        if condition == None:
            self.error("While statement invalid condition",line,False)
            return None

        if not self.match(")"):
            self.error("While statement missing ')'",line)
            return None
        
        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            self.error("While statement invalid body",line,False)
            return None
        
        return Node("whileStatement",\
                    ["condition.node","body.node"],\
                    [condition,compoundStatement])


    # ForStatement   -> for ( <ForInitializer> ; Expression ; ForUpdater ) CompoundStatement

    def parseForStatement(self):
        line = self.getLineNumber()

        if not self.match("for"):
            self.error("Missing 'for' keyword",line)
            return None

        if not self.match("("):
            self.error("For statement missing '('",line)
            return None
        

        if not self.match(";"):
            forInitializer = self.parseForInitializer()
            if forInitializer == None:
                self.error("Invalid for initializer",line)
            
            if not self.match(";"):
                self.error("For stetement missing separator ';' after for condition",line)
                return None

        expression = self.parseExpression()    
        if expression == None:
            self.error("For statement missing condition",line)
            return None
        
        if not self.match(";"):
            self.error("For stetement missing separator ';' after for initializer",line)
            return None

        forUpdater = self.parseForUpdater()
        if forUpdater == None:
            self.error("For statement missing for updater",line)
            return None

        if not self.match(")"):
            self.error("For statement missing ')'")
            return None

        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            self.error("For statement invalid body",line)
            return None
 
        return Node("forStatement",\
                    ["forInitializer.node","condition.node","forUpdater.node","body.node"],\
                    [forInitializer,expression,forUpdater,compoundStatement])


    # ForInitializer ->  VariableDeclaration

    def parseForInitializer(self):
        return self.parseVariableDeclaration()


    # ForUpdater    -> AssignmentExpression

    def parseForUpdater(self):
        return self.parseAssignmentExpression()


    # ReturnStatement -> return ; 
    # 		| return ConditionalExpression ;

    def parseReturnStatement(self):
        line = self.getLineNumber()
        returnType = "void"

        if not self.match("return"):
            self.error("Missing 'return' keyword",line)
            return None
        
        if not self.match(";"):
            expr = self.parseConditionalExpression()
            if expr == None:
                self.error("Return statement invalid return value",line)
                return None

            if not self.match(";"):
                self.error("Return statement missing ';'",line)
                return None

        return Node("returnStatement",\
                        ["returnValue.node"],\
                        [expr])



    # Expression  -> let AssignmentExpression
    #       | ConditionalExpression
    
    def parseExpression(self): 
        if self.match("let"):
            return self.parseAssignmentExpression()

        return self.parseConditionalExpression()    



    # AssignmentExpression -> Identifier = Expression

    def parseAssignmentExpression(self):
        line = self.getLineNumber()

        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Assignment expression invalid left operator",line)
            return None
        
        if not self.match("="):
            self.error("Assignment expression missing '='",line)
            return None
        
        expr = self.parseExpression()
        if expr == None:
            self.error("Assignment expression invalid right operator",line)
            return None
        
        return Node("assingmentExpression",\
                    ["identifier.lit","expression.node"],\
                    [identifier,expr])


    # ConditionalExpression -> LogicalOrExpression

    def parseConditionalExpression(self):
        logicalOrExpr = self.parseLogicalOrExpression()
        if logicalOrExpr == None:
            return None
        
        return Node("conditionalExpression",\
                    ["body.node"],\
                    [logicalOrExpr])

    # LogicalOrExpression -> LogicalAndExpression
    #            | LogicalAndExpression || LogicalOrExpression

    def parseLogicalOrExpression(self):
        logicalAndExpr = self.parseLogicalAndExpression()
        if logicalAndExpr == None:
            return None
        
        if self.match("||"):
            operator = "||"
        else:
            return logicalAndExpr


        logicalOrExpr = self.parseLogicalOrExpression()
        if logicalOrExpr == None:
            return None


        return Node("binaryExpression",\
                    ["leftOP.node","operator.lit","rightOP.node"],\
                    [logicalAndExpr,operator,logicalOrExpr])
        


    # LogicalAndExpression -> EqualityExpression
    #         | EqualityExpression && LogicalAndExpression
    
    def parseLogicalAndExpression(self):
        equalityExpr = self.parseEqualityExpression()
        if equalityExpr == None:
            return None
        
        operator = None
        if self.match("&&"):
            operator == "&&"
        else:
            return equalityExpr


        logicalAndExpr = self.parseLogicalAndExpression()
        if logicalAndExpr == None:
            return None

        return Node("binaryExpression",\
                    ["leftOP.node","operator.lit","rightOP.node"],\
                    [equalityExpr,operator,logicalAndExpr])

        
    # EqualityExpression -> RelationalExpression
    #       | RelationalExpression == EqualityExpression
    #       | RelationalExpression != EqualityExpression

    def parseEqualityExpression(self):
        relationalExpr = self.parseRelationalExpression()
        if relationalExpr == None:
            None

        if self.match("=="):
            operator = "=="
        elif self.match("!="):
            operator = "!="
        else:
            return relationalExpr

        equalityExpr = self.parseEqualityExpression()
        if equalityExpr == None:
            return None

        return Node("binaryExpression",\
                    ["leftOP.node","operator.lit","rightOP.node"],\
                    [relationalExpr,operator,equalityExpr])
    
    
    # RelationalExpression -> AdditiveExpression
    #             | AdditiveExpression < RelationalExpression
    #             | AdditiveExpression > RelationalExpression
    #             | AdditiveExpression <= RelationalExpression
    #             | AdditiveExpression >= RelationalExpression
        
    def parseRelationalExpression(self):
        additiveExpr = self.parseAdditiveExpression()
        if additiveExpr == None:
            return None

        if self.match("<"):
            operator = "<"
        elif self.match(">"):
            operator = ">"
        elif self.match("<="):
            operator = "<="
        elif self.match(">="):
            operator = ">="
        else:
            return additiveExpr

        relationalExpr = self.parseRelationalExpression()
        if relationalExpr == None:
            return None

        return Node("binaryExpression",\
                    ["leftOP.node","operator.lit","rightOP.node"],\
                    [additiveExpr,operator,relationalExpr])

    
    # AdditiveExpression -> MultiplicativeExpression
    #           | MultiplicativeExpression + AdditiveExpression
    #           | MultiplicativeExpression - AdditiveExpression

    def parseAdditiveExpression(self):
        multiplicativeExpr = self.parseMultiplicativeExpression()
        if multiplicativeExpr == None:
            return None

        if self.match("+"):
            operator = "+"
        elif self.match("-"):
            operator = "-"
        else:
            return multiplicativeExpr
        
        additiveExpr = self.parseAdditiveExpression()
        if additiveExpr == None:
            return None
        
        return Node("binaryExpression",\
                    ["leftOP.node","operator.lit","rightOP.node"],\
                    [multiplicativeExpr,operator,additiveExpr])
        



    # MultiplicativeExpression -> UnaryExpression
    #               | UnaryExpression * MultiplicativeExpression
    #               | UnaryExpression / MultiplicativeExpression
    #               | UnaryExpression % MultiplicativeExpression

    def parseMultiplicativeExpression(self):
        unaryExpr = self.parseUnaryExpression()
        if unaryExpr == None:
            return None

        if self.match("*"):
            operator = "*"
        elif self.match("/"):
            operator = "/"
        elif self.match("%"):
            operator = "%"
        else:
            return unaryExpr
        
        multiplicativeExpr = self.parseMultiplicativeExpression()
        if multiplicativeExpr == None:
            return None
        
        return Node("binaryExpression",\
                    ["leftOP.node","operator.lit","rightOP.node"],\
                    [unaryExpr,operator,multiplicativeExpr])



    # UnaryExpression -> ! Term
#                      | & Term
#                      | * Term
#                      | - Term
#                      | Term

    def parseUnaryExpression(self):
        if self.match("-"):
            operator = "-"
        elif self.match("!"):
            operator = "!"
        elif self.match("&"):
            operator = "&"
        elif self.match("*"):
            operator = "*"
        else:
            operator = None
        
        term = self.parseTerm()
        if term == None:
            return None
        
        if operator == None:
            return term

        return Node("unaryExpression",\
                    ["operator.lit","term.node"],\
                    [operator,term])


    #       Term -> EnclosedTerm
    #               | NumericLiteral
    #               | PostfixExpression

    def parseTerm(self):
        token = self.getToken()

        if token == "(":
            return self.parseEnclosedTerm()

        if self.matchNum():
            return self.parseNumericLiteral()

        return self.parsePostfixExpression()


    #   EnclosedTerm -> ( ConditionalExpression )

    def parseEnclosedTerm(self):
        line = self.getLineNumber()

        if not self.match("("):
            self.error("Expression missing '('",line)
            return None
        
        conditionalExpr= self.parseConditionalExpression()
        if conditionalExpr == None:
            self.error("Invalid expression inside ( )",line,False)
            return None
        
        if not self.match(")"):
            self.error("Expression missing ')'",line)
            return None
        
        return conditionalExpr   

        

    # PostfixExpression -> Identifier 
    #             | Identifier [ ConditionalExpression ] 
    #             | Identifier -> Identifier
    #             | Identifier . Identifier
    #             | Identifier ( ArgumentList )


    def parsePostfixExpression(self):
        line = self.getLineNumber()

        identifier = self.parseIdentifier()
        if identifier == None:
            self.error("Invalid identifier",line)
            return None

        field = None

        if self.match("["):
            field = self.conditionalExpression()
            if field == None:
                self.error("Invalid expression inside [ ]",line)
                return None
            if not self.match("]"):
                self.error("Expression missing ']'",line)
                return None
            operator = "[]"            

        elif self.match("->"):
            field = self.parseIdentifier()
            if field == None:
                self.error("Invalid field specified after '->' operator ",line)
                return None
            operator = "->"
       
        elif self.match("."):
            field = self.parseIdentifier()
            if field == None:
                self.error("Invalid field specified after '.' operator",line)
                return None
            operator = "."

        elif self.match("("):
            argCnt = 0
            argumentsList = []

            while not self.match(")"):
                if argCnt > 0:
                    if not self.match(","):
                        self.error("Function call argument list missing ',",line)
                        return None
                
                argument = self.parseArgument()
                if argument == None:
                    self.error("Invalid function argument",line)
                    return None
                argumentsList.append(argument)
                argCnt+=1

            field = argumentsList
            operator = "()"

        else:
            operator = None
            field = None
        
        return Node("postfixExpression",\
                    ["identifier.list","operator.lit","field.node"],\
                    [identifier,operator,field])
            

        
    #   ArgumentExpressionlist ->  Argument
    #                          | Argument, ArgumentList

    # Argument = ConditionalExpression
    
    def parseArgument(self):
        return self.parseConditionalExpression()



