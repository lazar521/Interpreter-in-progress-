from nodeFile import Node

EOF = -1

class Parser:
    keywords = ["struct","for","while","void","int","float","double","if","else","return"]
    

    def parseTokens(self, tokens):
        self.tokens = tokens
        self.tokenPos = 0
        self.lineNumber = 1
        self.checkpoints = []
        self.errors = []
        
        while self.hasTokens() and self.getToken() == "\n":
            self.tokenPos += 1
            self.lineNumber += 1

        return self.parseProgram()


    def errorDiagnostic(self,string):
        error = "Line " + str(self.lineNumber) + ": " + string
        self.errors.insert(0,error)


    def showErrors(self):
        for message in self.errors:
            print(message)


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


    def saveCheckpoint(self):
        self.checkpoints.append(self.tokenPos)

    
    def rollback(self):
        if len(self.checkpoints) == 0:
            print("Parser error: No checkpoints left")
            exit(-1)

        self.tokenPos = self.checkpoints[-1]

    def removeCheckpoint(self):
        self.checkpoints.pop()



    def matchLiteral(self,string):
        token = self.getToken()
        #print(token)
        if token == string:
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


    def parseLiteral(self):              ##### THIS IS NOT A COMPLETE FUNCTION
        token = self.getToken()                     ### it only parses numeric literals
        #print(token)
        if token.isnumeric():
            self.advance()
            return token 
        
        return None

    def parseConstantExpression(self):
        return parseConditionalExpression()





