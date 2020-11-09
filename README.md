# Bristol Blackboard Quiz Maker

This is a fork of [toastedcrumpets/BlackboardQuizMaker](https://github.com/toastedcrumpets/BlackboardQuizMaker).

The project, like the original, is released under the MIT licence.

## Dependencies

This project currently requires the following, besides system packages:

  * `mistletoe`, a markdown parser (`pip install mistletoe` should get it)
  * `mako`, a template engine (`pip install mako`)
  * `Pillow`, the python image library (`pip install Pillow`)

Although a copy of the original file is currently around in `BlackboardQuiz.py` which requires sympy and a few other things (and so indirectly the whole NumPy stack), this is not needed for the main program.

TeX must be installed to run the program, with both `latex` and `dvipng` on the `PATH`.

## Usage

This project reads a source file in a text-based format and produces a ZIP file of questions that can be uploaded to blackboard. To run it, run 

    python src/main.py SOURCEFILE

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

Inside the stem and options, you can use inline Tex by using the `$...$` syntax. You need Tex installed and on your `PATH` for this, as this is handled by running the snippet through Tex itself to produce a PNG image, which is then embedded into the ZIP file to upload.
