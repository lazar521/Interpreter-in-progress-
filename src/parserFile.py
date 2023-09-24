from nodeFile import Node

EOF = -1

class Parser:
    keywords = ["struct","for","while","void","int","float","double","if","else","return"]
    

    def parseTokens(self, tokens):
        self.tokens = tokens
        self.tokenPos = 0
        self.lineNumber = 1
        self.checkpoints = []
        
        
        while self.hasTokens() and self.getToken() == "\n":
            self.advance()

        return self.parseProgram()



    def hasTokens(self):
        return self.getToken() != EOF


    def advance(self):     
        if self.hasTokens():
            self.tokenPos += 1

            while self.getToken() == "\n":
                self.tokenPos += 1
                self.lineNumber +=1

        else:
            signalError("No more tokens")    


    def getToken(self):
        return self.tokens[self.tokenPos]


    def saveCheckpoint(self):
        self.checkpoints.append(self.tokenPos)

    
    def rollback(self):
        if len(self.checkpoints) == 0:
            self.signalError("No checkpoints left")
        
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
        return self.parseLiteral()


    def signalError(self,string):
        print("Line " + str(self.lineNumber) + " error: " + string)
        exit(-1)



##################  PARSING  ##################


    # Program       -> DeclarationList
    
    def parseProgram(self):
        declarationList = self.parseDeclarationList()
        if declarationList == None:
            print("Cannot parse declaration program")
            exit(-1)

        return Node("Program",\
                    ["body"],\
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

        return Node("DeclarationList",\
                    ["body"],\
                    [declarations])



    # Declaration    -> VariableDeclaration
    #            | FunctionDeclaration
    #            | StructDeclaration

    def parseDeclaration(self):
        self.saveCheckpoint()
        
        declaration = self.parseVariableDeclaration()
        if declaration != None:
            self.removeCheckpoint()
            return Node("VariableDeclaratoin",\
                        ["body"],\
                        [declaration])
        
        self.rollback()

        declaration = self.parseFunctionDeclaration()
        if declaration != None:
            self.removeCheckpoint()
            return Node("FunctionDeclaration",\
                        ["body"],\
                        [declaration])

        self.rollback()
        
        declaration = self.parseStructDeclaration()
        if declaration != None:
            self.removeCheckpoint()
            return Node("StructDeclaration",\
                        ["body"],\
                        [declaration])
        
        self.removeCheckpoint()
        return None




    # VariableDeclaration -> TypeSpecifier Identifier ;
    #                    | TypeSpecifier Identifier [ ConstantExpression ] ;

    def parseVariableDeclaration(self):
        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        

        identifier = self.parseIdentifier()
        if identifier == None:
            return None


        if self.matchLiteral(";"):
            return Node("VariableDeclaration",\
                        ["identifier","array","constantExpression"],\
                        [identifier,False,None])

        if not self.matchLiteral("["):
            return None
        
        constantExpression = self.parseConstantExpression()
        if constantExpression == None:
            return None
        
        if not self.matchLiteral("]"):
            return None
        
        if not self.matchLiteral(";"):
            return None                 

        return Node("VariableDeclaration",\
                    ["identifier","array","constantExpression"],\
                    [identifier,True,None])
        


    # TypeSpecifier -> int
    #           | float
    #           | char
    #           | double
    #           | struct Identifier
        
    def parseTypeSpecifier(self):
        for word in ["int", "float", "char", "double","void"]:
            if self.matchLiteral(word):
                return Node("TypeSpecifier",\
                            ["type","identifier"],\
                            [word,None])

        if not self.matchLiteral("struct"):
            return None

        identifier = self.parseIdentifier()

        if  identifier == None:
            return None

        return Node("TypeSpecifier",\
            ["type","identifier"],\
            ["struct",identifier])


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
        
        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            return None

        return Node("FunctionDeclaration",\
                    ["typeSpecifier","identifier","parameterList",],\
                    [typeSpecifier,identifier,parameterList])


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

        return Node("ParameterList",\
                    ["body"],\
                    [parameters])



    # Parameter     -> TypeSpecifier Identifier
    #       | TypeSpecifier Identifier [ ]
    
    def parseParameter(self):
        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None
        

        if not self.matchLiteral("["):
            return Node("Parameter",\
                        ["typeSpecifier","identifier","array"],\
                        [typeSpecifier,identifier,False])

        if not self.matchLiteral("]"):
            return None
        
        return Node("Parameter",\
                    ["typeSpecifier","identifier","array"],\
                    [typeSpecifier,identifier,True])


    # StructDeclaration -> struct Identifier { MemberList } ;

    def parseStructDeclaration(self):
        if not self.matchLiteral("struct"):
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None
        
        if not self.matchLiteral("{"):
            return None

        memberList = self.parseMemberList()
        if memberList == None:
            return None
        
        if not self.matchLiteral("}"):
            return None

        return Node("structDeclaration",\
                    ["identifier","memberList"],\
                    [identifier,memberList])


    # MemberList    -> Member
    #       | Member MemberList

    def parseMemberList(self):
        members = []

        while True:
            member = self.parseMember()
            if member == None:
                break
            members.append(member)

        if len(members) == 0:
            return None
        
        return Node("MemberList",\
                    ["body"],\
                    [members])

        

    # Member        -> TypeSpecifier Identifier ;
    #       | TypeSpecifier Identifier [ ConstantExpression ] ;

    def parseMember(self):
        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None

        if self.matchLiteral(";"):
            return Node("member",\
                        ["typeSpecifier","identifier","array","constantExpression"],\
                        [typeSpecifier,identifier,False,None])

        if not self.matchLiteral("["):
            return None
        
        constantExpression = self.parseConstantExpression()
        if constantExpression == None:
            return None
        
        if not self.matchLiteral("]"):
            return None

        if not self.matchLiteral(";"):
            return None

        return Node("member",\
                    ["typeSpecifier","identifier","array","constantExpression"],\
                    [typeSpecifier,identifier,True,constantExpression])


    # CompoundStatement -> { StatementList }

    def parseCompountStatement(self):
        if not self.matchLiteral("{"):
            return None
        
        statementList = self.parseStatementList()
        if statementList == None:
            return None

        if not self.matchLiteral("}"):
            return None
        
        return Node("compoundStatement",\
                    ["statementList"],\
                    [statementList])


        
    # StatementList -> Statement
    #       | Statement StatementList

    def parseStatementList(self):
        statements = []

        while True:
            self.saveCheckpoint()
            statement = self.parseStatement()
            if statement == None:
                self.rollback()
                break
            
            self.removeCheckpoint()
            statements.append(statement)
        
        self.removeCheckpoint()
        return Node("StatementList",\
                    ["body"],\
                    [statements])


    # Statement     -> ExpressionStatement
    #       | IfStatement
    #       | WhileStatement
    #       | ForStatement
    #       | ReturnStatement
    #       | VariableDeclaration


    def parseStatement(self):
        self.saveCheckpoint()

        stmt = self.parseExpressionStatement()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.rollback()

        stmt = self.parseIfStatement()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.rollback()

        stmt = self.parseWhileStatement()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.rollback()

        stmt = self.parseForStatement()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.rollback()

        stmt = self.parseReturnStatement()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.rollback()

        stmt = self.parseVariableDeclaration()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.rollback()

        stmt = self.parseDeclaration()
        if stmt != None:
            self.removeCheckpoint()
            return Node("Statement",\
                        ["body"],\
                        [stmt])

        self.removeCheckpoint()
        return None

        

    # ExpressionStatement -> Expression ;

    def parseExpressionStatement(self):
        expression = self.parseExpression()
        if expression == None:
            return None

        if not self.matchLiteral(";"):
            return None
        
        return Node("Expression",\
                    ["body"],\
                    [expression])
        

    # IfStatement   -> if ( Expression ) CompoundStatement
    #               | if ( Expression ) CompoundStatement else CompoundStatement

    def parseIfStatement(self):
        if not self.matchLiteral("if"):
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

        if not self.matchLiteral("else"):
            return Node("ifStatement",\
                        ["condition","body","elseBody"],\
                        [expression,compoundStatement,None])

        elseCompountStatement = self.parseCompountStatement()
        if elseCompountStatement == None:
            return None
    
        return Node("ifStatement",\
                    ["condition","body","elseBody"],\
                    [expression,compoundStatement,elseCompountStatement])


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
            args = None #parseArgumentExpressionList()
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


  
