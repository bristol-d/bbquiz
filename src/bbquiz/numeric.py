from mako.template import Template
import uuid
from .renderer import template_filename
import re
import bbquiz.question as question

class Numeric(question.Question):
    def __init__(self):
        super().__init__()
        self.range = None

    def parse2(self, parser, cmd, arg):
        """
        Format is text, answer
        answer format is N [delta D]
        """
        if cmd != 'text':
            parser._raise("Expecting 'text'.")
        self.text = arg
        answerline = parser.expect('answer')
        match = re.match(r'([-]?\d+([.]\d+)?)( +delta +(\d+([.]\d+)?))?', answerline)
        answer = match.group(1)
        if "." in answer:
            self.answer = float(answer)
        else:
            self.answer = int(answer)
        delta = match.group(4)
        if delta is None:
            self.min = self.answer
            self.max = self.answer
        else:
            self.min = self.answer - float(delta)
            self.max = self.answer + float(delta)
        self.uuid = uuid.uuid4().hex

        return self


    def render(self, qn, idgen, renderer):
        template = Template(filename = template_filename("numeric"))
        self.note = renderer.render_text_html(self.note)
        self.rendered = renderer.render_text(self.text)
        return template.render(question = self, id = idgen(), title = qn)


    def display(self, fmt):
        """
        Return a view of this question for the HTML output.
        """

        if self.min != self.answer:
            d = f" Answers in the range [{self.min}, {self.max}] are accepted."
        else:
            d = ""

        t = f"""
<h3 class="doc">Numeric question ({self.config['points']} points)</h3>
<div class="stem">{fmt(self.text)}</div>
<p class="solution">The correct answer is {self.answer}. {d}</p>
<div class="note">{self.note}</div>
"""
        return t
