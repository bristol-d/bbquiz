
import os.path
import sys

from setuptools import find_packages, setup

def get_version():
  """Get version."""

  sys.path.append("src/bbquiz")
  import _version # type: ignore
  return _version.__version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# list of setup args:
# see <https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#setup-py>

if __name__ == '__main__':
  setup(
    version         =get_version(),
    name            ='bbquiz',
    url             ='https://github.com/arranstewart/bbquiz',
    description     ='Make blackboard quizzes from text+markdown',
    packages        =find_packages(where='src'),
    package_dir     ={'': 'src'},
    python_requires = '>=3.7',
    install_requires=('mistletoe',
                      'mako',
                      'Pillow',
    ),
    author='Arran D. Stewart',
    author_email='arran.stewart@uwa.edu.au',
    license         ='MIT',
    license_files   =('LICENCE',),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers     =[
        "Development Status :: 3 - Alpha",
    ],
    include_package_data=True,
    entry_points={
          'console_scripts': [
                # thin wrapper around bbquiz.main
                'bbquiz = bbquiz.main:main'
           ] },

  )

