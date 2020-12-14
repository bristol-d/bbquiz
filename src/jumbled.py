from mako.template import Template
import uuid
from renderer import template_filename
import question
import re

class JumbledOption:
    def __init__(self, text):
        self.text = text
        self.id = uuid.uuid4().hex

class Jumbled(question.Question):
    """
    self.options holds a list of (text, hex) options.
    self.mapping holds a map tag => index
    """
    def __init__(self):
        super().__init__(confopts = {'partial': 'false'})
        self.options = []
        self.partial = 'false'
        self.counter = 0
        self.mapping = {}
        
    def parse2(self, parser, command, arg):
        if command == 'text':
            self.text = arg
        else:
            parser._raise("Expecting .text")
        
        while True:
            line = parser.next_interesting_line()
            if line is None:
                if len(self.options) < 2:
                    parser._raise("A jumbled sentence question needs at least 2 options.")
                else:
                    break
            command, arg = parser.parse_command(line)
            if command == 'option':
                self.options.append(JumbledOption(arg))
            elif command == 'question' or command == 'pool':
                parser.putback = line
                break
        if 'partial' in self.config:
            p = self.config['partial']
            if p in ['true', 'false']:
                self.partial = p
            else:
                parser._raise(f"Illegal value for 'partial', use 'true' or 'false' (question starting at line {self.startline})")

        # parse the text and replace {i} identifiers
        # doing this here so we can throw a parser exception with a line number if needed
        text = self.text
        expr = r'[{]([0-9]+)[}]'
        while (m := re.search(expr, text)):
            i = m.group(1)
            try:
                i = int(i)
                if i <= 0 or i > len(self.options): raise ValueError()
            except ValueError:
                parser._raise(
                    f"In jumbled text question starting at line {self.startline}: " +
                    "Invalid format specifier in question text: must be " +
                    "{i} where i is an integer between 1 and the number of options."
                )
            tag = self.next_tag()
            self.mapping[tag] = i
            text = re.sub(expr, f"[{tag}]", text, 1)
        self.text2 = text

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

    def render(self, qn, idgen, renderer):
        template = Template(filename = template_filename("jumbled"))
        self.rendered = renderer.render_text(self.text2)
        return template.render(
            question = self,
            id = idgen(),
            title = qn
        )

    def display(self, fmt):
        t = Template(filename = template_filename("html_jumbled"))
        return t.render(question = self, fmt = fmt)


        




