
class Node:
    def __init__(self, nodeType, attributes, values):
        if len(attributes) != len(values):
            print("Attribute list isn't the same length as the value list")
            exit(-1)
            
        self.attributes = attributes
        self.values = values
        self.type = nodeType

    def getAttribute(self, attribute):
        i = 0
        while i < len(self.attributes) and self.attributes[i] != attribute:
            i += 1
        
        if i == len(self.attributes):
            print("Attribute " + attribute + " doesn't exist")
            exit(-1)
        
        return self.values[i]

    def getType(self):
        return self.type



    


        