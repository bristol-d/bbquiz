from mako.template import Template
import uuid
from renderer import template_filename
import question
import re

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

    Partial scoring lets you implement marks per option, using
    'partial = N' (N marks per option).
    """

    def __init__(self):
        super().__init__(confopts = {'partial': 'false'})
        self.options = []
        self.text = None
        self.partialcredit = 'false'

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
        conditions = []            
        if 'partial' in self.config:
            self.partialcredit = 'true'
            partial = self.config['partial']
            if re.match('[0-9]+', partial):
                points = int(partial)
                if points == 0:
                    raise Exception(f"Invalid number of points for partial marks in question starting at line {self.startline}, must be a positive integer.")
                # same marks per question
                p = 0
                for option in self.options:
                    option.points = points
                    p += points
                self.points = p
            else:
                raise Exception(f"Invalid number of points for partial marks in question starting at line {self.startline}, must be a positive integer. Got '{partial}'.")
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

    def resp_line(self, option, negate = False, indent = 28):
        line = f'<varequal respident="response" case="No">{option.uuid}</varequal>'
        if negate:
            line = f'<not>\n{" " * (indent + 4)}{line}\n{" " * indent}</not>'
        return line

    def render_partial_scoring(self):
        blocks = []
        self.points = 0
        for option in self.options:
            self.points += option.points
            c = self.resp_line(option, not option.correct)
            blocks.append(self.resp_block(c, option.points, "correct"))
        self.config['points'] = str(self.points)
        return self._write_indented(20, blocks)

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

    def resp_block(self, condition, points, refid = "correct"):
        return f"""<respcondition title="correct">
                        <conditionvar>
                            {condition}
                        </conditionvar>
                        <setvar variablename="SCORE" action="Set">{points}</setvar>
                        <displayfeedback linkrefid="{refid}" feedbacktype="Response"/>
                    </respcondition>"""

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