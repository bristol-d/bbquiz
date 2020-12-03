from mako.template import Template
import uuid
from renderer import template_filename
import question

class McqOption:
    def __init__(self, text, correct):
        self.text = text
        self.correct = correct
        self.id = uuid.uuid4().hex

class Mcq(question.Question):
    def __init__(self):
        super().__init__()
        self.options = []
        self.index = None

    def parse2(self, parser, command, arg):
        text = None
        correct = None
        index = 0

        if command == 'text':
            text = arg
        else:
            parser._raise("Expecting 'text'.")
        while True:
            line = parser.next_interesting_line()
            if line is None:
                if len(self.options) == 0:
                    parser._raise("Question with no answers starting at line " + str(self.startline))
                else:
                    break
            command, arg = parser.parse_command(line)
            if command == 'option':
                index += 1
                self.options.append(McqOption(arg, False))
            elif command == 'answer':
                if correct is None:
                    correct = index
                else:
                    parser._raise("More than one correct answer to question starting at line " + str(startline))
                index += 1
                self.options.append(McqOption(arg, True))
                self.correctid = self.options[-1].id
            elif command == 'question' or command == 'pool':
                parser.putback = line
                break
            else:
                parser._raise("Unexpected command.")

        if correct is None:
            parser._raise("Question with no correct answer starting at line " + str(startline))

        self.stem = text
        self.index = correct
        return self

    def render(self, qn, idgen, renderer):
        """
        Render a question 'in house'.
        """
        assert self.index is not None, "MCQ with no correct answer"
        template = Template(filename = template_filename("mcq"))
        self.rendered = renderer.render_text(self.stem)
        for option in self.options:
            option.rendered = renderer.render_text(option.text)
        return template.render(
            question = self,
            id = idgen(),
            title = qn
        )

    def display(self, fmt):
        """
        Return a view of this question for the HTML output.
        """
        t = Template(filename = template_filename("html_mcq"))
        return t.render(question = self, fmt = fmt)