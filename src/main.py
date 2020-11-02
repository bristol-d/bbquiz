import BBparser as parser
import mcq
from renderer import Renderer

# import BlackboardQuiz
import sys
import re


def render(package):
    """
    Render a package with our own code.
    """
    Renderer(package).render()


def renderBB(package):
    """
    Call BlackboardQuiz to render a package.
    """
    counter = 1
    with BlackboardQuiz.Package(package.name) as pk:
        for pool in package.pools:
            with pk.createPool(pool.name, description = "", instructions = "") as pl:
                for question in pool.questions:
                    question.renderBB(pl, counter)
                    counter += 1


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
#renderBB(package)
