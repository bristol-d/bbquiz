import BBtypes as types
import questions
import re

class Parser:
    def __init__(self, file):
        self.file = file
        # pre-initialised so we can increment on first run
        self.N = 0 # line number
        self.Q = 0 # question number
        # one-line putback
        self.putback = ''
        self.package = types.Package()
        self.has_name = None

    def _raise(self, msg):
        raise Exception("Line " + str(self.N) + ": " + msg)

    def nextline(self):
        if self.putback != '':
            line = self.putback
            self.putback = ''
        else:
            line = self.file.readline()
            self.N += 1
        return line

    def expect(self, command, command_err = None, EOF_err = None, EOF_allowed = False):
        """
        Utility method when the next command must be the one specified in the argument.
        Optionally, EOF can be accepted too.
        Returns argument or, if allowed, None for EOF.
        """
        if command_err is None:
            command_err = f"A '{command}' is required here."
        if EOF_err is None:
            EOF_err = f"End of file but a '{command}' is required here."
        line = self.next_interesting_line()
        if line is None:
            if EOF_allowed:
                return None
            else:
                parser._raise(EOF_err)
        c, arg = self.parse_command(line)
        if c == command:
            return arg
        else:
            parser._raise(command_err)

    def next_interesting_line(self):
        """
        Get the next line that is not empty or a comment. 
        Returns None on EOF, otherwise the line contents.
        """
        while True:
            line = self.nextline()
            if line == '': return None   # EOF, we're done
            line = line.strip()
            if line == '': continue      # skip empty line
            if line[0] == '#': continue # and comments
            return line

    def parse_command(self, line):
        """
        Read a line, expecting it to be a command line.
        return (command, argument) if a command is found,
        otherwise raise an exception.
        In case of a heredoc, argument reads lines from the file to consume it.
        """
        match = re.match('[.]([a-z]+) *(<<[a-zA-Z0-9_]+)?(.*)', line)
        if match is None: self._raise("Non-command line found outside of heredoc.")
        command = match.group(1)
        if match.group(2) is not None:
            # heredoc
            marker = match.group(2)[2:]
            lines = []
            startline = self.N
            while True:
                line = self.nextline()
                if line == '': self._raise("EOF inside heredoc started at line " + str(startline))
                s = line.strip()
                if s == marker:
                    return (command, "\n".join(lines))
                if line[-1] == "\n":
                    line = line[:-1]
                lines.append(line)
        else:
            return (command, match.group(3))

    # this is the main method to call
    def parse(self):
        while True:
            line = self.next_interesting_line()
            if line is None: return self.package
            command, arg = self.parse_command(line)
            if command == 'pool':
                pool = self.parse_pool(arg)
                self.package.pools.append(pool)
            elif command == 'filename':
                if self.has_name is not None:
                    self._raise(f"Filename has already been set on line {self.has_name}")
                else:
                    self.package.name = arg
                    self.has_name = self.N
            elif command == 'html':
                self.package.htmlcontent = arg
            else:
                self._raise("Expected a pool or filename command.")

    def parse_pool(self, name):
        pool = types.Pool(name)
        while True:
            line = self.next_interesting_line()
            if line is None: return pool 
            command, arg = self.parse_command(line)
            if command == 'question':
                self.parse_question(pool, arg)
            elif command == 'pool':
                # put this back rather than recurse, it's cleaner
                # and python isn't guaranteed to do tail recursion
                self.putback = line
                return pool
            else:
                self._raise("Expecting pool or question")

    def parse_question(self, pool, type):
        """
        Parse a question by delegating to the appropriate handler class.
        """

        if type is None or type == "":
            type = "mcq"
        
        if type in questions.QUESTION_TYPES:
            cls = questions.QUESTION_TYPES[type]
        else:
            self._raise(f"Unknown question type: {type}")
        q = cls()
        q.parse(self)
        self.Q += 1
        pool.questions.append(q)

def parse(file):
    return Parser(file).parse()
