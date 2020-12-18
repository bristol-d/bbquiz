from mako.template import Template
import uuid
from renderer import template_filename
import question
from xmlgen import node as XML

class MaqOption:
    def __init__(self, text, correct):
        self.text = text
        self.correct = correct
        self.uuid = uuid.uuid4().hex
        self.rendered = None
        self.points = None

class Maq(question.Question):
    """
    Multiple answer question.
    The difference to multiple choice is that you select all that apply.

<<<<<<< HEAD
    Partial scoring lets you implement marks per option, either as 
    'partial = N' (N marks per option)
    or 'partial = 1,1,2, ...' with a comma-separated list of values that represent the marks per
    option. In this case the length of the list must match the number of options.
    """

    def __init__(self):
        super().__init__(confopts = {'partial': 'false'})
=======
    Partial scoring lets you implement marks per option, currently limited to at most 5 options though
    as the encoding of the scoring rule is exponential in the size of the number of options.
    The argument is either a single number (same number of points per option)
    or a comma-separated list of numbers (for each option).
    """

    def __init__(self):
        super().__init__(confopts = {'partial': '1'})
>>>>>>> 93a945e675fa9f3c5cb61199d6c2e0e73e2fb9f4
        self.options = []
        self.text = None

    def parse2(self, parser, command, arg):
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

    def render(self, qn, idgen, renderer):
        assert len(self.options) > 0, "MAQ with no answers"
        template = Template(filename = template_filename("maq"))
        self.rendered = renderer.render_text(self.text)
        for option in self.options:
            option.rendered = renderer.render_text(option.text)
        if 'partial' not in self.config or self.config['partial'] == 'false':
            self.scoring = self.render_standard_scoring()
        else:
            partial = self.config['partial']
            if re.match(partial, '[0-9]+'):
                points = int(partial)
                if points == 0:
                    raise Exception(f"Invalid number of points for partial marks in question starting at line {self.startline}, must be a positive integer.")
                # same marks per question
                for option in self.options:
                    option.points = points
                self.scoring = self.render_partial_scoring()

        fragment = template.render(
            question = self,
            title = qn,
            id = idgen()
        )
        return fragment

    def _write_indented(self, indent, lines):
        b = []
        for (num, line) in enumerate(lines):
            if num > 0: b.append(" " * indent)
            b.append(line)
            if num < len(lines) - 1: b.append("\n")
        return "".join(b)

    def render_partial_scoring(self):
        if len(self.options) > 5:
            raise Exception(f"Partial scoring is currently only available for max 5 options per question, in question starting at line {self.startline}")
        conditions = []
        # TODO

    def render_standard_scoring(self):
        conditions = []
        for option in self.options:
            if option.correct == True:
                conditions.append(f'<varequal respident="response" case="No">{option.uuid}</varequal>')
            else:
                conditions.append("<not>")
                conditions.append(f'    <varequal respident="response" case="No">{option.uuid}</varequal>')
                conditions.append("</not>")
        conditions = self._write_indented(32, conditions)
        return self.score_block(conditions, "SCORE.max")

    def score_block(self, conditions, points, refid = "correct"):
        return f"""<respcondition title="correct">
                        <conditionvar>
                            <and>
                                {conditions}
                            </and>
                        </conditionvar>
                        <setvar variablename="SCORE" action="Set">{points}</setvar>
                        <displayfeedback linkrefid="{refid}" feedbacktype="Response"/>
                    </respcondition>"""

    def display(self, fmt):
        t = Template(filename = template_filename("html_maq"))
        return t.render(question = self, fmt = fmt)