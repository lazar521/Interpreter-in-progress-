class BaseNode:
    def getType(self)->str:
        pass



class StartNode(BaseNode):
    def __init__(self):
        self.body = []

    def getType(self):
        return "PROGRAM"



class IfNode(BaseNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def getType(self):
        return "IF_STMT"
