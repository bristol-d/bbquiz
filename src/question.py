import re

def validate_points(key, value, err):
    """
    Check that points is an integer > 0.
    """
    try:
        v = int(value)
    except:
        err(f"Option {key} expects an integer value, but cannot convert '{value}' to an integer.")
    if v > 0:
        return v
    else:
        err(f"The value for {key} must be a positive integer.")



class Question:
    """
    Common base class for questions so we can support .note for notes
    and common config options.

    Subclasses must implement parse2, render, display.
    Subclass constructors must call super().__init__().

    If the config option 'points' is not set, it defaults to 10.
    """

    def __init__(self, confopts = None):
        """
        The optional confopts parameter allows you to set more configuration options
        for this particular question type.
        """
        self.config = {}
        self.note = ""
        self.confopts = { 'points': validate_points }
        if confopts is not None:
            for key in confopts:
                self.confopts[key] = confopts[key]

    def parse(self, parser):
        """
        Parse note and config options, then delegate.
        """
        self.startline = parser.N
        while True:
            line = parser.next_interesting_line()
            if line is None:
                parser._raise("EOF immediately after start of new question.")
            command, arg = parser.parse_command(line)
            if command == 'note':
                self.note = arg
            elif command == 'config':
                m = re.match('([a-z0-9A-Z_]+) *= *(.+)', arg)
                if m is None:
                    parser._raise("Unexpected format of config line, was expecting 'key=value'")
                key = m.group(1)
                value = m.group(2)
                if key in self.confopts:
                    typ = self.confopts[key]
                    if callable(typ):
                        value = typ(key, value, parser._raise)
                    self.config[key] = value
                else:
                    parser._raise(f"This question type does not support the {key} configuration option.")
            else:
                parser.putback = line
                break
        if 'points' not in self.config:
            self.config['points'] = 10
        return self.parse2(parser)
