from mako.template import Template
import uuid
from renderer import template_filename

class MaqOption:
    def __init__(self, text, correct):
        self.text = text
        self.correct = correct
        self.uuid = uuid.uuid4().hex
        self.rendered = None

class Maq:
    """
    Multiple answer question.
    The difference to multiple choice is that you select all that apply.
    """

    def __init__(self):
        self.options = []
        self.text = None

    def parse(self, parser):
        startline = parser.N
        line = parser.next_interesting_line()
        if line is None: 
            parser._raise("EOF while looking for a question text for question starting at line " + str(startline))
        command, arg = parser.parse_command(line)
        if command == 'text':
            self.text = arg
        else:
            parser._raise("First command after 'question' must be 'text'.")
        while True:
            line = parser.next_interesting_line()
            if line is None:
                if len(self.options) == 0:
                    parser._raise("Question with no answers starting at line " + str(startline))
                else:
                    break
            command, arg = parser.parse_command(line)
            if command == 'option':
                self.options.append(MaqOption(arg, False))
            elif command == 'answer':
                self.options.append(MaqOption(arg, True))
            elif command == 'question' or command == 'pool':
                parser.putback = line
                break
            else:
                parser._raise("Unexpected command.")
        
        if len(self.options) == 0:
            parser._raise("Question with no answers starting at line " + str(startline))

        return self

    def render(self, counter, idgen, renderer):
        assert len(self.options) > 0, "MAQ with no answers"
        template = Template(filename = template_filename("maq"))
        self.rendered = renderer.render_text(self.text)
        for option in self.options:
            option.rendered = renderer.render_text(option.text)
        fragment = template.render(
            question = self,
            title = "Q" + str(counter),
            id = idgen()
        )
        return fragment

    def display(self, fmt):
        t = Template(filename = template_filename("html_maq"))
        return t.render(question = self, fmt = fmt)