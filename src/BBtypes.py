# Types for the different kinds of objects we handle.

class Package:
    def __init__(self):
        self.name = "BBQuestions"
        self.pools = []
        self.htmlcontent = ""
<<<<<<< HEAD
        self.config = {}
=======
        self.preamble = None
>>>>>>> soo-dev

class Pool:
    def __init__(self, name):
        self.name = name
        self.questions = []
        self.instructions = ''
