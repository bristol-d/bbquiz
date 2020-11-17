# Adding a question type

_This documentation is for developers, not users of the software._

  1. Create a new class for the question type
  2. Implement `render(self, counter, idgen, renderer)` to return the XML for this question where
    - counter is a global counter for the question number
    - idgen is a globally-unique blackboard id generator
    - renderer lets you call back to `renderer.render_text` for markdown/Tex
  3. Implement `parse(self, parser)` to handle parsing the source file
    - parser is the main parser instance, e.g. `parser.next_interesting_line()` grabs a non-empty line and `parser.parse_command(line)` grabs a command. This method should `return self`.
  4. implement `display(self, fmt)` where `fmt` is the formatter for markdown/Tex in an HTML context. The question header should be a `<h3 class="doc">` and the stem should be wrapped in a `<div class="stem">` to allow styling of the html. Don't forget to include the points `question.config['points']` in the heading, and the note `<div class="note">` at the end.
  5. In `questions.py`, add the class to `QUESTION_TYPES`.

`from renderer import template_filename` lets you use mako templates with
```
template = Template(filename = template_filename("NAME"))
template.render(...)
```
