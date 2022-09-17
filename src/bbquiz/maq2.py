import bbquiz.jumbled as jumbled
import re

class MultipleAnswerDropdown(jumbled.Jumbled):
    """
    A version of the jumbled sentence (dropdown) question explicitly to
    represent multiple answer questions with proper partial marking options.
    """
    def __init__(self):
        super().__init__(confopts = {'partial': 'false', 'display': 'True'})
        self.subtype = "multiple answer dropdown"

    def display(self, fmt):
        return super().display(fmt, "Multiple answer dropdown")

    def parse2(self, parser, command, arg):
        if command == 'text':
            self.text = arg
        else:
            parser._raise("Expecting .text")
        # no options here, as that's handled implicitly
        if 'partial' in self.config:
            p = self.config['partial']
            if p in ['true', 'false']:
                self.partial = p
            else:
                parser._raise(f"Illegal value for 'partial', use 'true' or 'false' (question starting at line {self.startline})")
        if 'display' in self.config:
            _display = self.config['display']
        else:
            _display = 'True'
        D = [
            ('True', 'False'),
            ('true', 'false'),
            ('Yes', 'No'),
            ('yes', 'no'),
            ('Correct', 'Incorrect'),
            ('correct', 'incorrect')
        ]
        for item in D:
            if _display == item[0]:
                self.options.append(jumbled.JumbledOption(item[0]))
                self.options.append(jumbled.JumbledOption(item[1]))
        if len(self.options) == 0:
            parser._raise(f"Illegal value for 'display' (question starting at line {self.startline})")

        # Now we have to set the text2 correctly
        text = self.text
        expr = r'[{]([0-9]+)[}]'
        while True:
            m = re.search(expr, text)
            if not m:
                break
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

    def textfor(self, num):
        return self.options[num-1].text
