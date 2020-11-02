from mako.template import Template
import uuid
from renderer import template_filename

class Mcq:
    def __init__(self):
        self.options = []
        self.index = None
        
    def renderBB(self, pool, counter):
        assert self.index is not None, "MCQ with no correct answer"
        pool.addMCQ('Q' + str(counter), self.stem, answers = [o for o in self.options],
            correct = self.index, positive_feedback = "", negative_feedback = "")

    class OptionRenderData:
        def __init__(self, id, text):
            self.id = id
            self.text = text

    class RenderData:
        def __init__(self, title, id, stem, options, correctid):
            self.title = title
            self.id = id
            self.stem = stem
            self.options = options
            self.correctid = correctid

    def render(self, counter, idgen):
        """
        Render a question 'in house'.
        """
        assert self.index is not None, "MCQ with no correct answer"
        template = Template(filename = template_filename("mcq"))
        correctid = uuid.uuid4().hex
        odata = []
        for (i, option) in enumerate(self.options):
            if i == self.index:
                odata.append(self.OptionRenderData(id = correctid, text = option))
            else:
                odata.append(self.OptionRenderData(id = uuid.uuid4().hex, text = option))
        data = self.RenderData(
            title = "Q" + str(counter), 
            id = idgen(),
            stem = self.stem,
            options = odata,
            correctid = correctid
        )
        return template.render(d=data)

    def parse(self, parser):
        text = None
        answers = []
        correct = None
        index = 0

        # find the text
        startline = parser.N
        line = parser.next_interesting_line()
        if line is None: parser._raise("EOF while looking for a question text for question starting at line " + str(startline))
        command, arg = parser.parse_command(line)
        if command == 'text':
            text = arg
        else:
            parser._raise("First command after 'question' must be 'text'.")
        while True:
            line = parser.next_interesting_line()
            if line is None:
                if len(answers) == 0:
                    parser._raise("Question with no answers starting at line " + str(startline))
                else:
                    break
            command, arg = parser.parse_command(line)
            if command == 'option':
                index += 1
                answers.append(arg)
            elif command == 'answer':
                if correct is None:
                    correct = index
                else:
                    parser._raise("More than one correct answer to question starting at line " + str(startline))
                index += 1
                answers.append(arg)
            elif command == 'question' or command == 'pool':
                parser.putback = line
                break
            else:
                parser._raise("Unexpected command.")

        if correct is None:
            parser._raise("Question with no correct answer starting at line " + str(startline))

        self.stem = text
        self.options = answers
        self.index = correct
        return self