from mako.template import Template
import uuid
from renderer import template_filename
import question
import re
import html

class JumbledOption:
    def __init__(self, text):
        self.text = text
        self.id = uuid.uuid4().hex

class Jumbled(question.Question):
    """
    self.options holds a list of (text, hex) options.
    self.mapping holds a map tag => index
    """
    def __init__(self, confopts = {'partial': 'false'}):
        super().__init__(confopts)
        self.options = []
        self.partial = 'false'
        self.counter = 0
        self.mapping = {}
        self.subtype = "jumbled sentence"
        
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

        return self

    def tagger(self):
        """
        Return a closure that, on each call, gets the next tag in the sequence
        a, b, ..., z, aa, ab, ... zz

        Calling with parameter 'True' returns the current counter value.
        """
        c = 0
        def closure(peek = None):
            nonlocal c
            if peek: return c
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            l = len(alphabet)
            r = c % l
            q = int((c-r)/l)
            if q == 0:
                tag = alphabet[r:r+1]
            else:
                tag = alphabet[q-1:q] + alphabet[r:r+1]
            c += 1
            return tag
        return closure

    def replace(self, text):
        """
        Replace {i} placeholders with [a], [b], ...
        Return the replaced text and the number of tags found.
        """
        expr = r'[{]([0-9]+)[}]'
        counter = 0
        mapping = {}
        tags = self.tagger()
        while (m := re.search(expr, text)):
            ii = m.group(1)
            i = int(ii)
            if i <= 0 or i > len(self.options): 
                raise Exception(
                    f"In {self.subtype} text question starting at line {self.startline}: " +
                    "Invalid format specifier in question text: must be " +
                    f"{i} where i is an integer between 1 and the number of options. " +
                    f"I got: '{ii}' (parsed as integer: {i})" +
                    f"Text is: \n{text}\n"
                )
            tag = tags()
            self.mapping[tag] = i
            text = re.sub(expr, f"[{tag}]", text, 1)
        return text, tags(True)


    def render(self, qn, idgen, renderer):
        template = Template(filename = template_filename("jumbled"))
        text = renderer.render_text(self.text)
        self.rendered, self.counter = self.replace(text)
        return template.render(
            question = self,
            id = idgen(),
            title = qn
        )

    def display(self, fmt, subtype = "Jumbled sentence"):
        t = Template(filename = template_filename("html_jumbled"))
        text = fmt(self.text)
        text, c2 = self.replace(text)
        assert c2 == self.counter, "Tag mismatch between HTML and BB versions."
        self.htmltext = text      
        return t.render(question = self, fmt = fmt, subtype = subtype)
