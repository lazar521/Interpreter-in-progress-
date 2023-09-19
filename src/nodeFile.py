class BaseNode:
    def getType(self)->str:
        pass


class StartNode(BaseNode):
    def __init__(self):
        self.body = []


class CompStmtNode(BaseNode):  # compound statement
    def __init__(self):
        pass

    def getType(self):
        return "COMP_STMT"


class IfNode(BaseNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def getType(self):
        return "IF_STMT"


class DeclNode(BaseNode):
    def __init__(self,) 

