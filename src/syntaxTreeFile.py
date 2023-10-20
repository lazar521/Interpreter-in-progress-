from nodeFile import Node


class SyntaxTree:
    def __init__(self,root):
        self.root = root
        self.depth = 0


    def traverseTree(self):
        self.traverseNode(self.root)

    def traverseNode(self,curr):
        if curr.getType() == "binaryExpression":
            print("   "*self.depth + curr.getValue("operator.lit"))
        else:
            print("   "*self.depth + curr.getType())

        for attr in curr.getAttributes():
            if ".node" in attr:
                nextNode = curr.getValue(attr)
                if nextNode != None:
                    self.depth += 1
                    self.traverseNode(nextNode)
                    self.depth -= 1

            elif ".list" in attr:
                nodeList = curr.getValue(attr)
                if nodeList != None:
                    for elem in curr.getValue(attr):
                        self.depth += 1
                        self.traverseNode(elem)
                        self.depth -= 1