##################  PARSING  ##################


    # Program       -> DeclarationList
    
    def parseProgram(self):
        declarationList = self.parseDeclarationList()
        if declarationList == None:
            self.showErrors()
            return None 

        return Node("Program",\
                    ["declarations"],\
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



    # Declaration    -> VariableDeclaration
    #            | FunctionDeclaration
    #            | StructDeclaration

    def parseDeclaration(self):
        self.saveCheckpoint()
        
        for i in range(0,3):
            if i == 0:
                decl = self.parseVariableDeclaration()
            elif i == 1:
                decl = self.parseFunctionDeclaration()
            elif i == 2:
                decl = self.parseStructDeclaration()
            
            if decl != None:
                break
            self.rollback()

        self.removeCheckpoint()
        return decl




    # VariableDeclaration -> TypeSpecifier Identifier ;
    #                    | TypeSpecifier Identifier [ ConstantExpression ] ;

    def parseVariableDeclaration(self):
        isArray = False
        constantExpression = None
        
        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None

        if self.matchLiteral("["):            
            constantExpression = self.parseConstantExpression()
            if not self.matchLiteral("]"):
                return None
        

        if not self.matchLiteral(";"):
            return None                 

        return Node("VariableDeclaration",\
                    ["type","identifier","isArray","constantExpression"],\
                    [typeSpecifier,identifier,isArray,constantExpression])
        


    # TypeSpecifier -> int
    #           | uint
    #           | char
    #           | struct Identifier
    #           | void


    def parseTypeSpecifier(self):
        isPointer = False
        identifier = None
        dataType = None

        for word in ["int", "char","void","uint","struct"]:
            dataType = word
            if self.matchLiteral(dataType):
                break
        else:
            return None

        if dataType == "struct":
            identifier = self.parseIdentifier()
            if identifier == None:
                return None

        if self.matchLiteral("*"):
            isPointer = True


        return Node("TypeSpecifier",\
            ["type","identifier","isPointer"],\
            [dataType,identifier,isPointer])


    # FunctionDeclaration -> TypeSpecifier Identifier ( ParameterList ) CompoundStatement

    def parseFunctionDeclaration(self):
        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None

        if not self.matchLiteral("("):
            return None
        
        parameterList = self.parseParameterList()    # parameterList is optional so we dont need to check None case

        if not self.matchLiteral(")"):
            return None
        
        statements = self.parseCompountStatement()
        if statements == None:
            return None

        return Node("FunctionDeclaration",\
                    ["typeSpecifier","identifier","parameterList","body"],\
                    [typeSpecifier,identifier,parameterList,statements])


    # ParameterList -> Parameter
    #       | Parameter , ParameterList 
    
    def parseParameterList(self):
        parameters = []
        
        while True:
            param = self.parseParameter()
            if param == None:
                break
            
            parameters.append(param)

            if not self.matchLiteral(","):
                break

        return parameters



    # Parameter     -> TypeSpecifier Identifier
    #       | TypeSpecifier Identifier [ ]
    
    def parseParameter(self):
        isArray = False

        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None
        
        if self.matchLiteral("["):
            if not self.matchLiteral("]"):
                return None
            isArray = True
        
        
        return Node("Parameter",\
                    ["typeSpecifier","identifier","isArray"],\
                    [typeSpecifier,identifier,isArray])


    # StructDeclaration -> struct Identifier { MemberList } ;

    def parseStructDeclaration(self):
        if not self.matchLiteral("struct"):
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            self.errorDiagnostic("Struct declaration: missing struct identifier")
            return None
        
        if not self.matchLiteral("{"):
            self.errorDiagnostic("Struct declaration: missing '}'")
            return None

        memberList = self.parseMemberList()
        if memberList == []:
            self.errorDiagnostic("Struct declaration: missing body")
            return None
        
        if not self.matchLiteral("}"):
            return None

        return Node("structDeclaration",\
                    ["identifier","memberList"],\
                    [identifier,memberList])


    # MemberList    -> Member
    #       | Member MemberList

    def parseMemberList(self):
        memberList = []

        while True:
            member = self.parseMember()
            if member == None:
                break
            memberList.append(member)
        
        return memberList

        

    # Member        -> TypeSpecifier Identifier ;
    #       | TypeSpecifier Identifier [ ConstantExpression ] ;

    def parseMember(self):
        constantExpression = None
        isArray = False

        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None


        if self.matchLiteral("["):
            constantExpression = self.parseConstantExpression()
            if not self.matchLiteral("]"):
                return None
            isArray = True

        if not self.matchLiteral(";"):
            return None

        return Node("member",\
                    ["typeSpecifier","identifier","isArray","constantExpression"],\
                    [typeSpecifier,identifier,isArray,constantExpression])


    # CompoundStatement -> { StatementList }

    def parseCompountStatement(self):
        if not self.matchLiteral("{"):
            return None
        
        statementList = self.parseStatementList()
        if statementList == None:
            return None

        if not self.matchLiteral("}"):
            return None
        
        return statementList


        
    # StatementList -> Statement
    #       | Statement StatementList

    def parseStatementList(self):
        statementList = []

        while True:
            self.saveCheckpoint()
            statement = self.parseStatement()
            if statement == None:
                self.rollback()
                break
            
            self.removeCheckpoint()
            statementList.append(statement)
        
        self.removeCheckpoint()
        return statementList


    # Statement     -> ExpressionStatement
    #       | IfStatement
    #       | WhileStatement
    #       | ForStatement
    #       | ReturnStatement
    #       | VariableDeclaration


    def parseStatement(self):
        self.saveCheckpoint()

        for i in range(0,6):
            if i == 0:
                stmt = self.parseExpressionStatement()
            elif i == 1:
                stmt = self.parseIfStatement()
            elif i == 2:
                stmt = self.parseWhileStatement()
            elif i == 3:
                stmt = self.parseForStatement()
            elif i == 4:
                stmt = self.parseReturnStatement()
            elif i == 5:
                stmt = self.parseVariableDeclaration()
            
            if stmt != None:
                break
            self.rollback()

        self.removeCheckpoint()
        return stmt

        

    # ExpressionStatement -> Expression ;

    def parseExpressionStatement(self):
        expression = self.parseExpression()
        if expression == None:
            return None

        if not self.matchLiteral(";"):
            return None
        
        return expression
        

    # IfStatement   -> if ( Expression ) CompoundStatement
    #               | if ( Expression ) CompoundStatement else CompoundStatement

    def parseIfStatement(self):
        if not self.matchLiteral("if"):
            return None
        
        if not self.matchLiteral("("):
            self.errorDiagnostic("If statement: missing '('")
            return None

        condition = self.parseExpression()
        if condition == None:
            self.errorDiagnostic("If statement: Cannot parse condition expression")
            return None
        
        if not self.matchLiteral(")"):
            self.errorDiagnostic("If statement: missing ')'")
            return None
        
        body = self.parseCompountStatement()
        if body == None:
            self.errorDiagnostic("If statement: missing body")
            return None

        
        elseBody = None
        if self.matchLiteral("else"):
            elseBody = self.parseCompountStatement()
            if elseCompountStatement == None:
                self.errorDiagnostic("If statement: else missing body")
                return None
        

    
        return Node("ifStatement",\
                    ["condition","body","elseBody"],\
                    [condition,body,elseBody])


    # WhileStatement -> while ( Expression ) CompoundStatement

    def parseWhileStatement(self):
        if not self.matchLiteral("while"):
            return None
        
        if not self.matchLiteral("("):
            return None
        
        expression = self.parseExpression()
        if expression == None:
            return None

        if not self.matchLiteral(")"):
            return None
        
        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            return None
        
        return Node("whileStatement",\
                    ["condition","body"],\
                    [expression,compoundStatement])


    # ForStatement   -> for ( ForInitializer ; Expression ; ForUpdater ) CompoundStatement

    def parseForStatement(self):
        if not self.matchLiteral("for"):
            return None

        if not self.matchLiteral("("):
            return None
        
        forInitializer = self.parseForInitializer()
        if forInitializer == None:
            return None
        
        if not self.matchLiteral(";"):
            return None

        expression = self.parseExpression()
        if expression == None:
            return None
        
        if not self.matchLiteral(";"):
            return None

        forUpdater = self.parseForUpdater()
        if forUpdater == None:
            return None

        if not self.matchLiteral(")"):
            return None

        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            return None

        return Node("forStatement",\
                    ["forInitializer","condition","forUpdater","body"],\
                    [forInitializer,expression,forUpdater,compoundStatement])


    # ForInitializer -> Expression
    #       | VariableDeclaration

    def parseForInitializer(self):
        self.saveCheckpoint()

        expression = self.parseExpression()
        if expression != None:
            self.removeCheckpoint()
            return Node("forInitializer",\
                        ["expression"],\
                        [expression])
        
        self.rollback()

        variableDeclaration = self.parseVariableDeclaration()
        if variableDeclaration != None:
            self.removeCheckpoint()
            return Node("forInitializer",\
                        ["variableDeclaration"],\
                        [variableDeclaration])

        self.removeCheckpoint()
        return None

        

    # ForUpdater    -> Expression
    #       | VariableDeclaration

    def parseForUpdater(self):
        self.saveCheckpoint()

        expression = self.parseExpression()
        if expression != None:
            self.removeCheckpoint()
            return Node("forUpdater",\
                        ["expression"],\
                        [expression])
        
        self.rollback()

        variableDeclaration = self.parseVariableDeclaration()
        if variableDeclaration != None:
            self.removeCheckpoint()
            return Node("forUpdater",\
                        ["expression"],\
                        [variableDeclaration])

        self.removeCheckpoint()
        return None



    # ReturnStatement -> return ; 
    # 		| return Expression ;

    def parseReturnStatement(self):
        if not self.matchLiteral("return"):
            return None
        
        if self.matchLiteral(";"):
            return Node("returnStatement",\
                        ["returnValue"],\
                        [None])

        expression = self.parseExpression()
        if expression == None:
            return None

        if not self.matchLiteral(";"):
            return None

        return Node("returnStatement",\
                        ["returnValue"],\
                        [expression])



    # Expression  -> ConditionalExpression
    #       | Identifier = Expression

    def parseExpression(self):
        self.saveCheckpoint()

        identifier = self.parseIdentifier()
        if identifier != None:

            if self.matchLiteral("="):

                expression = self.parseExpression()
                if expression != None:
                    self.removeCheckpoint()
                    return Node("expression",\
                                ["assignment","identifier","body"],\
                                [True,identifier,expression])
                

        self.rollback()

        conditionalExpression = self.parseConditionalExpression()
        if conditionalExpression != None:
            self.removeCheckpoint()
            return Node("expression",\
                        ["assignment","identifier","body"],\
                        [False,None,conditionalExpression])

        self.removeCheckpoint()
        return None



    def parseConditionalExpression(self):
        expr = self.parseLogicalOrExpression()
        if expr == None:
            return None
        
        return Node("conditionalExpression",\
                    ["body"],\
                    [expr])

    # LogicalOrExpression -> LogicalAndExpression
    #            | LogicalAndExpression || LogicalOrExpression

    def parseLogicalOrExpression(self):
        expr1 = self.parseLogicalAndExpression()
        if expr1 == None:
            return None
        
        if self.matchLiteral("||"):
            expr2 = self.parseLogicalOrExpression()
            if expr2 == None:
                return None

            return Node("LogicalOrExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])
        
        return expr1


    # LogicalAndExpression -> EqualityExpression
    #         | EqualityExpression && LogicalAndExpression
    
    def parseLogicalAndExpression(self):
        expr1 = self.parseEqualityExpression()
        if expr1 == None:
            return None
        
        if self.matchLiteral("&&"):
            expr2 = self.parseLogicalAndExpression()
            if expr2 == None:
                return None

            return Node("LogicalAndExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])
            
        return expr1

        
    # EqualityExpression -> RelationalExpression
    #       | RelationalExpression == EqualityExpression
    #       | RelationalExpression != EqualityExpression

    def parseEqualityExpression(self):
        expr1 = self.parseRelationalExpression()
        if expr1 == None:
            None
        
        expr2 = None

        if self.matchLiteral("=="):
            expr2 = self.parseEqualityExpression()
            if expr2 == None:
                return None
            
            return Node("equalityExpression",\
                    ["firstOperand","secondOperand"],\
                    [expr1,expr2])
    
        if self.matchLiteral("!="):
            expr2 = self.parseEqualityExpression()
            if expr2 == None:
                return None
            
            return Node("equalityExpression",\
                    ["firstOperand","secondOperand"],\
                    [expr1,expr2])
    
        return expr1

    
    
    # RelationalExpression -> AdditiveExpression
    #             | AdditiveExpression < RelationalExpression
    #             | AdditiveExpression > RelationalExpression
    #             | AdditiveExpression <= RelationalExpression
    #             | AdditiveExpression >= RelationalExpression
        
    def parseRelationalExpression(self):
        expr1 = self.parseAdditiveExpression()
        if expr1 == None:
            return None

        if self.matchLiteral("<"):
            expr2 = self.parseRelationalExpression()
            if expr2 == None:
                return None
            
            return Node("relationalExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])
        
        if self.matchLiteral(">"):
            expr2 = self.parseRelationalExpression()
            if expr2 == None:
                return None
            
            return Node("relationalExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])
        
        if self.matchLiteral("<="):
            expr2 = self.parseRelationalExpression()
            if expr2 == None:
                return None
            
            return Node("relationalExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])
        
        if self.matchLiteral(">="):
            expr2 = self.parseRelationalExpression()
            if expr2 == None:
                return None
            
            return Node("relationalExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])

        return expr1

    
    # AdditiveExpression -> MultiplicativeExpression
    #           | MultiplicativeExpression + AdditiveExpression
    #           | MultiplicativeExpression - AdditiveExpression

    def parseAdditiveExpression(self):
        expr1 = self.parseMultiplicativeExpression()
        if expr1 == None:
            return None

        if self.matchLiteral("+"):
            expr2 = self.parseAdditiveExpression()
            if expr2 == None:
                return None
            
            return Node("additiveExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])

        if self.matchLiteral("-"):
            expr2 = self.parseAdditiveExpression()
            if expr2 == None:
                return None
            
            return Node("additiveExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])

        return expr1


    # MultiplicativeExpression -> UnaryExpression
    #               | UnaryExpression * MultiplicativeExpression
    #               | UnaryExpression / MultiplicativeExpression
    #               | UnaryExpression % MultiplicativeExpression

    def parseMultiplicativeExpression(self):
        expr1 = self.parseUnaryExpression()
        if expr1 == None:
            return None

        if self.matchLiteral("*"):
            expr2 = self.parseAdditiveExpression()
            if expr2 == None:
                return None
            
            return Node("additiveExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])

        if self.matchLiteral("/"):
            expr2 = self.parseAdditiveExpression()
            if expr2 == None:
                return None
            
            return Node("additiveExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])

        if self.matchLiteral("%"):
            expr2 = self.parseAdditiveExpression()
            if expr2 == None:
                return None
            
            return Node("additiveExpression",\
                        ["firstOperand","secondOperand"],\
                        [expr1,expr2])

        return expr1



    # UnaryExpression -> PostfixExpression
    #        | - UnaryExpression
    #        | ! UnaryExpression

    def parseUnaryExpression(self):
        self.saveCheckpoint()

        expr = self.parsePostfixExpression()
        if expr != None:
            self.removeCheckpoint()
            return expr
        
        self.rollback()
        self.removeCheckpoint()

        if self.matchLiteral("-"):
            expr = self.parseUnaryExpression()
            if expr == None:
                return None

            return Node("unaryExpression",\
                        ["operand"],\
                        [expr])

        if self.matchLiteral("!"):
            expr = self.parseUnaryExpression()
            if expr == None:
                return None
                
            return Node("unaryExpression",\
                        ["operand"],\
                        [expr])

        return None

    

    # PostfixExpression -> numericLiteral
    #          | Identifier [ Expression ]
    #          | Identifier ( ArgumentExpressionList )
    #          | Identifier . Identifier
    #          | Identifier -> Identifier
    #          | Identifier ++
    #          | Identifier --
    #          | Identifier


    def parsePostfixExpression(self):
        literal = self.parseLiteral()
        if literal != None:
            return Node("postfixExpression",\
                        ["identifier","argument"],\
                        [literal,None]) 

        firstIdentifier = self.parseIdentifier()
        if firstIdentifier == None:
            return None


        if self.matchLiteral("["):
            expr = self.parseExpression()
            if expr == None:
                return None
            
            if not self.matchLiteral("]"):
                return None
            
            return Node("postfixExpression",\
                        ["subExpr","argument"],\
                        [firstIdentifier,expr])


        if self.matchLiteral("("):
            args = True #parseArgumentExpressionList()
            if args == None:
                return None
            
            if not self.matchLiteral(")"):
                return None
            
            return Node("postfixExpression",\
                        ["subExpr","argument"],\
                        [firstIdentifier,args])

        
        if self.matchLiteral("."):
            secondIdentifier = self.parseIdentifier()
            if secondIdentifier == None:
                return None
            
            return Node("postfixExpression",\
                        ["subExpr","argument"],\
                        [firstIdentifier,secondIdentifier])

        
        if self.matchLiteral("->"):
            secondIdentifier = self.parseIdentifier()
            if secondIdentifier == None:
                return None

            return Node("postfixExpression",\
                        ["subExpr","argument"],\
                        [firstIdentifier,secondIdentifier])

        
        if self.matchLiteral("++"):
            return Node("postfixExpression",\
                        ["subExpr","argument"],\
                        [firstIdentifier,None])


        if self.matchLiteral("--"):
            return Node("postfixExpression",\
                        ["subExpr","argument"],\
                        [firstIdentifier,None])

        
        return Node("postfixExpression",\
                    ["subExpr","argument"],\
                    [firstIdentifier,None])


  
