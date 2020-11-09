from mako.template import Template
from renderer import template_filename

class ShortAnswer:
    """
    Short-answer question.

    .question shortanswer
        .text Question text
    """

    def __init__(self):
        self.text = None

    def parse(self, parser):
        while True:
            line = parser.next_interesting_line()
            if line is None:
                break
            command, arg = parser.parse_command(line)
            if command == 'question' or command == 'pool':
                parser.putback = line
                break
            elif command == 'text':
                if self.text is None:
                    self.text = arg
                else:
                    parser._raise("More than one 'text' for same question.")
            else:
                parser._raise("Unexpected command.")
        if self.text is None:
            parser._raise("Question without 'text'.")
        return self

    def render(self, counter, idgen, renderer):
        assert self.text is not None, "Short answer question with no question text"
        self.rendered = renderer.render_text(self.text)
        template = Template(filename = template_filename("shortanswer"))
        fragment = template.render(
            question=self,
            title = "Q" + str(counter),
            id = idgen()
        )
        return fragment

    def display(self, fmt):
        return f"""
<h3>Short answer question<h3>
<p>{fmt(self.text)}</p>
"""
