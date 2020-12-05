# Types for the different kinds of objects we handle.

class Package:
    def __init__(self):
        self.name = "BBQuestions"
        self.pools = []
        self.htmlcontent = ""
        self.preamble = ""

class Pool:
    def __init__(self, name):
        self.name = name
        self.questions = []
