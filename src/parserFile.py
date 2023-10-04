from nodeFile import Node

EOF = -1

ERROR = -2

class Parser:
    keywords = ["struct","for","while","void","int","uint","char","if","else","return"]
    

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
        print("An error has occured")
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


    def parseNumericLiteral(self):             
        token = self.getToken()                     
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



    # Declaration    -> VariableDeclarationStatement
    #            | FunctionDeclaration
    #            | StructDeclaration

    def parseDeclaration(self):
        self.saveCheckpoint()
        
        for i in range(0,3):
            if i == 0:
                decl = self.parseVariableDeclarationStatement()
            elif i == 1:
                decl = self.parseFunctionDeclaration()
            elif i == 2:
                decl = self.parseStructDeclaration()
            
            if decl != None:
                break
            self.rollback()

        self.removeCheckpoint()
        
        if decl == None:
            self.errorDiagnostic("Declaration error: Cannot deduce declaration type")
        return decl



    def parseVariableDeclarationStatement(self):
        declarataion = self.parseVariableDeclaration()
        if declarataion == None:
            return None
        
        if not self.matchLiteral(";"):
            self.errorDiagnostic("Variable declaration: missing ';'")
            return None
        
        return declarataion


    # VariableDeclarationState -> TypeSpecifier Identifier ;
    #                    | TypeSpecifier Identifier [ ConstantExpression ] ;
    #                    | TypeSpecifier Identifier = Expression ;

    def parseVariableDeclaration(self):
        isArray = False
        expression = None
        
        typeSpecifier = self.parseTypeSpecifier()
        if typeSpecifier == None:
            return None
        
        identifier = self.parseIdentifier()
        if identifier == None:
            return None

        if self.matchLiteral("["):  
            expression = self.parseConstantExpression()
            if not self.matchLiteral("]"):
                self.errorDiagnostic("Variable declaration: missing ']'")
                return None

        elif self.matchLiteral("="):
            expression = self.parseExpression()
            if expression == None:
                self.errorDiagnostic("Variable declaration: missing expression after '='")
                return None
               

        return Node("VariableDeclaration",\
                    ["type","identifier","isArray","expression"],\
                    [typeSpecifier,identifier,isArray,expression])
        


    # TypeSpecifier -> int
    #           | uint
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
            self.errorDiagnostic("Type specifier error: invalid struct identifier")
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
            self.errorDiagnostic("Function declaration: missing body")
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
                stmt = self.parseVariableDeclarationStatement()
            
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

        condition = self.parseConditionalExpression()
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
            self.errorDiagnostic("While statement: missing '('")
            return None
        
        condition = self.parseConditionalExpression()
        if condition == None:
            self.errorDiagnostic("While statement: invalid condition")
            return None

        if not self.matchLiteral(")"):
            self.errorDiagnostic("While statement: missing ')'")
            return None
        
        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            self.errorDiagnostic("While statement: missing body")
            return None
        
        return Node("whileStatement",\
                    ["condition","body"],\
                    [condition,compoundStatement])


    # ForStatement   -> for ( <ForInitializer> ; Expression ; ForUpdater ) CompoundStatement

    def parseForStatement(self):
        if not self.matchLiteral("for"):
            return None

        if not self.matchLiteral("("):
            self.errorDiagnostic("For statement: missing '('")
            return None
        
        self.saveCheckpoint()
        forInitializer = self.parseForInitializer()
        if forInitializer == None:
            self.rollback()

        self.removeCheckpoint()

        if not self.matchLiteral(";"):
            self.errorDiagnostic("For statement: missing ';'")
            return None

        expression = self.parseExpression()    
        if expression == None:
            self.errorDiagnostic("For statement: invalid condition")
            return None
        
        if not self.matchLiteral(";"):
            self.errorDiagnostic("For statement: missing ';'")
            return None

        forUpdater = self.parseForUpdater()
        if forUpdater == None:
            self.errorDiagnostic("For statement: invalid ForUpdater expression")
            return None

        if not self.matchLiteral(")"):
            self.errorDiagnostic("For statement: missing '('")
            return None

        compoundStatement = self.parseCompountStatement()
        if compoundStatement == None:
            self.errorDiagnostic("For statement: missing body")
            return None

        return Node("forStatement",\
                    ["forInitializer","condition","forUpdater","body"],\
                    [forInitializer,expression,forUpdater,compoundStatement])


    # ForInitializer -> Expression
    #       | VariableDeclaration

    def parseForInitializer(self):
        self.saveCheckpoint()
        initializer = None

        for i in range(0,2):
            if i == 0:
                initializer = self.parseExpression()
            elif i == 1:
                initializer = self.parseVariableDeclaration()
            
            if initializer != None:
                break
            self.rollback()
        
        self.removeCheckpoint()
        return initializer


        

    # ForUpdater    -> Expression

    def parseForUpdater(self):
        return self.parseExpression()



    # ReturnStatement -> return ; 
    # 		| return Expression ;

    def parseReturnStatement(self):
        if not self.matchLiteral("return"):
            return None
        
        self.saveCheckpoint()
        expr = self.parseExpression()
        if expr == None:
            self.rollback()
        
        self.removeCheckpoint()
        

        if not self.matchLiteral(";"):
            self.errorDiagnostic("Return statement: missing ';'")
            return None

        return Node("returnStatement",\
                        ["returnValue"],\
                        [expr])



    # Expression  -> AssignmentExpression
    #       | ConditionalExpression
    
    def parseExpression(self): 
        self.saveCheckpoint()

        for i in range(0,2):
            if i == 0:
                expr = self.parseAssignmentExpression()
            elif i == 1:
                expr = self.parseConditionalExpression()
            
            if expr != None:
                break
            self.rollback()    
            
        return expr                



    # AssignmentExpression -> Identifier = Expression

    def parseAssignmentExpression(self):
        identifier = self.parseIdentifier()
        if identifier == None:
            return None
        
        if not self.matchLiteral("="):
            return None
        
        expr = self.parseExpression()
        if expr == None:
            return None
        
        return Node("assingmentExpression",\
                    ["identifier","expression"],\
                    [identifier,expr])


    def parseConditionalExpression(self):
        logicalOrExpr = self.parseLogicalOrExpression()
        if logicalOrExpr == None:
            return None
        
        return Node("conditionalExpression",\
                    ["body"],\
                    [logicalOrExpr])

    # LogicalOrExpression -> LogicalAndExpression
    #            | LogicalAndExpression || LogicalOrExpression

    def parseLogicalOrExpression(self):
        logicalAndExpr = self.parseLogicalAndExpression()
        if logicalAndExpr == None:
            return None
        
        if self.matchLiteral("||"):
            operator = "||"
        else:
            return logicalAndExpr


        logicalOrExpr = self.parseLogicalOrExpression()
        if logicalOrExpr == None:
            return None


        return Node("binaryExpression",\
                    ["leftOP","operator","rightOP"],\
                    [logicalAndExpr,operator,logicalOrExpr])
        


    # LogicalAndExpression -> EqualityExpression
    #         | EqualityExpression && LogicalAndExpression
    
    def parseLogicalAndExpression(self):
        equalityExpr = self.parseEqualityExpression()
        if equalityExpr == None:
            return None
        
        operator = None
        if self.matchLiteral("&&"):
            operator == "&&"
        else:
            return equalityExpr


        logicalAndExpr = self.parseLogicalAndExpression()
        if logicalAndExpr == None:
            return None

        return Node("binaryExpression",\
                    ["leftOP","operator","rightOP"],\
                    [equalityExpr,operator,logicalAndExpr])

        
    # EqualityExpression -> RelationalExpression
    #       | RelationalExpression == EqualityExpression
    #       | RelationalExpression != EqualityExpression

    def parseEqualityExpression(self):
        relationalExpr = self.parseRelationalExpression()
        if relationalExpr == None:
            None
        
        if self.matchLiteral("=="):
            operator = "=="
        elif self.matchLiteral("!="):
            operator = "!="
        else:
            return relationalExpr

        equalityExpr = self.parseEqualityExpression()
        if equalityExpr == None:
            return None

        return Node("binaryExpression",\
                    ["leftOP","operator","rightOP"],\
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

        if self.matchLiteral("<"):
            operator = "<"
        elif self.matchLiteral(">"):
            operator = ">"
        elif self.matchLiteral("<="):
            operator = "<="
        elif self.matchLiteral(">="):
            operator = ">="
        else:
            return additiveExpr

        relationalExpr = self.parseRelationalExpression()
        if relationalExpr == None:
            return None

        return Node("binaryExpression",\
                    ["leftOP","operator","rightOP"],\
                    [additiveExpr,operator,relationalExpr])

    
    # AdditiveExpression -> MultiplicativeExpression
    #           | MultiplicativeExpression + AdditiveExpression
    #           | MultiplicativeExpression - AdditiveExpression

    def parseAdditiveExpression(self):
        multiplicativeExpr = self.parseMultiplicativeExpression()
        if multiplicativeExpr == None:
            return None

        if self.matchLiteral("+"):
            operator = "+"
        elif self.matchLiteral("-"):
            operator = "-"
        else:
            return multiplicativeExpr
        
        additiveExpr = self.parseAdditiveExpression()
        if additiveExpr == None:
            return None
        
        return Node("binaryExpression",\
                    ["leftOP","operator","rightOP"],\
                    [multiplicativeExpr,operator,additiveExpr])
        



    # MultiplicativeExpression -> UnaryExpression
    #               | UnaryExpression * MultiplicativeExpression
    #               | UnaryExpression / MultiplicativeExpression
    #               | UnaryExpression % MultiplicativeExpression

    def parseMultiplicativeExpression(self):
        unaryExpr = self.parseUnaryExpression()
        if unaryExpr == None:
            return None

        if self.matchLiteral("*"):
            operator = "*"
        elif self.matchLiteral("/"):
            operator = "/"
        elif self.matchLiteral("%"):
            operator = "%"
        else:
            return unaryExpr
        
        multiplicativeExpr = self.parseMultiplicativeExpression()
        if multiplicativeExpr == None:
            return None
        
        return Node("binaryExpression",\
                    ["leftOP","operator","rightOP"],\
                    [unaryExpr,operator,multiplicativeExpr])



    # UnaryExpression -> ! Term
#                      | & Term
#                      | * Term
#                      | Term

    def parseUnaryExpression(self):
        if self.matchLiteral("-"):
            operator = "-"
        elif self.matchLiteral("!"):
            operator = "!"
        elif self.matchLiteral("&"):
            operator = "&"
        elif self.matchLiteral("*"):
            operator = "*"
        else:
            operator = None
        
        term = self.parseTerm()
        if term == None:
            return None
        
        if operator == None:
            return term

        return Node("unaryExpression",\
                    ["operator","postfixExpression"],\
                    [operator,term])


    #       Term -> EnclosedTerm
    #               | NumericLiteral
    #               | FunctionCall
    #               | PostfixExpression

    def parseTerm(self):
        self.saveCheckpoint()

        for i in range(0,4):
            if i == 0:
                term = self.parseEnclosedTerm()
            elif i == 1:
                term = self.parseNumericLiteral()
            elif i == 2:
                term = self.parseFunctionCall()
            elif i == 3:
                term = self.parsePostfixExpression()

            if term != None:
                break
            self.rollback()
        
        self.removeCheckpoint()

        return term


    #   EnclosedTerm -> ( ConditionalExpression )

    def parseEnclosedTerm(self):
        if not self.matchLiteral("("):
            return None
        
        conditionalExpr= self.parseConditionalExpression()
        if conditionalExpr == None:
            return None
        
        if not self.matchLiteral(")"):
            return None
        
        return conditionalExpr   


    #     PostfixExpression -> DataField
    #                     | DataField ++
    #                     | DataField --

    def parsePostfixExpression(self):
        data = self.parseDataField()
        if data == None:
            return None

        if self.matchLiteral("++"):
            postfix = "++"
        elif self.matchLiteral("--"):
            postfix = "--"
        else:
            return data
        
        return Node("postfixExpression",\
                    ["postfix","data"],\
                    [postfix,data])
        
        

    # DataField -> Identifier 
    #             | Identifier SpecialOperator
    
    def parseDataField(self):
        identifier = self.parseIdentifier()
        if identifier == None:
            return None
        
        specialoperator = self.parseSpecialOperator()

        
        return Node("fieldSpecification",\
                    ["identifier","operator"],\
                    [identifier,specialoperator])
        


    # SpecialOperator   -> [ ConditionalExpression ] 
    #                      | -> Identifier
    #                      | . Identifier

    def parseSpecialOperator(self):
        field = None

        if self.matchLiteral("["):
            field = self.conditionalExpression()
            if field == None:
                return None
            if not self.matchLiteral("]"):
                return None
            operator = "[]"            

        elif self.matchLiteral("->"):
            field = self.parseIdentifier()
            if field == None:
                return None
            operator = "->"
       
        elif self.matchLiteral("."):
            field = self.parseIdentifier()
            if field == None:
                return None
            operator = "."

        else:
            return None
        
        return Node("specialOperator",\
                    ["operator","field"],\
                    [operator,field])
            

        
    #   FunctionCall -> Identifier( ArgumentList)

    def parseFunctionCall(self):
        identifier = self.parseIdentifier()
        if identifier == None:
            return None
        
        if not self.matchLiteral("("):
            return None
        
        argumentList = self.parseArgumentList()

        if not self.matchLiteral(")"):
            return None
        
        return Node("FunctionCall",\
                    ["identifier","argumentList"],\
                    [identifier,argumentList])

    
    #   ArgumentExpressionlist ->  Argument
    #                          | Argument, ArgumentList

    def parseArgumentList(self):
        argumentList = []

        while True:
            argument = self.parseArgument()
            if argument == None:
                break
                
            if not self.matchLiteral(","):
                return None
            
            argumentList.append(argument)
        
        return argumentList


    # Argument = ConditionalExpression
    
    def parseArgument(self):
        return self.parseConditionalExpression()



