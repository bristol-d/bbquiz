import BBparser as parser
import mcq
from renderer import Renderer

import sys
import re

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} FILENAME")
    print("where FILENAME is a file in the MCQ format")
    exit(1)
package = None

if len(sys.argv) == 3:
    poolname = sys.argv[2]
else:
    poolname = None

try:
    with open(sys.argv[1], "r") as file:
        package = parser.parse(file)
except FileNotFoundError:
    print(f"File not found: {sys.argv[1]}")
    exit(2)
except OSError:
    print(f"I/O error on file {sys.argv[1]}")
    exit(3)

Renderer(package).render(poolname)
