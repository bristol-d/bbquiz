import subprocess
import os
import pathlib

class Tex:
    """
    Functions for running Tex.
    This class is based off sympy/printing/preview.py which is BSD licenced.
    """

    def __init__(self, exe = 'latex', preamble = None):
        self.exe = exe
        self.preamble(preamble)
        self.ending()
        pass

    def preamble(self, p = None):
        if p is None:
            self.pre = r'''\documentclass[varwidth]{standalone}
            \usepackage{amsmath}
            \usepackage{amsfonts}
            \begin{document}'''
        else:
            self.pre = p

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

    def run(self, source, hash, cwd = __file__):
        temp_dir = pathlib.Path(cwd).parent.parent.joinpath('tmp').absolute()
        if not temp_dir.exists():
            temp_dir.mkdir()
        filename = hash + ".tex"
        with open(temp_dir.joinpath(filename), 'w') as file:
            file.write(self.pre)
            file.write(source)
            file.write(self._ending)
        print(f"Tex running {hash}")
        self._run([self.exe,
            '-halt-on-error',
            '-interaction=nonstopmode',
            filename
            ], temp_dir)
        # and convert to png
        self._run(["dvipng", hash + ".dvi"], temp_dir)
