

class Token:
    def __init__(self, tokenStr):
        self.value = tokenStr

    def __repr__(self):
        return str(self.value)

    def getValue(self):
        return self.value