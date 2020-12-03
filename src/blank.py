from mako.template import Template
import uuid
from renderer import template_filename
import question
import re

class FillInTheBlank(question.Question):
    """
    Fill in the blank question.
    source format uses {} ... {}
    which becomes [a] ... [zz] in the output
    """
    def __init__(self):
        super().__init__()
        self.blanks = []
        self.counter = 0
        self.mapping = {}

    def parse2(self, parser, command, arg):
        """
        One .text with the question text and {} markers,
        one .answer (string) per marker.
        """
        if command == 'text':
            self.text = arg
        else:
            parser._raise("Expecting .text")
        
        while True:
            line = parser.next_interesting_line()
            if line is None:
                if len(self.blanks) < 1:
                    parser._raise(f"Fill in the blank question with no answers starting at line {self.startline}")
                else:
                    break
            command, arg = parser.parse_command(line)
            if command == 'answer':
                self.blanks.append(arg)
            elif command == 'question' or command == 'pool':
                parser.putback = line
                break
        return self

    def next_tag(self):
        """
        Get the next tag in the sequence a, b, ..., z, aa, ab, ... zz
        """
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        l = len(alphabet)
        c = self.counter
        r = c % l
        q = int((c-r)/l)
        if q == 0:
            tag = alphabet[r:r+1]
        else:
            tag = alphabet[q-1:q] + alphabet[r:r+1]
        self.counter += 1
        return tag

    def render(self, counter, idgen, renderer):
        template = Template(filename = template_filename("fillblank"))
        rendered = renderer.render_text(self.text)

        bcounter = 0
        while re.search('[{][}]', rendered):
            tag = self.next_tag()
            if bcounter >= len(self.blanks):
                raise Exception("Fewer answers than {} placeholders in fill-in-the-blank question, starting at line " + str(self.startline))
            answer = self.blanks[bcounter]
            self.mapping[tag] = answer
            bcounter += 1
            rendered = rendered.replace('{}', f"[{tag}]", 1)
        self.rendered = rendered
        if bcounter < len(self.blanks):
            raise Exception("More answers than {} placeholders in fill-in-the-blank question starting at line " + str(self.startline))

        return template.render(
            question = self,
            id = idgen(),
            title = "Q" + str(counter)
        )

    def display(self, fmt):
        t = Template(filename = template_filename("html_blanks"))
        return t.render(question = self, fmt = fmt)