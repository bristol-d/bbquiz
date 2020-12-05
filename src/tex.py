import subprocess
import os
import pathlib
import hashlib
import shutil

class Tex:
    """
    Functions for running Tex.
    This class is based off sympy/printing/preview.py which is BSD licenced.
    """

    def __init__(self, exe = 'latex', preamble = None, cwd = None, renderer = None):
        self.exe = exe
        self.renderer = renderer
        if cwd is None:
            self.cwd = pathlib.Path(__file__).parent.parent.joinpath('tmp').absolute()
        else:
            self.cwd = pathlib.Path(cwd).absolute()
        if not self.cwd.exists():
            self.cwd.mkdir()
        self.preamble(preamble)
        self.ending()
        pass

    def preamble(self, p = None):
        if p is None:
            self.pre = r'''\documentclass[varwidth]{standalone}
\usepackage{amsmath}
\usepackage{amsfonts}
\begin{document}
'''
        else:
            documentclass = r"\documentclass[varwidth]{standalone}"
            begin = r"\begin{document}"
            self.pre = '\n'.join([documentclass, p, begin]) + '\n' #Add a '\n' at the end so that the actual TeX content starts on a new line

    def ending(self, e = None):
        if e is None:
            self._ending = r'\end{document}'
        else:
            self._ending = e

    def _run(self, cmdlist, dir):
        """
        Run a command in a specified directory.
        """
        if os.name == 'nt':
            creation_flag = 0x08000000 # CREATE_NO_WINDOW, avoids a CMD window popping up
        else:
            creation_flag = 0
        try:
            subprocess.check_output(cmdlist,
                cwd = dir,
                stderr = subprocess.STDOUT,
                creationflags = creation_flag
            )
        except subprocess.CalledProcessError:
            raise Exception(f"Failed to run subprocess {cmdlist[0]}. Check that it is on the PATH.")

    def run(self, source, hash, prepost = True):
        filename = hash + ".tex"
        with open(self.cwd.joinpath(filename), 'wb') as file:
            if prepost: file.write(self.pre)
            file.write(source)
            if prepost: file.write(self._ending)
        print(f"Tex running {hash}")
        self._run([self.exe,
            '-halt-on-error',
            '-interaction=nonstopmode',
            filename
            ], self.cwd)
        # and convert to png
        self._run(["dvipng", hash + ".dvi", "-o", hash + ".png"], self.cwd)

    def render(self, source, displaymath = False):
        """
        Render a formula (optionally as display math) and return the hash
        of the created output.
        """
        if displaymath:
            input = self.pre + "\\begin{align*}\n" + source + "\\end{align*}\n" + self._ending
        else:
            input = self.pre + "$" + source + "$\n" + self._ending
        input = bytes(input, 'utf-8')
        hash = hashlib.sha256(input).hexdigest()
        output = pathlib.Path(self.cwd).joinpath(hash + ".png")
        if not output.exists():
            self.run(input, hash, prepost = False)
        localfolder = pathlib.Path(self.renderer.package.name + "_files")
        if not localfolder.exists():
            localfolder.mkdir()
        filename = hash + ".png"
        targetfile = localfolder.joinpath(filename)
        if not targetfile.exists():
            shutil.copy(self.cwd.joinpath(filename), targetfile)
        return hash
