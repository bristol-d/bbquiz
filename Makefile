
.PHONY: install clean extra-clean

PYTHON3=python3.8
PIP=$(PYTHON3) -m pip

SHELL=bash

env:
	$(PYTHON3) -m venv env
	. activate && $(PIP) install --upgrade pip wheel virtualenv pip-tools

install:
	. activate && $(PIP) install --force-reinstall -e .

toplevel = find . -maxdepth 1 -mindepth 1 | grep -v -E 'env|\.git'

clean:
	-rm -rf build $$(find $$( $(toplevel) ) -name __pycache__ -o -name .mypy_cache)

extra-clean: clean
	-rm -rf *.egg-info

#extra-extra-clean: extra-clean
#	-rm -rf ./env


