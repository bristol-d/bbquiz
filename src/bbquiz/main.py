import bbquiz.BBparser as parser
import bbquiz.mcq as mcq
from bbquiz.renderer import Renderer

import sys
import re


def render(package):
    """
    Render a package with our own code.
    """
    Renderer(package).render()

def main():

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} FILENAME")
        print("where FILENAME is a file in the MCQ format")
        exit(1)
    package = None
    try:
        with open(sys.argv[1], "r") as file:
            package = parser.parse(file)
    except FileNotFoundError:
        print(f"File not found: {sys.argv[1]}")
        exit(2)
    except OSError:
        print(f"I/O error on file {sys.argv[1]}")
        exit(3)

    render(package)

if __name__ == "__main__":
  main()

