all: test lint build
.PHONY: all test lint build

clean:
	rm -fr logs.whiteboxtest

test:
	PYTHONPATH=$(PWD)/py python py/strato/whiteboxtest/tests/test.py

build: pyproject.toml *.py
	python -m build .

lint:
	pep8 py --max-line-length=109
