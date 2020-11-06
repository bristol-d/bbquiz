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
