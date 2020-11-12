# Bristol Blackboard Quiz Maker

This is a fork of [toastedcrumpets/BlackboardQuizMaker](https://github.com/toastedcrumpets/BlackboardQuizMaker). The project, like the original, is released under the MIT licence.

This project lets you write your blackboard quizzes in a text-based format instead of using the clunky user interface in blackboard. You can compile quiz files to ZIP packages that you can upload to blackboard, as well as create HTML overview files that you can use for example to show to your external examiner or other quality control people. The main features are:

  * A text-based format for quizzes.
  * Write your questions in markdown for emphasis, lists, paragraphs etc.
  * Embed Tex formulas in your quizzes that are rendered as PNG images.
  * Rendered images are cached across runs to speed up the common use case where you repeatedly proofread, edit and recompile your quiz.

## Dependencies

This project is written in python and currently requires the following packages, besides system packages. You should be able to install all of them with `pip install PACKAGENAME`, even on Windows.

  * `mistletoe`, a markdown parser
  * `mako`, a template engine
  * `Pillow`, the python image library

TeX must also be installed to run the program, with both `latex` and `dvipng` on the `PATH`.

Unlike the toastedcrumpets version, this program does not need the sympy/numpy python stack installed, which means it is easier to set up with vanilla python on Windows.

## Usage

This project reads a source file in a text-based format and produces a ZIP file of questions that can be uploaded to blackboard. To run it, run 

    python src/main.py SOURCEFILE

This creates both a ZIP file, which you can upload to blackboard, and a HTML file with an overview of your questions. The names of the output files are taken from the `.filename` command in your source file, which also functions as the blackboard package name.

## File format

Source files are in a text-based format. Each line must be exactly one of:

  * A comment, starting with the `#` character (comments last until the end of line).
  * Empty (that is, containing only whitespace), which are ignored.
  * A command (see below).
  * Part of a here-document.

Command lines are in the format `.COMMAND [ARGUMENT]`, where the optional argument either runs until the end of line, for example

    .text What is the capital of Switzerland?
    
or you can use a here-document to have an argument that spans multiple lines:

    .text <<END
    Consider the following cities:
      1. Zurich
      2. Bern
      3. Basel 
    END

The starting indicator for a here-document is `<<` followed by a word following variable-naming conventions, with no space before the word and no further text on the same line. A here-document ends on a line containing the same word and nothing else except whitespace (so you can indent the end marker). You can reuse the same word for multiple here-documents in the same file, for example use `END` for all of them except of course if you want the string END inside one of your questions.

Where a command takes a free-text argument, it is generally parsed as markdown (including the option to just write HTML directly).

A non-empty line outside of a here-document must be either a comment or a command; you cannot put a comment on the end of a command as the `#` would be interpreted as part of the command's argument. You can indent commands and comments: outside of a here-document, the first non-whitespace character (`.` or `#`) determines which kind of line it is. Any other starting character is an error.

## Commands

The first command in a source file must be `.filename NAME` where `NAME` follows variable naming conventions (alphanumeric and underscores). This is used both for the name of the ZIP file to output and for the name of the package object that will be created in blackboard.

A package contains pools, and pools contain questions. You start a new pool with `.pool NAME` where the name can be anything that is safe to use in a HTML/XML tag value (e.g. spaces are ok, but double quotes are not). So the general format of the file is:

    .filename MyQuestions

    .pool Mock Exam
      .question mcq
        # mock question 1 details
      .question mcq
        # mock question 2 details
        # ...

    .pool Real Exam
      .question mcq
        # real question 1 details
        # ...
    
The argument to a `.question` command is the question type. If you give a question with no type, then `mcq` is assumed.

Parsing of a question ends when another `.question` or `.pool` is encountered, or at the end of the file.

## Question types

### Multiple choice (mcq)

    .question mcq
      .text What is the capital of Switzerland?
      .option Zurich
      .answer Bern
      .option Geneva

Multiple choice questions have exactly one right answer. They take a mandatory `.text` with the question stem, then a list of options where incorrect options are given with `.option` and the correct one with `.answer`. The stem and the options (both correct and incorrect) are parsed as markdown, and you can use here-documents to make them span more than one line.

It is an error to have a number of `.answer` commands for a question other than one. Blackboard seems to support multiple choice questions with up to 100 options (including the correct one).

You can use markdown and Tex in both the text and the option/answer commands' arguments.

### Multiple answer (maq)

    .question maq
        .text Which of the following are in Switzerland?
        .option Paris
        .answer Geneva
        .answer Lausanne
        .option Nancy

A multiple answer question is syntactically exactly like a multiple choice question, except that there can be any number of correct answers including zero. Students must select all that apply and blackboard's automarker will give full marks if all choices are correct (the student has selected all of the correct options and none of the incorrect ones) and no marks otherwise.

It should be possible to implement more complex scoring rules as blackboard's internal XML format uses tags with arbitrary and/or/not combinations, but this is not implemented in this tool yet.

### Short answer

```
.question shortanswer
    .text What is the capital of Switzerland?
```

A short-answer question simply contains a text (that can include markdown/HTML/Tex) and displays a rich-text box for students to answer. It cannot be automatically marked, but you can mark it manually in the blackboard grade centre.

### Numeric

   .question numeric
       .text What is the square root of 2?
       .answer 1.414 delta 0.01

A numeric question requires a 'text' and an 'answer' command, in that order. The text can be markdown/HTML/Tex as for other question types. The answer is either a number (in which case the student must give that exact answer to get points) or "NUMBER delta NUMBER" to specify a range, for example "1.414 delta 0.01" accepts answers in the range from 1.404 to 1.424.

Numbers can be:
  - An integer, with an optional leading minus sign.
  - A floating point value, with an optional leading minus sign, where at least one digit before the decimal point is required (so 0.2 is ok but .2 is not).

Exponential notation (1.0e2) is currently not supported.

## Markdown, HTML and Tex

In most places where a command's argument is text that will end up being displayed in blackboard, you can use markdown as understood by the [mistletoe](https://github.com/miyuchina/mistletoe) parser - it complies with the CommonMark standard so anything defined in that standard should work. You can also include raw HTML, as long as blackboard is happy with it.

Note that markdown's indentation rules apply, for example anything indented four or more spaces is generally a code block. For example:

```
.question mcq
    # This will not do what you want, as the indentation creates a code block:
    .text <<END
    What is the **capital** of Switzerland?
    END

.question mcq
    # This is the correct way to do it, even though it spoils indentation
    # of the source file. Indentation of the END marker does not matter
    # as markdown never sees it.
    .text <<END
What is the **capital** of Switzerland?
    END    
```

On top of this, I have implemented inline Tex by defining a new span token `$...$` with similar parsing behaviour to the backtick, except that the contents are rendered by calling Tex to produce a PNG image and then embedding this in the ZIP file. The contents of the tag are interpreted in Tex' math mode, not paragraph mode.

The way the Tex token is implemented means that you are subject to the markdown parser's rules for span tokens, for example this works to create an unordered list whose elements are Tex formulas:

```
.question mcq
.text <<END
Consider the following polynomials:
  * $(x-1)(x-2)$
  * $(x-1)(x-3)$
END
```

But this does not, because markdown inline tags are not recognised in lines starting with raw HTML tags:

```
# Do not do this, it doesn't work
.question mcq
.text <<END
Consider the following polynomials:
<ul>
  <li>$(x-1)(x-2)$</li>
  <li>$(x-1)(x-3)$</li>
</ul>
END
```

Your Tex code can span several lines, but not markdown paragraphs - in other words, you cannot have empty lines inside your Tex code. For example:

```
.question mcq
# this works
.text <<END
Consider the formula
$
\left(
  \sum_{i=0}^N i
\right)
=
\frac{N(N+1)}{2}
$
END
```

This puts the formula inline in the rendered output, so you get "Consider the formula ..." all on one line. If you want the formula to stand on its own, include an empty line _before_ the first `$` sign. This causes a paragraph break in markdown (same rule as in Tex' paragraph mode), and as long as there are no empty lines between the opening and closing `$` sign, the formula will become a paragraph of its own in the output.